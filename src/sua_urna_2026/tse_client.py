"""Polite async client for resultados.tse.jus.br: rate limit, retries, browser UA."""

from __future__ import annotations

import asyncio
import logging
import time
from types import TracebackType
from typing import Any

import httpx

from sua_urna_2026 import tse_urls as urls
from sua_urna_2026.bu_decoder import BuDecoder
from sua_urna_2026.models import SectionResult

log = logging.getLogger(__name__)

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/128.0 Safari/537.36 sua-urna-2026/0.1"
)


class RateLimiter:
    def __init__(self, per_second: float) -> None:
        self._interval = 1.0 / per_second
        self._next = 0.0
        self._lock = asyncio.Lock()

    async def wait(self) -> None:
        async with self._lock:
            now = time.monotonic()
            delay = self._next - now
            if delay > 0:
                await asyncio.sleep(delay)
                now = time.monotonic()
            self._next = max(self._next, now) + self._interval


class TseClient:
    def __init__(
        self,
        rate_per_second: float = 60.0,
        concurrency: int = 32,
        retries: int = 3,
        backoff_seconds: float = 1.0,
        timeout: float = 30.0,
    ) -> None:
        self._limiter = RateLimiter(rate_per_second)
        self._sem = asyncio.Semaphore(concurrency)
        self._retries = retries
        self._backoff = backoff_seconds
        self._http = httpx.AsyncClient(headers={"User-Agent": USER_AGENT}, timeout=timeout)
        self._decoder = BuDecoder()

    async def __aenter__(self) -> TseClient:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self._http.aclose()

    async def _get(self, url: str) -> httpx.Response | None:
        """Return the response, None on 404, raise after exhausting retries."""
        last: Exception | None = None
        for attempt in range(self._retries):
            async with self._sem:
                await self._limiter.wait()
                try:
                    resp = await self._http.get(url)
                except httpx.HTTPError as exc:
                    last = exc
                else:
                    if resp.status_code == 404:
                        return None
                    if resp.status_code < 500:
                        resp.raise_for_status()
                        return resp
                    last = httpx.HTTPStatusError(
                        f"{resp.status_code} on {url}", request=resp.request, response=resp
                    )
            await asyncio.sleep(self._backoff * (2**attempt))
        raise RuntimeError(f"giving up on {url}: {last}")

    async def get_json(self, url: str) -> dict[str, Any] | None:
        resp = await self._get(url)
        return None if resp is None else resp.json()

    async def get_bytes(self, url: str) -> bytes | None:
        resp = await self._get(url)
        return None if resp is None else resp.content

    async def fetch_section(self, uf: str, municipio: str, zona: str, secao: str) -> SectionResult:
        missing = SectionResult.missing(uf, municipio, zona, secao)
        try:
            return await self._fetch_section(uf, municipio, zona, secao, missing)
        except RuntimeError as exc:
            log.error("section %s/%s/%s/%s failed: %s", uf, municipio, zona, secao, exc)
            return missing.model_copy(update={"status": "erro"})

    async def _fetch_section(
        self, uf: str, municipio: str, zona: str, secao: str, missing: SectionResult
    ) -> SectionResult:
        aux = await self.get_json(urls.section_aux_url(uf, municipio, zona, secao))
        if not aux or not aux.get("hashes"):
            return missing
        for entry in aux["hashes"]:
            bu_file = next((a["nm"] for a in entry.get("arq", []) if a.get("tp") == "bu"), None)
            if not bu_file:
                continue
            raw = await self.get_bytes(
                urls.bu_url(uf, municipio, zona, secao, entry["hash"], bu_file)
            )
            if raw is None:
                continue
            try:
                return self._decoder.decode(raw, uf=uf)
            except ValueError:
                log.warning("undecodable bulletin %s/%s/%s/%s", uf, municipio, zona, secao)
                return missing.model_copy(update={"status": "erro"})
        return missing
