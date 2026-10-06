# Sua Urna 2026

## Visão geral
Site estático, de pessoa física, que mostra ao eleitor os números da própria seção eleitoral no primeiro turno de 2026 (aptos, ausentes, brancos, nulos, votos em Cury, Renan e Caiado, diferença entre Flávio Bolsonaro e Lula) e calcula quantas pessoas daquela sala precisam mudar para virar a eleição. Em cima do número, entrega um roteiro de conversa por perfil de eleitor, com fatos verificados e link para a fonte. Público: quem quer convencer duas ou três pessoas conhecidas até 25/10/2026.

## Estrutura
```
sua-urna-2026/
├── README.md
├── AGENTS.md
├── CLAUDE.md
├── TASKS.md
├── docs/
│   ├── research/      dossiê de pesquisa (números, fatos, regras do TSE, canais)
│   ├── specs/         SDD por feature
│   ├── adrs/ rfcs/ decisions/ runbooks/ prompts/
├── logs/activity.md
├── src/sua_urna_2026/ pipeline: baixa config e boletins do TSE, decodifica e gera JSON estático
├── tests/
├── scripts/
├── site/              HTML, CSS, JS e data/ gerados; publicado no Cloudflare Pages
└── pyproject.toml
```

## Como usar
- Pré-requisitos: Python 3.11, `uv`.
- Setup: `cd projects/sua-urna-2026 && uv venv && uv pip install -e ".[dev]"`.
- Pipeline: `python -m sua_urna_2026 fetch --uf ap` gera `site/data/ap/*.json`.
- Site: abrir `site/index.html` com um servidor estático local (`python -m http.server -d site`).
- Lint e testes: `ruff check . && ruff format --check . && pytest`.

## Fonte dos dados
Resultados oficiais do TSE em `resultados.tse.jus.br/oficial` (pleito 3220, eleição 6257). O boletim de urna por seção é decodificado com a especificação ASN.1 pública do TSE.

## Referências
- [[AGENTS - sua-urna-2026]]
- [[TASKS - sua-urna-2026]]
- [[Síntese de pesquisa - Sua Urna 2026]]
