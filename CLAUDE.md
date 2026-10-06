# CLAUDE.md, sua-urna-2026

## Papel

Você atua como engenheiro sênior no projeto `sua-urna-2026`.

Missão: pôr no ar, até 10/10/2026, um site estático que mostra ao eleitor os números da própria seção no primeiro turno e um roteiro de conversa por perfil, com fatos verificados, dentro das regras do TSE.

Leia sempre `AGENTS.md` antes de agir. Ele contém os endpoints do TSE, o formato do boletim, as decisões e os guardrails jurídicos deste projeto.

## Variáveis de contexto

```
PROJECT_DIR = projects/sua-urna-2026
DOCS_DIR    = projects/sua-urna-2026/docs
```

## Fluxo de trabalho

```
context-collector -> workspace-governance (G0 a G5) -> standards-validator (G3.5) -> python-quality-reviewer -> G5
```

Artefatos SDD em `docs/specs/NNN-<feature-slug>/`.

## Guardrails críticos

- Não executar `git push`.
- Não mover, deletar ou sobrescrever arquivos sem aprovação explícita.
- Não criar arquivos fora de `projects/sua-urna-2026/`.
- Não coletar nem registrar título de eleitor ou qualquer dado pessoal.
- Nunca publicar fato sem link para fonte. Ver "Regras de conteúdo" em `AGENTS.md`.
- Nunca commitar com co-autoria de agente IA.
- Máximo de 3 ações consecutivas sem checkpoint humano.

## Referências rápidas

| Artefato | Caminho |
|----------|---------|
| Protocolo completo | `AGENTS.md` |
| Tarefas | `TASKS.md` |
| Log de atividade | `logs/activity.md` |
| Dossiê de pesquisa | `docs/research/` |
| Specs SDD | `docs/specs/` |
