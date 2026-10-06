"""CLI: python -m sua_urna_2026 fetch --uf ap [--municipio 06050] [--out site/data]."""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
import time
from pathlib import Path

from sua_urna_2026 import tse_urls as urls
from sua_urna_2026.aggregate import OutputWriter, parse_cs_config, parse_municipio_totals
from sua_urna_2026.filters import MunicipioFilter
from sua_urna_2026.models import Municipio, SectionResult, Uf
from sua_urna_2026.share_pages import SharePages
from sua_urna_2026.tse_client import TseClient

log = logging.getLogger("sua_urna_2026")

ALL_UFS = (
    "ac al am ap ba ce df es go ma mg ms mt pa pb pe pi pr rj rn ro rr rs sc se sp to"
).split()


class Fetcher:
    def __init__(
        self,
        client: TseClient,
        writer: OutputWriter,
        municipio_filter: MunicipioFilter | None = None,
        skip_existing: bool = False,
    ) -> None:
        self.client = client
        self.writer = writer
        self.filter = municipio_filter or MunicipioFilter()
        self.skip_existing = skip_existing
        self._started = time.monotonic()
        self._secoes_done = 0

    async def run_uf(self, uf_cd: str) -> Uf:
        cs = await self.client.get_json(urls.cs_config_url(uf_cd))
        if cs is None:
            raise RuntimeError(f"no config for {uf_cd}")
        uf = parse_cs_config(cs)
        self.writer.write_uf_index(uf)
        self.writer.write_ufs_index([uf])
        uf_totals = await self.client.get_json(urls.uf_url(uf.cd))
        if uf_totals:
            self.writer.write_totals(f"{uf.cd}/totais", parse_municipio_totals(uf_totals))
        for name in sorted(self.filter.unmatched(uf.municipios)):
            log.warning("name filter did not match any municipality in %s: %s", uf.cd, name)
        for municipio in uf.municipios:
            if not self.filter.keep(municipio):
                continue
            if self.skip_existing and self.writer.has_municipio(uf, municipio):
                log.info("skip %s %s (%s): already on disk", uf.cd, municipio.nm, municipio.cd)
                continue
            await self.run_municipio(uf, municipio)
            self.writer.write_uf_index(uf)
            self.writer.write_progress()
            elapsed = time.monotonic() - self._started
            if elapsed > 30 and self._secoes_done:
                self.writer.write_rate(self._secoes_done / elapsed, uf.cd)
        return uf

    async def run_municipio(self, uf: Uf, municipio: Municipio) -> None:
        totals_raw = await self.client.get_json(urls.municipio_url(uf.cd, municipio.cd))
        if totals_raw is None:
            log.warning("no totals for %s/%s", uf.cd, municipio.cd)
            return
        totals = parse_municipio_totals(totals_raw)
        tasks = [
            self.client.fetch_section(uf.cd, municipio.cd, z.cd, s)
            for z in municipio.zonas
            for s in z.secoes
        ]
        sections: list[SectionResult] = list(await asyncio.gather(*tasks))
        ok = sum(1 for s in sections if s.status == "ok")
        checked = sum(s.compareceram for s in sections if s.status == "ok")
        log.info(
            "%s %s (%s): %d/%d sections ok, turnout %d vs TSE %d",
            uf.cd,
            municipio.nm,
            municipio.cd,
            ok,
            len(sections),
            checked,
            totals.compareceram,
        )
        self.writer.write_municipio(uf, municipio, totals, sections)
        self._secoes_done += len(sections)


async def fetch(args: argparse.Namespace) -> None:
    writer = OutputWriter(Path(args.out))
    uf_list = ALL_UFS if args.uf == "all" else [args.uf.lower()]
    async with TseClient(rate_per_second=args.rate, concurrency=args.concurrency) as client:
        brasil = await client.get_json(urls.brasil_url())
        if brasil:
            writer.write_totals("brasil", parse_municipio_totals(brasil))
        fetcher = Fetcher(
            client,
            writer,
            MunicipioFilter.from_args(args.municipios, args.nomes),
            skip_existing=args.skip_existing,
        )
        ufs: list[Uf] = []
        for uf_cd in uf_list:
            ufs.append(await fetcher.run_uf(uf_cd))
        writer.write_ufs_index(ufs)


async def reindex(args: argparse.Namespace) -> None:
    ufs = OutputWriter(Path(args.out)).reindex()
    log.info("reindexed %d states: %s", len(ufs), ", ".join(u.cd for u in ufs))


async def plan(args: argparse.Namespace) -> None:
    """Fetch the section config of each planned state and record totals for the progress page."""
    order = [u.strip().lower() for u in args.ufs.split(",") if u.strip()]
    totals: dict[str, dict[str, object]] = {}
    async with TseClient(rate_per_second=args.rate) as client:
        for uf_cd in order:
            cs = await client.get_json(urls.cs_config_url(uf_cd))
            if cs is None:
                log.warning("no config for %s", uf_cd)
                continue
            uf = parse_cs_config(cs)
            totals[uf.cd] = {
                "nm": uf.nm,
                "municipios": len(uf.municipios),
                "secoes": sum(len(z.secoes) for m in uf.municipios for z in m.zonas),
            }
            log.info(
                "%s: %d municipios, %d secoes",
                uf.cd,
                totals[uf.cd]["municipios"],
                totals[uf.cd]["secoes"],
            )
    OutputWriter(Path(args.out)).write_plan(order, totals)


async def pages(args: argparse.Namespace) -> None:
    site = Path(args.out).parent
    stats = SharePages(site, base_url=args.base_url, min_aptos_own_image=args.min_aptos).run()
    log.info("share pages: %s", stats)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="sua_urna_2026")
    sub = parser.add_subparsers(dest="command", required=True)
    r = sub.add_parser("reindex", help="rebuild ufs.json and state indexes from files on disk")
    r.add_argument("--out", default=os.environ.get("SUA_URNA_DATA_DIR", "site/data"))
    r.set_defaults(func=reindex)
    pl = sub.add_parser("plan", help="record planned states and their section totals")
    pl.add_argument("--ufs", required=True, help="comma separated state codes in collection order")
    pl.add_argument("--out", default=os.environ.get("SUA_URNA_DATA_DIR", "site/data"))
    pl.add_argument("--rate", type=float, default=10.0)
    pl.set_defaults(func=plan)
    pg = sub.add_parser("pages", help="write per-municipality share pages and preview images")
    pg.add_argument("--out", default=os.environ.get("SUA_URNA_DATA_DIR", "site/data"))
    pg.add_argument(
        "--base-url",
        default=os.environ.get("SUA_URNA_BASE_URL", "https://iurizambotto.github.io/sua-urna-2026"),
    )
    pg.add_argument(
        "--min-aptos", type=int, default=20_000, help="own preview image above this size"
    )
    pg.set_defaults(func=pages)
    f = sub.add_parser("fetch", help="download TSE results and write static JSON")
    f.add_argument("--uf", required=True, help="two letter state code or 'all'")
    f.add_argument("--municipios", default=None, help="comma separated municipality codes")
    f.add_argument("--nomes", default=None, help="comma separated municipality names, or 'rmsp'")
    f.add_argument(
        "--skip-existing", action="store_true", help="skip municipalities already written"
    )
    f.add_argument("--out", default=os.environ.get("SUA_URNA_DATA_DIR", "site/data"))
    f.add_argument("--rate", type=float, default=float(os.environ.get("SUA_URNA_RATE_LIMIT", "60")))
    f.add_argument("--concurrency", type=int, default=32)
    f.set_defaults(func=fetch)
    return parser


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)
    args = build_parser().parse_args()
    asyncio.run(args.func(args))


if __name__ == "__main__":
    main()
