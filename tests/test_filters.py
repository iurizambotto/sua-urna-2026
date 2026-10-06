from sua_urna_2026.filters import RMSP, MunicipioFilter, normalize
from sua_urna_2026.models import Municipio


def test_normalize_strips_accents_hyphens_and_case():
    assert normalize("Embu-Guaçu") == "EMBU GUACU"
    assert normalize("  são  PAULO ") == "SAO PAULO"


def test_rmsp_has_39_municipios():
    assert len(RMSP.split(",")) == 39


def test_filter_by_name_and_code():
    f = MunicipioFilter.from_args(codes="06050", names="Santo André")
    assert f.keep(Municipio(cd="06050", nm="MACAPÁ", zonas=[]))
    assert f.keep(Municipio(cd="99999", nm="SANTO ANDRE", zonas=[]))
    assert not f.keep(Municipio(cd="00001", nm="OSASCO", zonas=[]))


def test_inactive_filter_keeps_everything():
    f = MunicipioFilter.from_args(codes=None, names=None)
    assert not f.active
    assert f.keep(Municipio(cd="00001", nm="QUALQUER", zonas=[]))


def test_rmsp_alias_and_unmatched_report():
    f = MunicipioFilter.from_args(codes=None, names="rmsp")
    assert f.keep(Municipio(cd="1", nm="SÃO PAULO", zonas=[]))
    missing = f.unmatched([Municipio(cd="1", nm="SÃO PAULO", zonas=[])])
    assert "GUARULHOS" in missing and "SAO PAULO" not in missing
