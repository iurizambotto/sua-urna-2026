"""URL builders for the official TSE results site (verified on 2026-10-06)."""

BASE = "https://resultados.tse.jus.br/oficial"
CICLO = "ele2026"
PLEITO = "3220"
ELEICAO = "6257"
ELEICAO_ID = int(ELEICAO)


def _uf(uf: str) -> str:
    return uf.strip().lower()


def pad_municipio(cd: str | int) -> str:
    return str(int(cd)).zfill(5)


def pad4(cd: str | int) -> str:
    return str(int(cd)).zfill(4)


def cs_config_url(uf: str) -> str:
    uf = _uf(uf)
    return f"{BASE}/{CICLO}/arquivo-urna/{PLEITO}/config/{uf}/{uf}-p00{PLEITO}-cs.json"


def municipio_url(uf: str, municipio: str | int) -> str:
    uf = _uf(uf)
    code = f"{uf}{pad_municipio(municipio)}"
    return f"{BASE}/{CICLO}/{ELEICAO}/dados/{uf}/{code}-c0001-e00{ELEICAO}-u.json"


def uf_url(uf: str) -> str:
    uf = _uf(uf)
    return f"{BASE}/{CICLO}/{ELEICAO}/dados/{uf}/{uf}-c0001-e00{ELEICAO}-u.json"


def brasil_url() -> str:
    return f"{BASE}/{CICLO}/{ELEICAO}/dados/br/br-c0001-e00{ELEICAO}-u.json"


def section_dir(uf: str, municipio: str | int, zona: str | int, secao: str | int) -> str:
    uf = _uf(uf)
    return (
        f"{BASE}/{CICLO}/arquivo-urna/{PLEITO}/dados/{uf}/{pad_municipio(municipio)}/"
        f"{pad4(zona)}/{pad4(secao)}"
    )


def section_aux_url(uf: str, municipio: str | int, zona: str | int, secao: str | int) -> str:
    uf = _uf(uf)
    m, z, s = pad_municipio(municipio), pad4(zona), pad4(secao)
    return f"{section_dir(uf, m, z, s)}/p00{PLEITO}-{uf}-m{m}-z{z}-s{s}-aux.json"


def bu_url(
    uf: str,
    municipio: str | int,
    zona: str | int,
    secao: str | int,
    file_hash: str,
    filename: str,
) -> str:
    return f"{section_dir(uf, municipio, zona, secao)}/{file_hash}/{filename}"
