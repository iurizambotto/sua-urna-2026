import json
from pathlib import Path

from PIL import Image

from sua_urna_2026.models import Totals
from sua_urna_2026.share_pages import SharePages, headline


def totals(flavio: int, lula: int, aptos: int = 100_000) -> Totals:
    return Totals(
        aptos=aptos,
        compareceram=int(aptos * 0.8),
        abstencao=int(aptos * 0.2),
        brancos=1000,
        nulos=1000,
        validos=flavio + lula,
        votos={"22": flavio, "13": lula},
    )


def test_headline_when_flavio_leads_is_per_person():
    titulo, sub = headline("OSASCO", totals(60_000, 50_000))
    assert titulo == "1 em cada 9"
    assert "Osasco" in sub and "50.000" in sub


def test_headline_when_lula_leads():
    titulo, sub = headline("CEARÁ-MIRIM", totals(10_000, 15_000))
    assert titulo == "Lula na frente por 5.000"
    assert "Ceará-Mirim" in sub


def test_headline_when_lula_has_almost_no_votes():
    titulo, _ = headline("X", totals(1_000, 100))
    assert titulo == "451 pessoas"


def test_headline_tie():
    assert headline("X", totals(10, 10))[0] == "Empate"


def write_mun(root: Path, uf: str, cd: str, nm: str, t: Totals, ok: bool = True) -> None:
    (root / "data" / uf).mkdir(parents=True, exist_ok=True)
    (root / "data" / uf / f"{cd}.json").write_text(
        json.dumps({"uf": uf, "cd": cd, "nm": nm, "totais": t.model_dump(), "zonas": []})
    )
    idx = root / "data" / uf / "index.json"
    data = (
        json.loads(idx.read_text())
        if idx.exists()
        else {"cd": uf, "nm": uf.upper(), "municipios": []}
    )
    data["municipios"].append({"cd": cd, "nm": nm, "ok": ok})
    idx.write_text(json.dumps(data))


def test_generator_writes_page_and_images(tmp_path: Path):
    write_mun(tmp_path, "sp", "67890", "OSASCO", totals(60_000, 50_000, aptos=500_000))
    write_mun(tmp_path, "sp", "11111", "PEQUENA", totals(600, 500, aptos=1_000))
    write_mun(tmp_path, "sp", "22222", "SEM DADOS", totals(1, 1), ok=False)
    (tmp_path / "data" / "brasil.json").write_text(
        json.dumps(totals(56_104_503, 53_879_538, 158_745_502).model_dump())
    )
    gen = SharePages(
        tmp_path, base_url="https://exemplo.github.io/sua-urna-2026", min_aptos_own_image=20_000
    )
    stats = gen.run()
    assert stats == {"paginas": 2, "imagens_municipio": 1, "imagens_estado": 1}

    page = (tmp_path / "m" / "sp" / "67890.html").read_text()
    assert (
        'property="og:image" content="https://exemplo.github.io/sua-urna-2026/og/sp/67890.jpg"'
        in page
    )
    assert "1 em cada 9" in page
    assert "location.replace" in page and "#sp/67890" in page
    assert 'name="robots" content="noindex"' in page

    small = (tmp_path / "m" / "sp" / "11111.html").read_text()
    assert "/og/sp.jpg" in small
    assert not (tmp_path / "m" / "sp" / "22222.html").exists()

    img = Image.open(tmp_path / "og" / "sp" / "67890.jpg")
    assert img.size == (1200, 630)
    assert (tmp_path / "og" / "brasil.jpg").exists()


def test_generator_skips_unchanged_images(tmp_path: Path):
    write_mun(tmp_path, "sp", "67890", "OSASCO", totals(60_000, 50_000, aptos=500_000))
    gen = SharePages(tmp_path, base_url="https://x", min_aptos_own_image=20_000)
    gen.run()
    assert gen.run()["imagens_municipio"] == 0
