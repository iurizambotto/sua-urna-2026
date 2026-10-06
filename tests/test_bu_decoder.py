import pytest

from sua_urna_2026.bu_decoder import BuDecoder
from sua_urna_2026.models import SectionResult


@pytest.fixture(scope="module")
def decoder() -> BuDecoder:
    return BuDecoder()


def test_decodes_identification(decoder: BuDecoder, bu_bytes: bytes):
    result = decoder.decode(bu_bytes, uf="ap")
    assert isinstance(result, SectionResult)
    assert result.uf == "ap"
    assert result.municipio == "06050"
    assert result.zona == "0002"
    assert result.secao == "0069"
    assert result.local == "2313"


def test_decodes_presidential_counts_only(decoder: BuDecoder, bu_bytes: bytes):
    result = decoder.decode(bu_bytes, uf="ap")
    assert result.aptos == 159
    assert result.compareceram == 133
    assert result.abstencao == 26
    assert result.brancos == 1
    assert result.nulos == 2
    assert result.votos == {"13": 54, "14": 1, "22": 67, "27": 1, "55": 5, "70": 2}
    assert result.validos == 130
    assert result.status == "ok"


def test_votes_plus_blank_plus_null_equal_turnout(decoder: BuDecoder, bu_bytes: bytes):
    result = decoder.decode(bu_bytes, uf="ap")
    assert sum(result.votos.values()) + result.brancos + result.nulos == result.compareceram


def test_garbage_raises_value_error(decoder: BuDecoder):
    with pytest.raises(ValueError):
        decoder.decode(b"not a boletim", uf="ap")
