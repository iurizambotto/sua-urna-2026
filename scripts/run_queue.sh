#!/usr/bin/env bash
# Runs the collection queue for the given states, one at a time, resuming what is on disk.
# Meant to be launched detached (setsid nohup) so it does not depend on the session that started it.
set -u
cd "$(dirname "$0")/.." || exit 1
source .venv/bin/activate
export -n AWS_PROFILE 2>/dev/null || true
unset AWS_PROFILE
collector_running() {
  ps -eo args | grep -qE "^(python|/[^ ]*python) -m sua_urna_2026 fetch"
}
RATE="${RATE:-75}"
CONC="${CONC:-48}"
LANE="${LANE:-queue}"
# WAIT=0 lets several lanes run side by side; keep the sum of RATE under 80 req/s.
if [ "${WAIT:-1}" = "1" ]; then while collector_running; do sleep 30; done; fi
for uf in "$@"; do
  echo "$(date '+%F %T') [$LANE] start $uf"
  python -m sua_urna_2026 fetch --uf "$uf" --rate "$RATE" --concurrency "$CONC" --skip-existing --out site/data >> "logs/fetch-$uf.log" 2>&1
  echo "$(date '+%F %T') [$LANE] end $uf exit=$? $(grep -c 'sections ok' "logs/fetch-$uf.log") municipios"
done
python -m sua_urna_2026 reindex --out site/data
echo "$(date '+%F %T') [$LANE] queue done"
