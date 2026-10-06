import json
from pathlib import Path

from sua_urna_2026.aggregate import (
    OutputWriter,
    parse_cs_config,
    parse_municipio_totals,
)
from sua_urna_2026.models import SectionResult, Uf


def test_parse_cs_config_lists_municipios_zonas_secoes(cs_json: dict):
    uf = parse_cs_config(cs_json)
    assert uf.cd == "ap"
    assert uf.nm == "AMAPÁ"
    assert len(uf.municipios) == 16
    macapa = uf.municipios[0]
    assert macapa.cd == "06050"
    assert macapa.nm == "MACAPÁ"
    assert macapa.zonas[0].cd == "0002"
    assert macapa.zonas[0].secoes[0] == "0069"
    assert len(macapa.zonas[0].secoes) == 456


def test_parse_municipio_totals(municipio_json: dict):
    t = parse_municipio_totals(municipio_json)
    assert t.aptos == 321597
    assert t.compareceram == 270534
    assert t.abstencao == 51063
    assert t.brancos == 2792
    assert t.nulos == 4024
    assert t.validos == 263718
    assert t.votos["22"] == 124378
    assert t.votos["13"] == 114179
    assert t.votos["55"] == 5510
    assert t.votos["70"] == 11656
    assert t.votos["14"] == 7001
    assert t.secoes == 1027


def test_writer_produces_municipio_and_zone_files(
    tmp_path: Path, cs_json: dict, municipio_json: dict
):
    uf = parse_cs_config(cs_json)
    macapa = uf.municipios[0]
    totals = parse_municipio_totals(municipio_json)
    sections = [
        SectionResult(
            uf="ap",
            municipio="06050",
            zona="0002",
            secao="0069",
            local="2313",
            aptos=159,
            compareceram=133,
            brancos=1,
            nulos=2,
            votos={"13": 54, "22": 67},
        ),
        SectionResult.missing(uf="ap", municipio="06050", zona="0002", secao="0070"),
    ]
    writer = OutputWriter(tmp_path)
    writer.write_municipio(uf, macapa, totals, sections)

    mun = json.loads((tmp_path / "ap" / "06050.json").read_text(encoding="utf-8"))
    assert mun["nm"] == "MACAPÁ"
    assert mun["totais"]["aptos"] == 321597
    assert mun["zonas"][0] == {"cd": "0002", "n_secoes": 456}

    zone = json.loads((tmp_path / "ap" / "06050" / "0002.json").read_text(encoding="utf-8"))
    assert zone["secoes"][0]["secao"] == "0069"
    assert zone["secoes"][0]["votos"]["22"] == 67
    assert zone["secoes"][0]["abstencao"] == 26
    assert zone["secoes"][1]["status"] == "sem_bu"


def test_writer_index_files(tmp_path: Path, cs_json: dict):
    uf = parse_cs_config(cs_json)
    writer = OutputWriter(tmp_path)
    writer.write_uf_index(uf)
    writer.write_ufs_index([uf])
    idx = json.loads((tmp_path / "ap" / "index.json").read_text(encoding="utf-8"))
    assert idx["municipios"][0] == {"cd": "06050", "nm": "MACAPÁ", "ok": False, "n_secoes": 1045}
    ufs = json.loads((tmp_path / "ufs.json").read_text(encoding="utf-8"))
    assert ufs["ufs"] == [{"cd": "ap", "nm": "AMAPÁ"}]


def test_ufs_index_merges_with_existing_file(tmp_path: Path, cs_json: dict):
    uf = parse_cs_config(cs_json)
    other = Uf(cd="ac", nm="ACRE", municipios=[])
    writer = OutputWriter(tmp_path)
    writer.write_ufs_index([uf])
    writer.write_ufs_index([other])
    ufs = json.loads((tmp_path / "ufs.json").read_text(encoding="utf-8"))
    assert ufs["ufs"] == [{"cd": "ac", "nm": "ACRE"}, {"cd": "ap", "nm": "AMAPÁ"}]


def test_reindex_marks_ready_municipios_and_lists_states(
    tmp_path: Path, cs_json: dict, municipio_json: dict
):
    uf = parse_cs_config(cs_json)
    writer = OutputWriter(tmp_path)
    writer.write_uf_index(uf)
    writer.write_municipio(uf, uf.municipios[0], parse_municipio_totals(municipio_json), [])
    ufs = writer.reindex()
    assert [u.cd for u in ufs] == ["ap"]
    idx = json.loads((tmp_path / "ap" / "index.json").read_text(encoding="utf-8"))
    assert idx["municipios"][0]["ok"] is True
    assert idx["municipios"][1]["ok"] is False
    assert json.loads((tmp_path / "ufs.json").read_text(encoding="utf-8"))["ufs"] == [
        {"cd": "ap", "nm": "AMAPÁ"}
    ]
