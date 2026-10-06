from sua_urna_2026 import tse_urls as u


def test_config_url_for_uf():
    assert u.cs_config_url("ap") == (
        "https://resultados.tse.jus.br/oficial/ele2026/arquivo-urna/3220/config/ap/ap-p003220-cs.json"
    )


def test_municipio_url_pads_codes_and_lowercases_uf():
    assert u.municipio_url("AP", "6050") == (
        "https://resultados.tse.jus.br/oficial/ele2026/6257/dados/ap/ap06050-c0001-e006257-u.json"
    )


def test_section_aux_url():
    assert u.section_aux_url("ap", "06050", "2", "69") == (
        "https://resultados.tse.jus.br/oficial/ele2026/arquivo-urna/3220/dados/ap/06050/0002/0069/"
        "p003220-ap-m06050-z0002-s0069-aux.json"
    )


def test_bu_url_uses_hash_and_filename_from_aux():
    url = u.bu_url("ap", "06050", "0002", "0069", "abc123", "o03220ap0605000020069-bu.dat")
    assert url == (
        "https://resultados.tse.jus.br/oficial/ele2026/arquivo-urna/3220/dados/ap/06050/0002/0069/"
        "abc123/o03220ap0605000020069-bu.dat"
    )


def test_brasil_url():
    assert u.brasil_url() == (
        "https://resultados.tse.jus.br/oficial/ele2026/6257/dados/br/br-c0001-e006257-u.json"
    )
