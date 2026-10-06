"""Decode a TSE ballot box bulletin (BU) into a SectionResult."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import asn1tools

from sua_urna_2026.models import SectionResult
from sua_urna_2026.tse_urls import ELEICAO_ID, pad4, pad_municipio

log = logging.getLogger(__name__)

SPEC_PATH = Path(__file__).parent / "spec" / "bu.asn1"
ENVELOPE = "EntidadeEnvelopeGenerico"
BULLETIN = "EntidadeBoletimUrna"


class BuDecoder:
    def __init__(self, spec_path: Path = SPEC_PATH) -> None:
        self._codec = asn1tools.compile_files([str(spec_path)], codec="ber")

    def decode(self, raw: bytes, uf: str, eleicao: int = ELEICAO_ID) -> SectionResult:
        try:
            envelope = self._codec.decode(ENVELOPE, raw)
            bulletin = self._codec.decode(BULLETIN, envelope["conteudo"])
        except Exception as exc:  # asn1tools raises several unrelated types
            raise ValueError("payload is not a TSE bulletin") from exc
        ident = bulletin["identificacaoSecao"]
        municipio = pad_municipio(ident["municipioZona"]["municipio"])
        zona = pad4(ident["municipioZona"]["zona"])
        secao = pad4(ident["secao"])
        aptos, compareceram, votos, brancos, nulos = self._presidential(bulletin, eleicao)
        return SectionResult(
            uf=uf.lower(),
            municipio=municipio,
            zona=zona,
            secao=secao,
            local=str(ident.get("local", "")),
            aptos=aptos,
            compareceram=compareceram,
            brancos=brancos,
            nulos=nulos,
            votos=votos,
        )

    @staticmethod
    def _presidential(
        bulletin: dict[str, Any], eleicao: int
    ) -> tuple[int, int, dict[str, int], int, int]:
        for election in bulletin.get("resultadosVotacaoPorEleicao", []):
            if int(election.get("idEleicao", -1)) != eleicao:
                continue
            aptos = int(election.get("qtdEleitoresAptos", 0))
            for result in election.get("resultadosVotacao", []):
                compareceram = int(result.get("qtdComparecimento", 0))
                for cargo in result.get("totaisVotosCargo", []):
                    if not _is_president(cargo.get("codigoCargo")):
                        continue
                    votos: dict[str, int] = {}
                    brancos = nulos = 0
                    for v in cargo.get("votosVotaveis", []):
                        kind = v.get("tipoVoto")
                        qty = int(v.get("quantidadeVotos", 0))
                        if kind == "nominal":
                            code = str(v["identificacaoVotavel"]["codigo"])
                            votos[code] = votos.get(code, 0) + qty
                        elif kind == "branco":
                            brancos += qty
                        elif kind == "nulo":
                            nulos += qty
                    return aptos, compareceram, votos, brancos, nulos
        raise ValueError(f"no presidential result for election {eleicao} in bulletin")


def _is_president(code: Any) -> bool:  # noqa: ANN401 - asn1tools returns a CHOICE tuple
    return isinstance(code, tuple) and len(code) == 2 and code[1] == "presidente"
