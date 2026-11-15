#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT"
export DATABASE_URL="${DATABASE_URL:-postgresql://momoshield:momoshield_dev@localhost:15432/momoshield}"
exec "$ROOT/.venv/bin/streamlit" run "$ROOT/dashboards/app.py" \
  --server.address "${STREAMLIT_ADDRESS:-0.0.0.0}" \
  --server.port "${STREAMLIT_PORT:-8501}" \
  --server.headless true