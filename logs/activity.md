---
title: "Activity Log - sua-urna-2026"
date: 2026-10-06
type: log
status: active
tags: [log, sua-urna-2026]
project: sua-urna-2026
---

# Activity Log
- 2026-10-06 08:30:00 -03 - Pesquisa inicial: transcrição do vídeo "Analisei 499 Mil Urnas" (Filipe Boni, 2026-10-05), quatro agentes de pesquisa (números do 1º turno, fatos sobre Flávio Bolsonaro, regras do TSE, canais e dados abertos). Síntese em [[Síntese de pesquisa - Sua Urna 2026]].
- 2026-10-06 09:10:00 -03 - Spike: endpoints de config, município, seção e BU do TSE respondem 200; BU de 2026 decodifica com a spec ASN.1 pública de 2022; sem CORS no TSE, decisão por JSON estático pré-computado.
- 2026-10-06 09:20:00 -03 - Scaffold criado a partir do blueprint: [[AGENTS - sua-urna-2026]], [[TASKS - sua-urna-2026]], docs/research, src, tests, site.
- 2026-10-06 09:05:00 -03 - T-002: pipeline escrito com TDD (tse_urls, models, bu_decoder, aggregate, tse_client, filters, CLI), 32 testes verdes, ruff limpo. Coleta do Amapá: 1.971 seções, 1.914 com BU, totais batem com o TSE em 16 municípios (só nulo técnico difere).
- 2026-10-06 09:20:00 -03 - Dono redirecionou a prioridade: RMSP primeiro, depois SP, MG, PR e RS. Coleta em segundo plano iniciada (logs/fetch-*.log). Site MVP escrito (index.html, style.css, app.js, kits.js com 7 roteiros e 20 fatos com fonte).
- 2026-10-06 09:40:00 -03 - T-003 e T-011: site validado headless (Playwright, 420 px): seleção por hash, conta por seção, 7 roteiros, 20 fatos, zero erro de console. Painel "Dá para virar" com urna média calculada do brasil.json (318, 112, 108, 19, 12, 67, iguais aos do vídeo). Paleta ajustada para a referência validada (azul e vermelho) com neutros rotulados.
- 2026-10-06 09:50:00 -03 - Dono ampliou a coleta: SC, RJ, ES, GO, DF, MS e MT encadeados após SP, MG, PR e RS (logs/fetch-<uf>.log). Links dos fatos conferidos: 17 de 18 respondem, TSE bloqueia robô.
- 2026-10-06 10:00:00 -03 - Dono viu só o Amapá no site: o índice de estados só era gravado no fim da coleta. Corrigido: estado entra no início, município ganha flag `ok`, comando `reindex` criado e executado (SP com 38 de 39 da RMSP prontos). 33 testes verdes.
- 2026-10-06 10:40:00 -03 - T-012 e T-013: página progresso.html (plan.json com 321.096 seções nos 12 estados, progress.json, rate.json), interface v2 com paleta vermelho, branco e preto a pedido do dono, Bricolage Grotesque e Public Sans, seletor de tema, cards de fatos com filtro, roteiros em abas, imagem com os pontos da seção, seletores ordenados e frase de esforço por pessoa. Validado headless nos dois temas, sem estouro horizontal e sem erro de console. 33 testes verdes.
- 2026-10-06 11:10:00 -03 - Roteiros passam a cards de pessoa em grade (ponto na cor do grupo, título como gente, número do grupo, prioritário em duas colunas). Corrigida colisão da classe `.tema` entre o botão de tema e a etiqueta dos cards de fato.
- 2026-10-06 10:30:00 -03 - T-007: dono criou o repositório e publicou pelo workflow de Pages; endereço https://iurizambotto.github.io/sua-urna-2026/ conferido nos dois temas (dados pelo subcaminho, fontes, imagem, botão de tema, progresso), sem erro de console nem falha de rede. Coleta: SP completo, MG em 82%.
- 2026-10-06 11:10:00 -03 - Leva 1 (SP, MG, PR, RS) interrompida pelo limite de 2 h do job em segundo plano com RS em 485 de 497; leva 2 (SC, RJ, ES, GO, DF, MS, MT) seguiu sozinha; retomada dos 12 municípios de RS enfileirada após a leva 2. SP, MG e PR completos e publicados pelo dono.
- 2026-10-06 11:15:00 -03 - Leva 2 também morreu no limite de 2 h (SC em 225 de 295). Fila restante (SC, RJ, ES, GO, DF, MS, MT) relançada por scripts/run_queue.sh desacoplado da sessão (setsid nohup), que espera a retomada do RS terminar e roda um estado por vez com --skip-existing; registro em logs/queue.log.
- 2026-10-06 12:10:00 -03 - Fila desacoplada concluiu SC, RJ, ES, GO, DF, MS e MT: 12 estados completos, zero seção com erro. A pedido do dono, plano ampliado para os 27 estados (514.464 seções) e os 15 restantes lançados em quatro filas paralelas a 20 req/s. Gravação atômica de JSON. Criado scripts/sync_site.sh para publicação contínua.
- 2026-10-06 13:40:00 -03 - As quatro filas das 12:10 terminaram sem coletar nada: o zsh passou cada lista de estados como um argumento só. O sincronizador do dono viu a coleta parada e publicou 12 estados. Filas relançadas às 13:38 dentro de bash; BA, CE, PE e PA coletando.
- 2026-10-06 14:20:00 -03 - T-014: comando `pages` gera páginas por município com prévia própria (fontes Bricolage Grotesque e Public Sans, OFL, em src/sua_urna_2026/fonts), integrado ao sync_site.sh; analytics.js neutro entre GoatCounter e Umami, desligado até configurar; botão de WhatsApp por roteiro com mensagem própria; links com ?r=; privacidade reescrita. 39 testes verdes, validado headless.
- 2026-10-06 14:05:00 -03 - Dono não achou o botão de WhatsApp (estava só no Passo 3 e o JS antigo estava em cache). Botão "Enviar no WhatsApp" adicionado ao resultado da seção, com evento whatsapp-secao; arquivos estáticos versionados com ?v=.
