#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

export PYTHONPATH="${ROOT}:${PYTHONPATH:-}"
export AIRFLOW_HOME="${ROOT}/airflow"
export AIRFLOW__CORE__LOAD_EXAMPLES=False
export AIRFLOW__DATABASE__SQL_ALCHEMY_CONN="${AIRFLOW__DATABASE__SQL_ALCHEMY_CONN:-sqlite:////tmp/airflow_ci.db}"

echo "=== P0: ruff ==="
ruff check .
ruff format --check .

echo "=== P1: pytest unit ==="
pytest tests/unit -q --cov=streaming/rules --cov-report=term-missing:skip-covered --cov-fail-under=70

echo "=== P2: contract ==="
python -m momoshield.contracts.validate

echo "=== P3: DAGs ==="
python -m tests.validate_dags

echo "=== P4: dbt parse ==="
if command -v dbt >/dev/null 2>&1; then
  (cd dbt && dbt parse --profiles-dir .)
else
  echo "dbt not in PATH, skipping P4 (ok in slim CI if dbt-core installed in image)"
  (cd dbt && python -c "import yaml; yaml.safe_load(open('dbt_project.yml'))")
fi

if [[ "${RUN_INTEGRATION:-0}" == "1" ]]; then
  echo "=== P5: integration ==="
  pytest tests/integration -m "integration and not slow" -q
fi

echo "CI paliers terminés avec succès"