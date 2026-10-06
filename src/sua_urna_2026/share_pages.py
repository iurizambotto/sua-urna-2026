"""Static share pages per municipality, each with its own Open Graph image.

WhatsApp and social networks never see what comes after '#', so a link to the single page app
always shows the same preview. One small HTML page per municipality carries its own og:image
and then redirects the visitor to the app, keeping the section in the hash and the referral in
the query string.
"""

from __future__ import annotations

import hashlib
import html
import json
import logging
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from sua_urna_2026.models import FLAVIO, LULA, Totals

log = logging.getLogger(__name__)

FONTS = Path(__file__).parent / "fonts"
W, H = 1200, 630
COL = {
    "bg": (11, 11, 11),
    "ink": (246, 246, 246),
    "muted": (179, 179, 179),
    "red": (255, 59, 78),
    "flavio": (246, 246, 246),
    "lula": (255, 59, 78),
    "outros": (90, 90, 90),
}
LOWER = {"de", "da", "do", "das", "dos", "e", "d'"}


def fmt(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def nice_name(name: str) -> str:
    words = []
    for i, w in enumerate(name.lower().split(" ")):
        parts = ["-".join(p.capitalize() for p in w.split("-"))]
        words.append(w if i > 0 and w in LOWER else parts[0])
    return " ".join(words)


def headline(nome: str, t: Totals) -> tuple[str, str]:
    flavio, lula = t.votos.get(FLAVIO, 0), t.votos.get(LULA, 0)
    diff = flavio - lula
    lugar = nice_name(nome)
    if diff > 0:
        precisa = diff // 2 + 1
        k = lula // precisa
        if k >= 1:
            return (
                f"1 em cada {fmt(k)}",
                f"Em {lugar}, se uma em cada {fmt(k)} das {fmt(lula)} pessoas que votaram no Lula "
                f"trouxer uma que votou no Flávio, vira.",
            )
        return (
            f"{fmt(precisa)} pessoas",
            f"Em {lugar}, {fmt(precisa)} pessoas mudando de ideia viram o resultado.",
        )
    if diff < 0:
        return (
            f"Lula na frente por {fmt(-diff)}",
            f"Em {lugar}, Lula venceu o 1º turno. Agora é segurar quem veio e buscar quem faltou: "
            f"{fmt(t.abstencao)} pessoas não foram votar.",
        )
    return ("Empate", f"Em {lugar}, empate no 1º turno. Uma pessoa decide.")


def _font(name: str, size: int, weight: str) -> ImageFont.FreeTypeFont:
    f = ImageFont.truetype(str(FONTS / name), size)
    try:
        f.set_variation_by_name(weight)
    except (OSError, ValueError):
        log.debug("font %s has no variation %s", name, weight)
    return f


def _wrap(
    draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_w: int
) -> list[str]:
    lines, line = [], ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if draw.textlength(trial, font=font) > max_w and line:
            lines.append(line)
            line = word
        else:
            line = trial
    if line:
        lines.append(line)
    return lines


def render_image(path: Path, kicker: str, titulo: str, sub: str, t: Totals) -> None:
    img = Image.new("RGB", (W, H), COL["bg"])
    d = ImageDraw.Draw(img)
    pad = 64
    d.text(
        (pad, 54), kicker.upper(), font=_font("BricolageGrotesque.ttf", 26, "Bold"), fill=COL["red"]
    )
    size = 104 if len(titulo) <= 16 else 78
    d.text(
        (pad - 3, 100),
        titulo,
        font=_font("BricolageGrotesque.ttf", size, "ExtraBold"),
        fill=COL["red"],
    )
    body = _font("PublicSans.ttf", 34, "Regular")
    y = 100 + size + 34
    for line in _wrap(d, sub, body, W - 2 * pad)[:3]:
        d.text((pad, y), line, font=body, fill=COL["ink"])
        y += 46
    # proportional bar: Flavio, Lula, everyone else in the electorate
    flavio, lula = t.votos.get(FLAVIO, 0), t.votos.get(LULA, 0)
    total = max(t.aptos, flavio + lula, 1)
    x, bar_y, bar_w, bar_h = pad, H - 118, W - 2 * pad, 22
    for key, val in (("flavio", flavio), ("lula", lula), ("outros", total - flavio - lula)):
        w = round(bar_w * val / total)
        if w > 0:
            d.rectangle([x, bar_y, x + w - 2, bar_y + bar_h], fill=COL[key])
        x += w
    small = _font("PublicSans.ttf", 24, "Regular")
    d.text(
        (pad, H - 80),
        f"Flávio {fmt(flavio)}   Lula {fmt(lula)}   "
        "Fonte: TSE, 1º turno 2026   Dia 25, das 8h às 17h",
        font=small,
        fill=COL["muted"],
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, "JPEG", quality=78, optimize=True, progressive=True)


PAGE = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:locale" content="pt_BR">
<meta property="og:site_name" content="Sua urna">
<meta property="og:title" content="{og_title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{image}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{image}">
<script>
  (function () {{
    var extra = location.hash ? "/" + location.hash.slice(1) : "";
    location.replace("../../index.html" + location.search + "#{target}" + extra);
  }})();
</script>
</head>
<body style="font-family:system-ui,sans-serif;padding:24px">
<p><a href="../../index.html#{target}">Abrir Sua urna para {nome}</a></p>
</body>
</html>
"""


class SharePages:
    def __init__(self, site: Path, base_url: str, min_aptos_own_image: int = 20_000) -> None:
        self.site = site
        self.base = base_url.rstrip("/")
        self.min_aptos = min_aptos_own_image
        self.manifest_path = site / "og" / ".manifest.json"
        self.manifest: dict[str, str] = {}
        if self.manifest_path.exists():
            self.manifest = json.loads(self.manifest_path.read_text("utf-8"))

    def _image(self, key: str, path: Path, kicker: str, titulo: str, sub: str, t: Totals) -> bool:
        sig = hashlib.sha256(
            json.dumps([kicker, titulo, sub, t.model_dump()], sort_keys=True).encode()
        ).hexdigest()
        if self.manifest.get(key) == sig and path.exists():
            return False
        render_image(path, kicker, titulo, sub, t)
        self.manifest[key] = sig
        return True

    def _state_totals(self, uf: str, municipios: list[dict[str, Any]]) -> Totals:
        own = self.site / "data" / uf / "totais.json"
        if own.exists():
            return Totals(**json.loads(own.read_text("utf-8")))
        acc = {
            "aptos": 0,
            "compareceram": 0,
            "abstencao": 0,
            "brancos": 0,
            "nulos": 0,
            "validos": 0,
        }
        votos: dict[str, int] = {}
        for m in municipios:
            for k in acc:
                acc[k] += m["totais"][k]
            for c, q in m["totais"]["votos"].items():
                votos[c] = votos.get(c, 0) + q
        return Totals(**acc, votos=votos)

    def run(self) -> dict[str, int]:
        stats = {"paginas": 0, "imagens_municipio": 0, "imagens_estado": 0}
        brasil = self.site / "data" / "brasil.json"
        if brasil.exists():
            t = Totals(**json.loads(brasil.read_text("utf-8")))
            titulo, sub = headline("Brasil", t)
            sub = sub.replace("Em Brasil,", "No Brasil,")
            self._image(
                "brasil",
                self.site / "og" / "brasil.jpg",
                "Sua urna  ·  2º turno, 25 de outubro",
                titulo,
                sub,
                t,
            )
        for index in sorted((self.site / "data").glob("*/index.json")):
            data = json.loads(index.read_text("utf-8"))
            uf, uf_nm = data["cd"], data["nm"]
            muns = []
            for m in data["municipios"]:
                f = self.site / "data" / uf / f"{m['cd']}.json"
                if m.get("ok") and f.exists():
                    muns.append(json.loads(f.read_text("utf-8")))
            if not muns:
                continue
            st = self._state_totals(uf, muns)
            st_titulo, st_sub = headline(nice_name(uf_nm), st)
            if self._image(
                uf,
                self.site / "og" / f"{uf}.jpg",
                f"Sua urna  ·  {nice_name(uf_nm)}",
                st_titulo,
                st_sub,
                st,
            ):
                stats["imagens_estado"] += 1
            for m in muns:
                t = Totals(**m["totais"])
                nome = nice_name(m["nm"])
                titulo, sub = headline(m["nm"], t)
                if t.aptos >= self.min_aptos:
                    rel = f"og/{uf}/{m['cd']}.jpg"
                    kicker = f"Sua urna  ·  {nome}, {uf.upper()}"
                    if self._image(f"{uf}/{m['cd']}", self.site / rel, kicker, titulo, sub, t):
                        stats["imagens_municipio"] += 1
                else:
                    rel = f"og/{uf}.jpg"
                page = PAGE.format(
                    title=html.escape(f"Sua urna em {nome}"),
                    og_title=html.escape(f"{titulo}: a sua urna em {nome}"),
                    desc=html.escape(sub),
                    url=f"{self.base}/m/{uf}/{m['cd']}.html",
                    image=f"{self.base}/{rel}",
                    target=f"{uf}/{m['cd']}",
                    nome=html.escape(nome),
                )
                out = self.site / "m" / uf / f"{m['cd']}.html"
                out.parent.mkdir(parents=True, exist_ok=True)
                if not out.exists() or out.read_text("utf-8") != page:
                    out.write_text(page, "utf-8")
                stats["paginas"] += 1
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        self.manifest_path.write_text(json.dumps(self.manifest, sort_keys=True), "utf-8")
        return stats
