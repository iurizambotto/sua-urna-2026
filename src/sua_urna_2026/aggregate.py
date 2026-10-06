"""Parse TSE JSON files and write the static data consumed by the site."""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sua_urna_2026.models import Municipio, SectionResult, Totals, Uf, Zona

log = logging.getLogger(__name__)


def parse_cs_config(data: dict[str, Any]) -> Uf:
    abr = data["abr"][0]
    municipios = [
        Municipio(
            cd=m["cd"],
            nm=m["nm"],
            zonas=[Zona(cd=z["cd"], secoes=[s["ns"] for s in z["sec"]]) for z in m["zon"]],
        )
        for m in abr["mu"]
    ]
    return Uf(cd=abr["cd"].lower(), nm=abr["ds"], municipios=municipios)


def parse_municipio_totals(data: dict[str, Any]) -> Totals:
    """Works for municipality, state and country files, they share one layout."""
    votos: dict[str, int] = {}
    candidatos: dict[str, str] = {}
    for cargo in data.get("carg", []):
        if str(cargo.get("cd")) != "1":
            continue
        for agr in cargo.get("agr", []):
            for par in agr.get("par", []):
                for cand in par.get("cand", []):
                    votos[str(cand["n"])] = int(cand["vap"])
                    candidatos[str(cand["n"])] = cand.get("nmu") or cand.get("nm", "")
    e, v = data["e"], data["v"]
    return Totals(
        aptos=int(e["te"]),
        compareceram=int(e["c"]),
        abstencao=int(e["a"]),
        brancos=int(v["vb"]),
        nulos=int(v["tvn"]),
        validos=int(v["vvc"]),
        votos=votos,
        candidatos=candidatos,
        secoes=int(data.get("s", {}).get("ts", 0) or 0),
    )


class OutputWriter:
    def __init__(self, root: Path) -> None:
        self.root = root

    def _dump(self, path: Path, payload: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), "utf-8")

    def has_municipio(self, uf: Uf, municipio: Municipio) -> bool:
        return (self.root / uf.cd / f"{municipio.cd}.json").exists()

    def write_ufs_index(self, ufs: list[Uf]) -> None:
        """Merge with the index already on disk so single state runs accumulate."""
        path = self.root / "ufs.json"
        known: dict[str, str] = {}
        if path.exists():
            for item in json.loads(path.read_text("utf-8")).get("ufs", []):
                known[item["cd"]] = item["nm"]
        for u in ufs:
            known[u.cd] = u.nm
        self._dump(
            path,
            {
                "generated_at": _now(),
                "ufs": [{"cd": cd, "nm": known[cd]} for cd in sorted(known)],
            },
        )

    def write_totals(self, name: str, totals: Totals) -> None:
        self._dump(self.root / f"{name}.json", totals.model_dump())

    def _n_secoes(self, uf: Uf, m: Municipio, hints: dict[str, int]) -> int | None:
        if m.zonas:
            return sum(len(z.secoes) for z in m.zonas)
        if m.cd in hints:
            return hints[m.cd]
        path = self.root / uf.cd / f"{m.cd}.json"
        if path.exists():
            return sum(int(z["n_secoes"]) for z in json.loads(path.read_text("utf-8"))["zonas"])
        return None

    def write_uf_index(self, uf: Uf, hints: dict[str, int] | None = None) -> None:
        """Lists every municipality; `ok` tells the site which ones already have data."""
        hints = hints or {}
        entries = []
        for m in uf.municipios:
            entry: dict[str, Any] = {"cd": m.cd, "nm": m.nm, "ok": self.has_municipio(uf, m)}
            n = self._n_secoes(uf, m, hints)
            if n is not None:
                entry["n_secoes"] = n
            entries.append(entry)
        self._dump(
            self.root / uf.cd / "index.json",
            {"cd": uf.cd, "nm": uf.nm, "generated_at": _now(), "municipios": entries},
        )

    def reindex(self) -> list[Uf]:
        """Rebuild ufs.json, every state index and progress.json from the files on disk."""
        ufs: list[Uf] = []
        for index in sorted(self.root.glob("*/index.json")):
            data = json.loads(index.read_text("utf-8"))
            hints = {m["cd"]: int(m["n_secoes"]) for m in data["municipios"] if "n_secoes" in m}
            uf = Uf(
                cd=data["cd"],
                nm=data["nm"],
                municipios=[
                    Municipio(cd=m["cd"], nm=m["nm"], zonas=[]) for m in data["municipios"]
                ],
            )
            self.write_uf_index(uf, hints)
            ufs.append(uf)
        self.write_ufs_index(ufs)
        self.write_progress()
        return ufs

    def write_progress(self) -> dict[str, Any]:
        """Per state: municipalities and sections done, read from the indexes on disk."""
        ufs: dict[str, Any] = {}
        for index in sorted(self.root.glob("*/index.json")):
            data = json.loads(index.read_text("utf-8"))
            ms = data["municipios"]
            ok = [m for m in ms if m.get("ok")]
            ufs[data["cd"]] = {
                "nm": data["nm"],
                "municipios_total": len(ms),
                "municipios_ok": len(ok),
                "secoes_total": sum(int(m["n_secoes"]) for m in ms if "n_secoes" in m) or None,
                "secoes_ok": sum(int(m["n_secoes"]) for m in ok if "n_secoes" in m),
                "municipios_ok_nomes": [m["nm"] for m in ok],
            }
        payload = {"generated_at": _now(), "ufs": ufs}
        self._dump(self.root / "progress.json", payload)
        return payload

    def write_rate(self, secoes_por_segundo: float, uf: str) -> None:
        self._dump(
            self.root / "rate.json",
            {"generated_at": _now(), "uf": uf, "secoes_por_segundo": round(secoes_por_segundo, 2)},
        )

    def write_plan(self, order: list[str], ufs: dict[str, dict[str, Any]]) -> None:
        self._dump(self.root / "plan.json", {"generated_at": _now(), "order": order, "ufs": ufs})

    def write_municipio(
        self, uf: Uf, municipio: Municipio, totals: Totals, sections: list[SectionResult]
    ) -> None:
        self._dump(
            self.root / uf.cd / f"{municipio.cd}.json",
            {
                "uf": uf.cd,
                "cd": municipio.cd,
                "nm": municipio.nm,
                "totais": totals.model_dump(),
                "zonas": [{"cd": z.cd, "n_secoes": len(z.secoes)} for z in municipio.zonas],
            },
        )
        by_zone: dict[str, list[SectionResult]] = {}
        for s in sections:
            by_zone.setdefault(s.zona, []).append(s)
        for zona, items in by_zone.items():
            items.sort(key=lambda s: s.secao)
            self._dump(
                self.root / uf.cd / municipio.cd / f"{zona}.json",
                {
                    "uf": uf.cd,
                    "municipio": municipio.cd,
                    "zona": zona,
                    "secoes": [s.model_dump() for s in items],
                },
            )


def _now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")
