#!/usr/bin/env bash
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
mkdir -p outputs/logs
LOG="outputs/logs/phase0_verify_$(date +%Y%m%d_%H%M%S).log"
exec > >(tee -a "$LOG") 2>&1
FAIL=0
echo "== OpsTwin Phase 0 verification =="
echo "-- interpreter --"; .venv/bin/python --version
echo "-- container engine --"; docker --version; docker compose version; colima status 2>&1 | head -n 3
echo "-- orchestration and IaC tooling --"
for t in terraform kind kubectl; do
  if command -v "$t" >/dev/null 2>&1; then
    case "$t" in
      kubectl) kubectl version --client 2>/dev/null | head -n 1 ;;
      *) "$t" version 2>/dev/null | head -n 1 ;;
    esac
  else
    echo "MISSING: $t"; FAIL=1
  fi
done
echo "-- invariants --"
.venv/bin/pytest -q || FAIL=1
echo "-- result --"
if [ "$FAIL" -eq 0 ]; then echo "PHASE 0 GATE: PASS"; else echo "PHASE 0 GATE: FAIL"; fi
exit "$FAIL"