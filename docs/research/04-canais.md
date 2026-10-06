---
title: "Canais, hábitos de mídia e dados abertos do TSE - Sua Urna"
date: 2026-10-06
type: research
status: draft
tags: [sua-urna-2026, pesquisa, eleicoes-2026]
project: sua-urna-2026
---

# Agente pesquisa-canais (2026-10-06)

## Hábitos de mídia
- Reuters DNR 2025 Brasil: fonte semanal de notícia: YouTube 37%, Instagram 37%, WhatsApp 36%, TikTok 18%. 33% seguem criadores de notícia. Redes lideram a TV por 9 pontos. Confiança 36%.
- Datafolha 1-2/09/2026 (2.002 eleitores): 57% viram conteúdo eleitoral em redes. Entre expostos: veículos 75%, jornalistas 71%, candidatos 69%, amigos/família 65%, influenciadores 61%, grupos de WhatsApp/Telegram 47%. Eleitor de Flávio: influenciadores 68%, mensageria 55%. Eleitor de Lula: 55% e 43%. Sem alinhamento: veículos 81%, jornalistas 74%, mensageria 39%.
- Recorte por segmento (60+, rural, evangélico, mulher) em fonte brasileira: NÃO ENCONTRADO. Global (DNR): 16-44 Instagram, 45+ WhatsApp.
- Evangélicos (Datafolha, antes do 1T): Flávio 62 x Lula 29. Baixa renda até 2 SM: Lula à frente.

## Alcance orgânico
- Zeeng jan-jun/2026 (Instagram, interação média por post): Nikolas Ferreira 1,47 mi, depois Michelle, Pavanato, Erika Hilton, Flávio (193 mil)... Lula 11o com 104 mil. 8 dos 10 são do PL. Nikolas ~22 mi seguidores.
- Direita domina interação; criadores de esquerda fora do top 10 exceto Erika Hilton. Conta nova sem audiência não alcança ninguém em 19 dias; alcance vem de quem já tem audiência.

## Iniciativas existentes
- Checagem: Fato ou Boato (TSE + 10 parceiros), Aos Fatos, Lupa. Landing page de "fatos" genérica compete com isso.
- 70+: campanha com Drauzio Varella e Tânia Maria (Agência Brasil, set/2026). Transporte: "Seu Voto Importa" (Res. 23.753/2026). TSE: "Boletim na Mão" no e-Título lê QR do BU impresso e mostra votos, brancos, nulos e abstenção.
- Vira Voto, Virando Votos (2022): nenhuma atividade 2026 encontrada.
- Saldo 1T: abstenção + brancos + nulos = 39,1 mi (24,63%).

## Dados do TSE
- dadosabertos.tse.jus.br: BU por seção existe para 2018-2024; 2026 ainda sem dataset de BU (entra após totalização final).
- resultados.tse.jus.br/oficial: JSON de totalização por UF, zona, seção. Projeto sibila (github.com/carlos-schwabe/sibila) descobre pleitos em ele-c.json, baixa por UF/zona/seção, limite ~90 req/s. Padrão 2022 de arquivo por urna: /oficial/ele2022/arquivo-urna/406/dados/[uf]/[mun]/[zona]/[secao]/[hash]/[arquivo]; BU em ASN.1 (github.com/doccaz/urnas-br, gist bu_dump.py).
- Endereço -> zona/seção: só e-Título e consulta oficial; sem API. Ferramenta deve pedir UF/município/zona/seção, nunca título (dado pessoal).

## Hospedagem
- Cloudflare Pages grátis (banda ilimitada, 500 builds/mês) é a opção mais robusta contra DDoS. GitHub Pages 100 GB/mês. Custo: domínio.
- Res. 23.610 art. 29: identificação clara do responsável. Site como pessoa física, não sob CNPJ.

## Fontes
reutersinstitute.politics.ox.ac.uk/digital-news-report/2026/brazil
tribunadejundiai.com.br/politica/eleicoes-2026/conteudo-eleitoral-redes-sociais/
static.poder360.com.br/uploads/2026/07/zeeng-politicos-mais-influentes-2026.pdf
exame.com/brasil/como-conferir-o-boletim-de-urna-da-sua-secao-pelo-celular/
agenciabrasil.ebc.com.br/politica/noticia/2026-09/campanha-incentiva-voto-de-quem-tem-mais-de-70-anos
congressoemfoco.com.br/noticia/122744/saldo-das-urnas-abstencoes-nulos-e-brancos-na-eleicao-de-2026
dadosabertos.tse.jus.br/dataset/?groups=resultados&res_format=CSV
github.com/carlos-schwabe/sibila ; github.com/doccaz/urnas-br
