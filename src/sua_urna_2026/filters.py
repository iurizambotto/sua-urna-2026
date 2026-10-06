"""Municipality filters by code or by name, accent and case insensitive."""

from __future__ import annotations

import unicodedata

from sua_urna_2026.models import Municipio

RMSP = (
    "Arujá, Barueri, Biritiba-Mirim, Caieiras, Cajamar, Carapicuíba, Cotia, Diadema, "
    "Embu das Artes, Embu-Guaçu, Ferraz de Vasconcelos, Francisco Morato, Franco da Rocha, "
    "Guararema, Guarulhos, Itapecerica da Serra, Itapevi, Itaquaquecetuba, Jandira, Juquitiba, "
    "Mairiporã, Mauá, Mogi das Cruzes, Osasco, Pirapora do Bom Jesus, Poá, Ribeirão Pires, "
    "Rio Grande da Serra, Salesópolis, Santa Isabel, Santana de Parnaíba, Santo André, "
    "São Bernardo do Campo, São Caetano do Sul, São Lourenço da Serra, São Paulo, Suzano, "
    "Taboão da Serra, Vargem Grande Paulista"
)


def normalize(name: str) -> str:
    stripped = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return " ".join(stripped.replace("-", " ").upper().split())


class MunicipioFilter:
    def __init__(self, codes: list[str] | None = None, names: list[str] | None = None) -> None:
        self.codes = {c.strip().zfill(5) for c in codes or [] if c.strip()}
        self.names = {normalize(n) for n in names or [] if n.strip()}

    @classmethod
    def from_args(cls, codes: str | None, names: str | None) -> MunicipioFilter:
        name_list = (
            RMSP.split(",")
            if names and names.strip().lower() == "rmsp"
            else (names or "").split(",")
        )
        return cls(codes=(codes or "").split(","), names=name_list)

    @property
    def active(self) -> bool:
        return bool(self.codes or self.names)

    def keep(self, municipio: Municipio) -> bool:
        if not self.active:
            return True
        return municipio.cd in self.codes or normalize(municipio.nm) in self.names

    def unmatched(self, municipios: list[Municipio]) -> set[str]:
        present = {normalize(m.nm) for m in municipios}
        return self.names - present
