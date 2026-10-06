#!/usr/bin/env bash
# Publishes collected data while collection runs: reindex, commit site/data, push. Final pass at the end.
set -u
cd "$(dirname "$0")/.." || exit 1
INTERVAL="${INTERVAL:-600}"
collecting() { ps -eo args | grep -qE "^bash scripts/run_queue.sh|^(python|/[^ ]*python) -m sua_urna_2026 fetch"; }
publish() {
  .venv/bin/python -m sua_urna_2026 reindex --out site/data >/dev/null 2>&1
  git add site/data
  if git diff --cached --quiet; then echo "$(date '+%F %T') sem mudanças"; return; fi
  local estados
  estados=$(python3 -c "import json; pr=json.load(open('site/data/progress.json')); print(sum(1 for v in pr['ufs'].values() if v['municipios_ok']==v['municipios_total']))")
  git commit -qm "data: $1 ($estados estados completos)" && git push -q && echo "$(date '+%F %T') publicado: $1, $estados estados completos"
}
while collecting; do publish "coleta parcial $(date +%H:%M)"; sleep "$INTERVAL"; done
publish "coleta completa"
echo "$(date '+%F %T') sync done"
