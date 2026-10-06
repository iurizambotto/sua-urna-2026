# AGENTS - sua-urna-2026

## Contexto do projeto

**Objetivo**: site estático de pessoa física que mostra ao eleitor os números da própria seção no primeiro turno de 2026 (aptos, ausentes, brancos, nulos, votos em Cury, Renan e Caiado, diferença Flávio x Lula), calcula quantas pessoas daquela sala precisam mudar para virar a eleição e entrega um roteiro de conversa por perfil de eleitor, com fatos verificados e link para a fonte. Meta: ajudar quem quer convencer duas ou três pessoas conhecidas até o segundo turno de 25/10/2026.

**Domínio**: dados abertos eleitorais (TSE), pipeline Python de extração e decodificação, site estático.

**Status**: em desenvolvimento

**Última atualização deste arquivo**: 2026-10-06

---

## Contexto técnico

### Stack e versões

| Componente | Versão | Observação |
|-----------|--------|-----------|
| Python | 3.11 | `uv venv`, `uv pip install -e ".[dev]"` |
| httpx | última | cliente HTTP assíncrono para o TSE |
| asn1tools | última | decodifica o boletim de urna (BER) |
| pydantic | 2.x | modelos de seção e município |
| ruff, pytest, bandit | última | gate de qualidade |
| Site | HTML, CSS, JS puro | sem framework, sem build; publicado no Cloudflare Pages |

### Estrutura de módulos

```
src/sua_urna_2026/
├── tse_urls.py      # monta as URLs do resultados.tse.jus.br (puro, testável)
├── bu_decoder.py    # bytes do BU -> SectionResult
├── tse_client.py    # download com limite de taxa e retentativa
├── aggregate.py     # SectionResult[] -> JSON por município + índice
├── models.py        # Pydantic: SectionResult, Totals, Uf, Municipio, Zona
├── filters.py       # filtro de município por código ou nome, atalho rmsp
├── spec/bu.asn1     # especificação pública do TSE (via doccaz/urnas-br, MIT)
└── __main__.py      # CLI: fetch --uf <uf>
site/
├── index.html, app.js, style.css
├── kits/            # roteiros de conversa por perfil
└── data/<uf>/<municipio>.json, data/index.json
```

### Endpoints do TSE (verificados em 2026-10-06)

Base `https://resultados.tse.jus.br/oficial`. Pleito `3220`, eleição presidencial 1º turno `6257` (2º turno `6258`). Sem cabeçalho CORS: o navegador não consegue buscar direto, por isso o pipeline pré-computa tudo.

| Arquivo | URL |
|---|---|
| Lista de pleitos | `/comum/config/ele-c.json` |
| Municípios, zonas e seções da UF | `/ele2026/arquivo-urna/3220/config/<uf>/<uf>-p003220-cs.json` |
| Totais do município | `/ele2026/6257/dados/<uf>/<uf><mun>-c0001-e006257-u.json` |
| Índice da seção (hash e arquivos) | `/ele2026/arquivo-urna/3220/dados/<uf>/<mun>/<zona>/<secao>/p003220-<uf>-m<mun>-z<zona>-s<secao>-aux.json` |
| Boletim de urna | `/ele2026/arquivo-urna/3220/dados/<uf>/<mun>/<zona>/<secao>/<hash>/o03220<uf><mun><zona><secao>-bu.dat` |

`mun` tem 5 dígitos, `zona` e `secao` 4 dígitos com zero à esquerda. Enviar `User-Agent` de navegador. Limite de taxa: no máximo 80 requisições por segundo, o TSE bloqueia acima de 100.

### Decodificação do BU

`asn1tools.compile_files(["spec/bu.asn1"], codec="ber")`. Primeiro `EntidadeEnvelopeGenerico`, depois `EntidadeBoletimUrna` sobre `conteudo`. Aptos ficam em `resultadosVotacaoPorEleicao[].qtdEleitoresAptos` (filtrar `idEleicao == 6257`), comparecimento em `resultadosVotacao[].qtdComparecimento`, votos em `totaisVotosCargo[].votosVotaveis[]` com `tipoVoto` em `nominal`, `branco`, `nulo` e `identificacaoVotavel.codigo` igual ao número do candidato.

Números na urna: 13 Lula, 22 Flávio Bolsonaro, 55 Caiado, 14 Renan Santos, 70 Augusto Cury, 30 Zema, 80 Samara, 16 Hertz Dias, 27 Clariana Barão, 21 Edmilson Costa, 35 Wilson Grassi, 29 Rui Costa Pimenta.

### Decisões arquiteturais

| Decisão | Motivo | Data |
|---------|--------|------|
| Pré-computar tudo em JSON estático por município | TSE não envia CORS; site precisa funcionar sem backend e sem depender do TSE no dia | 2026-10-06 |
| Entrada por UF, município, zona e seção, nunca por título de eleitor | título é dado pessoal; a ferramenta não coleta nada | 2026-10-06 |
| Site em nome de pessoa física, fora do CNPJ ME | Lei 9.504 art. 57-C §1º veda propaganda em site de pessoa jurídica | 2026-10-06 |
| Nenhum centavo em impulsionamento | pessoa física não pode impulsionar (art. 57-C), multa de R$ 5 mil a 30 mil | 2026-10-06 |
| Todo fato com link para fonte primária ou checadora; "investigado", nunca "corrupto" | fato sabidamente inverídico ou descontextualizado é ilícito (Res. 23.610 art. 9-A) | 2026-10-06 |
| Sem IA de voz ou rosto; rótulo explícito se IA gerar texto ou imagem; nenhum conteúdo sintético com candidato a partir de 22/10 | Res. 23.610 art. 9-B e 23.755/2026 | 2026-10-06 |
| Vanilla JS, sem framework | 19 dias de prazo; alguém sem Node precisa conseguir editar | 2026-10-06 |
| Paleta vermelho, branco e preto (cores do PT), pedida pelo dono: Lula vermelho `#d7141f` (claro) e `#ff3b4e` (escuro), Flávio preto no tema claro e branco no escuro, demais categorias em cinza com rótulo direto; o acento das ações é o mesmo vermelho | Palavra do dono vence a paleta de referência da skill dataviz; vermelho x preto separa bem inclusive para daltonismo | 2026-10-06 |
| Tipografia: Bricolage Grotesque (títulos e números) e Public Sans (texto), via Google Fonts com fallback de sistema | Evita Inter e similares; Public Sans é face cívica, Bricolage dá personalidade aos números grandes | 2026-10-06 |
| Seletor de tema no topo (`tema.js`): grava `data-theme` e lembra em `localStorage`; sem escolha, segue o sistema | Pedido do dono; o CSS já era por token nos dois temas | 2026-10-06 |
| Esforço sempre expresso por pessoa ("uma em cada N que votaram no Lula trouxer uma pessoa") e nunca só o total de trocas | "30 pessoas mudando de ideia" assusta; a conta por pessoa é a mesma matemática e soa possível (feedback do dono) | 2026-10-06 |
| Roteiros escolhidos por cards de pessoa (`.pessoa`), com ponto na cor do grupo, título escrito como gente e um número de tamanho do grupo; o card prioritário ocupa duas colunas | Pills pareciam filtro de busca; cards de pessoa dizem "quem é a pessoa" e fecham a grade com 7 itens | 2026-10-06 |
| Classes de CSS: botão de tema é `.tema-btn`, nunca `.tema`, que é a etiqueta de tema dos cards de fato | Colisão de nome quebrou as etiquetas em 2026-10-06 | 2026-10-06 |
| Página `progresso.html` lê `plan.json`, `progress.json` e `rate.json`; unidade de progresso é o município | O pipeline grava o município inteiro de uma vez; a estimativa usa a taxa medida na própria coleta (28 a 35 seções/s) | 2026-10-06 |
| Painel "Dá para virar" calcula a urna média a partir de `data/brasil.json`, não de número fixo | Os 318, 112, 108, 19, 12 e 67 do vídeo saem do próprio TSE e ficam auditáveis | 2026-10-06 |
| Teste visual por Playwright headless (venv do zambotto-agent-console), captura em 420 px | Extensão do Chrome não conecta nesta máquina; o hook de Read exige captura reduzida | 2026-10-06 |

### Edge cases e comportamentos especiais

- O BU traz várias eleições (6257 presidente, 6259 estadual): filtrar sempre por `idEleicao`.
- Seção agregadora (`dadosSecaoSA`) pode somar outras seções: registrar o campo e não duplicar aptos.
- `aux.json` pode ter `hashes` vazio ou `st` diferente de `Totalizada` quando a urna foi substituída ou não instalada: registrar como seção sem BU e seguir.
- O JSON de município tem `e.te` (aptos), `e.c` (comparecimento), `e.a` (abstenção), `v.vb` (brancos), `v.tvn` (nulos), `v.vvc` (válidos); os percentuais vêm como string com vírgula.
- `cache-control: max-age=4` no TSE: não há problema em rebaixar, mas o 1º turno já está totalizado, uma rodada basta.
- Seção listada no `cs.json` mas sem `aux.json` (404) é seção agregada: votou na urna de outra seção. O município fecha exato somando só as seções com BU. O BU não diz em qual seção ela foi agregada; o site mostra os totais do município nesse caso. Medido no Amapá em 2026-10-06: 57 de 1.971.
- `dadosSecaoSA` é só horário de abertura e encerramento da seção, não indica agregação.
- Nulos por seção excluem o "nulo técnico" (`vnt` no JSON do município), que o TSE soma à parte em `tvn`. Diferença de 1 a 10 por município, só nos nulos.
- `tipoVoto` tem também `legenda` e `cargoSemCandidato` (proporcionais); o decodificador ignora os dois para presidente.
- Validação por UF: somar aptos, comparecimento, brancos e votos 22 e 13 das seções com `status: ok` e comparar com `totais` do município. No Amapá todos bateram.
- Seletores: estados e municípios em ordem alfabética (`localeCompare` pt-BR), zonas e seções em ordem numérica; municípios sem dados aparecem desabilitados com "(ainda sem dados)".
- Job em segundo plano do Claude Code morre em 2 horas (limite do harness) e pode deixar a coleta pela metade: coleta longa roda por `scripts/run_queue.sh <ufs>` lançado com `setsid nohup`, fora do harness, com registro em `logs/queue.log`; retomar sempre com `--skip-existing`. Ao procurar coletor vivo, usar `ps -eo pid,args | grep -E "python -m sua_urna_2026 fetch"`, nunca `pgrep -f` com o texto do comando, que casa com o próprio shell que espera na fila.
- Prioridade de coleta definida pelo dono em 2026-10-06: Região Metropolitana de SP (`--nomes rmsp`), depois SP, MG, PR e RS (onde o vídeo do Boni localiza 7 em cada 10 votos perdidos), depois SC, RJ, ES, GO, DF, MS e MT. Em 2026-10-06 12:10 o dono pediu os 15 estados restantes (Norte e Nordeste) em paralelo: quatro filas `WAIT=0 RATE=20 CONC=16 LANE=<x> scripts/run_queue.sh`, somando 80 req/s. Coletas em paralelo só com a soma das taxas abaixo de 80 req/s. Gravação de JSON é atômica (arquivo temporário e `os.replace`) desde então. Publicação contínua: `scripts/sync_site.sh` (reindex, commit e push a cada 10 min enquanto houver coleta), executado pelo dono, porque push é dele.

### Variáveis de ambiente

| Variável | Obrigatória | Descrição | Exemplo |
|----------|-------------|-----------|---------|
| `SUA_URNA_RATE_LIMIT` | Não | requisições por segundo, padrão 60 | `60` |
| `SUA_URNA_DATA_DIR` | Não | saída do pipeline, padrão `site/data` | `site/data` |

CLI: `python -m sua_urna_2026 fetch --uf sp --nomes rmsp --rate 75 --concurrency 48 --skip-existing`. `--nomes` aceita lista de nomes separados por vírgula ou o atalho `rmsp` (39 municípios); `--municipios` aceita códigos; `--skip-existing` pula município já escrito, o que permite retomar. `python -m sua_urna_2026 reindex` regrava `ufs.json` e os `index.json` de cada UF a partir do disco, marcando `ok` nos municípios que já têm dados; o site desabilita os demais. Desde 2026-10-06 o estado entra no índice no início da coleta, e o índice da UF é regravado após cada município.

### Erros conhecidos e antipadrões

| Erro | Contexto | Correção aplicada |
|------|----------|-------------------|
| Classe `.tema` usada para o botão de tema e para a etiqueta de tema dos cards | Interface v2 | Botão renomeado para `.tema-btn`; conferir colisão de classe ao criar componente novo |

---

## Padrões obrigatórios

- Python 3.11+ com type hints, `pathlib`, `logging`, Pydantic, `uv`.
- TDD-first. Gate antes de commitar: `pytest`, `ruff check`, `ruff format --check`, `bandit -r src/ -ll`.
- Prosa em português com acentuação; comentário de código em inglês; sem travessão; sem emoji.
- Higiene de material público: nenhum caminho local, nenhum dado pessoal, nenhum número de título.

## Regras de conteúdo (o que o site publica)

1. Fato sem link para fonte não entra.
2. Status obrigatório por fato: comprovado, em disputa, arquivado.
3. Rachadinha: anulada por competência (STJ 2021) e arquivada por falta de justa causa (TJ-RJ 2022). Não é absolvição de mérito nem condenação.
4. Dark Horse e Banco Master: "investigado no STF", com a versão de Flávio ("patrocínio privado para filme privado").
5. Vice Alfredo Gaspar: só com duas fontes grandes e a negativa dele junto.
6. Nada novo publicado em 25/10.

## Leitura obrigatória ao iniciar sessão

- Este arquivo, `TASKS.md`, `logs/activity.md`.
- `docs/research/00-sintese.md` para a estratégia e o cronograma.

## Histórico de decisões relevantes (changelog deste arquivo)

| Data | Mudança |
|------|---------|
| 2026-10-06 | Arquivo criado com os endpoints do TSE verificados, o formato do BU e os guardrails jurídicos. |
