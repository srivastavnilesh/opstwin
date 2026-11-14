#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
mkdir -p outputs/logs
LOG="outputs/logs/phase0_bootstrap_$(date +%Y%m%d_%H%M%S).log"
exec > >(tee -a "$LOG") 2>&1
echo "== OpsTwin Phase 0 bootstrap (reproducible path) =="
echo "host: $(uname -ms) | ram: $(( $(sysctl -n hw.memsize) / 1073741824 )) GB"
command -v brew >/dev/null || { echo "Install Homebrew first: https://brew.sh"; exit 1; }
command -v python3.12 >/dev/null || brew install python@3.12
for pkg in colima docker docker-compose kind kubectl; do
  command -v "$pkg" >/dev/null || brew install "$pkg"
done
brew tap hashicorp/tap >/dev/null 2>&1 || true
command -v terraform >/dev/null || brew install hashicorp/tap/terraform
if ! colima status >/dev/null 2>&1; then
  RAM_GB=$(( $(sysctl -n hw.memsize) / 1073741824 ))
  if [ "$RAM_GB" -ge 16 ]; then colima start --cpu 4 --memory 6; else colima start --cpu 2 --memory 4; fi
fi
docker run --rm hello-world
if [ ! -x .venv/bin/python ] || ! .venv/bin/python -c 'import sys; assert sys.version_info[:2]==(3,12)' 2>/dev/null; then
  rm -rf .venv
  python3.12 -m venv .venv
fi
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt -r requirements-dev.txt
mkdir -p data/bronze data/silver data/gold outputs/logs \
         src/data src/warehouse src/flows src/ml src/serving src/agent src/platform \
         app tests docs scripts
touch src/__init__.py src/data/__init__.py src/flows/__init__.py src/ml/__init__.py \
      src/serving/__init__.py src/agent/__init__.py tests/__init__.py
pytest -q tests/test_scaffold.py
echo "== bootstrap complete =="