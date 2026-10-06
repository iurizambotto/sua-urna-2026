import pytest

from sua_urna_2026.models import SectionResult, swing_needed


def make(**kw) -> SectionResult:
    base = dict(
        uf="ap",
        municipio="06050",
        zona="0002",
        secao="0069",
        local="2313",
        aptos=159,
        compareceram=133,
        brancos=1,
        nulos=2,
        votos={"13": 54, "22": 67, "55": 5, "70": 2, "14": 1, "27": 1},
    )
    base.update(kw)
    return SectionResult(**base)


def test_derived_fields():
    s = make()
    assert s.abstencao == 26
    assert s.validos == 130
    assert s.flavio == 67
    assert s.lula == 54
    assert s.terceira_via == 8
    assert s.soltos == 26 + 3 + 8


@pytest.mark.parametrize(
    ("flavio", "lula", "tie", "win"),
    [
        (67, 54, 7, 7),
        (60, 54, 3, 4),
        (55, 54, 1, 1),
        (54, 54, 0, 1),
        (50, 54, 0, 0),
    ],
)
def test_swing_needed(flavio: int, lula: int, tie: int, win: int):
    assert swing_needed(flavio, lula) == (tie, win)


def test_section_without_bu_has_zero_counts_and_status():
    s = SectionResult.missing(uf="ap", municipio="06050", zona="0002", secao="0070")
    assert s.status == "sem_bu"
    assert s.aptos == 0
    assert s.votos == {}
