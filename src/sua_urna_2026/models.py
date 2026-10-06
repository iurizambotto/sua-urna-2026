"""Data contracts shared by the pipeline and the static site."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, computed_field

LULA = "13"
FLAVIO = "22"
TERCEIRA_VIA = ("55", "14", "70")  # Caiado, Renan Santos, Augusto Cury

SectionStatus = Literal["ok", "sem_bu", "erro"]


def swing_needed(flavio: int, lula: int) -> tuple[int, int]:
    """Return (people to tie, people to win) when voters switch from Flavio to Lula.

    Each switch moves two votes, one out and one in.
    """
    diff = flavio - lula
    if diff < 0:
        return 0, 0
    tie = (diff + 1) // 2
    win = diff // 2 + 1
    return tie, win


class SectionResult(BaseModel):
    uf: str
    municipio: str
    zona: str
    secao: str
    local: str = ""
    aptos: int = 0
    compareceram: int = 0
    brancos: int = 0
    nulos: int = 0
    votos: dict[str, int] = Field(default_factory=dict)
    status: SectionStatus = "ok"

    @computed_field
    @property
    def abstencao(self) -> int:
        return max(self.aptos - self.compareceram, 0)

    @computed_field
    @property
    def validos(self) -> int:
        return sum(self.votos.values())

    @property
    def flavio(self) -> int:
        return self.votos.get(FLAVIO, 0)

    @property
    def lula(self) -> int:
        return self.votos.get(LULA, 0)

    @property
    def terceira_via(self) -> int:
        return sum(self.votos.get(n, 0) for n in TERCEIRA_VIA)

    @property
    def soltos(self) -> int:
        """Voters who chose nobody still on the ballot: absent, blank, null, third way."""
        return self.abstencao + self.brancos + self.nulos + self.terceira_via

    @classmethod
    def missing(cls, uf: str, municipio: str, zona: str, secao: str) -> SectionResult:
        return cls(uf=uf, municipio=municipio, zona=zona, secao=secao, status="sem_bu")


class Totals(BaseModel):
    aptos: int
    compareceram: int
    abstencao: int
    brancos: int
    nulos: int
    validos: int
    votos: dict[str, int]
    candidatos: dict[str, str] = Field(default_factory=dict)
    secoes: int = 0


class Zona(BaseModel):
    cd: str
    secoes: list[str]


class Municipio(BaseModel):
    cd: str
    nm: str
    zonas: list[Zona]


class Uf(BaseModel):
    cd: str
    nm: str
    municipios: list[Municipio]
