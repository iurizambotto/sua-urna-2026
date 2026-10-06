---
title: "TASKS - sua-urna-2026"
date: 2026-10-06
type: tasks
status: active
tags: [tasks, sua-urna-2026, eleicoes-2026]
project: sua-urna-2026
---

# TASKS - sua-urna-2026

Ver [[AGENTS - sua-urna-2026]] e [[Síntese de pesquisa - Sua Urna 2026]].

## Backlog ativo

- [x] T-001 · Scaffold do projeto, dossiê de pesquisa e spike dos endpoints do TSE (2026-10-06)
- [x] T-002 · Pipeline: URLs, decodificação do BU, cliente com limite de taxa, agregação por município, CLI, filtros e retomada (32 testes, 2026-10-06)
- [x] T-003 · Site MVP: seleção UF, município, zona, seção; números da urna; conta de "quantos precisam mudar"; card para WhatsApp; link direto por hash (validado headless, 2026-10-06)
- [x] T-011 · Painel "Dá para virar": número herói, urna média de 318 pontos, blocos de números e precedente de 2022 (2026-10-06)
- [x] T-012 · Página de progresso da coleta com percentual por estado e município e estimativa de tempo; comandos `plan` e `reindex` (2026-10-06)
- [x] T-013 · Interface v2: paleta vermelho, branco e preto, tipografia própria, seletor de tema, fatos em cards com filtro por tema, roteiros em abas com botão de copiar, imagem de compartilhamento com os pontos da seção, seletores ordenados, mensagem de esforço por pessoa (2026-10-06)
- [ ] T-004 · Kits de conversa por perfil (7 perfis) em site/kits.js (escrito, falta revisão do dono)
- [ ] T-005 · Fatos com fonte e status em site/kits.js, 20 fatos (escrito, falta conferir cada URL com um link checker)
- [ ] T-006 · Rodar o pipeline por prioridade: RMSP, depois SP, MG, PR, RS (leva 1, desde 09:20) e SC, RJ, ES, GO, DF, MS, MT (leva 2, encadeada); validar cada UF contra os totais do TSE; Norte e Nordeste em coleta paralela desde 12:10
- [x] T-007 · MVP publicado em GitHub Pages por workflow (`.github/workflows/pages.yml`, repositório público `iurizambotto/sua-urna-2026`, dados versionados em `site/data`), com `noindex` enquanto for só para amigos (2026-10-06). Pendente para o lançamento: tirar o `noindex`, avaliar Cloudflare Pages e domínio em nome de pessoa física
- [ ] T-008 · Cinco vídeos verticais de 45 s derivados do site, sem IA de voz ou rosto
- [x] T-014 · Compartilhamento e medição: páginas por município com prévia própria (3.633 páginas, 896 imagens), botão de WhatsApp por roteiro, origem marcada nos links, camada de medição anônima até a zona, texto de privacidade reescrito (2026-10-06)
- [ ] T-015 · Dono cria a conta no GoatCounter e informa o código; preencher `site/config.js`
- [ ] T-009 · Distribuição: Filipe Boni, equipe digital da campanha, criadores, grupos pessoais
- [ ] T-010 · Atualizar fatos após o debate de 11/10 e a AtlasIntel de 09/10

## Próximo

T-004 (revisão dos roteiros pelo dono), T-006 (acompanhar a coleta), T-007 (repositório e deploy)

## Bloqueadores

nenhum

## Histórico comprimido

- 2026-10-06 Pesquisa com quatro frentes (números, fatos, TSE, canais), transcrição do vídeo do Boni, spike dos endpoints do TSE com BU decodificado, scaffold criado.
