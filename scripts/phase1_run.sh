#!/usr/bin/env bash
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
mkdir -p outputs/logs
LOG="outputs/logs/phase1_run_$(date +%Y%m%d_%H%M%S).log"
exec > >(tee -a "$LOG") 2>&1
FAIL=0
echo "== OpsTwin Phase 1 =="
.venv/bin/python --version || FAIL=1
docker compose version >/dev/null 2>&1 || { echo "MISSING: docker compose plugin"; FAIL=1; }
if ! docker exec opstwin_postgres pg_isready -U opstwin -d opstwin_ops >/dev/null 2>&1; then
  docker compose -f src/platform/docker/postgres.yml up -d
  for i in $(seq 1 30); do
    docker exec opstwin_postgres pg_isready -U opstwin -d opstwin_ops >/dev/null 2>&1 && break
    sleep 2
  done
fi
docker exec opstwin_postgres pg_isready -U opstwin -d opstwin_ops || FAIL=1
.venv/bin/python -m src.data.generate --months "${MONTHS:-24}" || FAIL=1
.venv/bin/pytest -q tests/test_phase1.py || FAIL=1
if [ "$FAIL" -eq 0 ]; then echo "PHASE 1 GATE: PASS"; else echo "PHASE 1 GATE: FAIL"; fi
exit "$FAIL"