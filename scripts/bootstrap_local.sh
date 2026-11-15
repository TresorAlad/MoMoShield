#!/usr/bin/env bash
# Stack locale complète sans build Docker des apps (infra Docker + Python venv).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

RUN_DIR="$ROOT/.run"
# shellcheck source=lib_local_services.sh
source "$ROOT/scripts/lib_local_services.sh"
BRONZE_DIR="${BRONZE_DIR:-$ROOT/data/bronze}"
KAFKA_BOOTSTRAP="${KAFKA_BOOTSTRAP:-localhost:9092}"
DATABASE_URL="${DATABASE_URL:-postgresql://momoshield:momoshield_dev@localhost:15432/momoshield}"
PRODUCER_RATE="${PRODUCER_RATE:-500}"
BOOTSTRAP_TX_SECONDS="${BOOTSTRAP_TX_SECONDS:-20}"
INSTALL_DBT="${INSTALL_DBT:-1}"
KEEP_PRODUCER="${KEEP_PRODUCER:-1}"
START_STREAMLIT="${START_STREAMLIT:-1}"
START_AIRFLOW="${START_AIRFLOW:-1}"

log() { printf '[bootstrap] %s\n' "$*"; }

if [[ ! -x "$ROOT/.venv/bin/python" ]]; then
  log "Création du venv…"
  python3 -m venv "$ROOT/.venv"
fi

log "Dépendances Python (producer)…"
"$ROOT/.venv/bin/pip" install -q -e ".[producer]"

if [[ "$INSTALL_DBT" == "1" ]]; then
  log "Dépendances dbt (optionnel)…"
  "$ROOT/.venv/bin/pip" install -q -e ".[dbt]" 2>/dev/null || true
fi

log "Docker infra (Kafka + Postgres)…"
docker compose --profile infra up -d

if [[ "$START_AIRFLOW" == "1" ]]; then
  log "Airflow (profil full, lié à Kafka/Postgres)…"
  if ! docker compose --profile full up -d --build \
    airflow-init airflow-webserver airflow-scheduler; then
    log "Airflow Docker non démarré (souvent réseau/DNS au build). Réessaie: make up-airflow"
    log "Kafka reste disponible sur $KAFKA_BOOTSTRAP"
  fi
fi

log "Attente Postgres…"
deadline=$((SECONDS + 90))
until PGPASSWORD=momoshield_dev psql -h localhost -p 15432 -U momoshield -d momoshield -c 'SELECT 1' >/dev/null 2>&1; do
  (( SECONDS >= deadline )) && { echo "Postgres timeout" >&2; exit 1; }
  sleep 2
done

log "Attente Kafka…"
deadline=$((SECONDS + 90))
until docker compose exec -T kafka kafka-topics --bootstrap-server localhost:29092 --list >/dev/null 2>&1; do
  (( SECONDS >= deadline )) && { echo "Kafka timeout" >&2; exit 1; }
  sleep 2
done

chmod +x "$ROOT/scripts/apply_staging_schema.sh"
DATABASE_URL="$DATABASE_URL" "$ROOT/scripts/apply_staging_schema.sh"

if [[ ! -f "$ROOT/data/references/sources_inventory.json" ]]; then
  log "Import métadonnées références…"
  chmod +x "$ROOT/scripts/import_reference_data.sh"
  "$ROOT/scripts/import_reference_data.sh" || true
fi

mkdir -p "$BRONZE_DIR" "$RUN_DIR"

exec 9>"$RUN_DIR/bootstrap.lock"
if ! flock -n 9; then
  log "Un bootstrap est déjà en cours (verrou $RUN_DIR/bootstrap.lock). Abandon."
  log "Sinon : make bootstrap-stop puis relance."
  exit 1
fi

log "Arrêt des services locaux existants (PID + orphelins)…"
momoshield_stop_local_services "$ROOT" "$RUN_DIR"

log "Consumer streaming (arrière-plan)…"
nohup env PYTHONPATH="$ROOT" BRONZE_DIR="$BRONZE_DIR" KAFKA_BOOTSTRAP="$KAFKA_BOOTSTRAP" \
  "$ROOT/.venv/bin/python" -m streaming.python_consumer \
  >>"$RUN_DIR/consumer.log" 2>&1 &
echo $! >"$RUN_DIR/consumer.pid"

sleep 3
consumer_count="$(momoshield_count_repo_processes "$ROOT" "streaming.python_consumer")"
if [[ "$consumer_count" != "1" ]]; then
  log "ATTENTION : $consumer_count consumer(s) détecté(s) — attendu 1. make bootstrap-stop puis relance."
fi

log "Producteur hybrid ${PRODUCER_RATE}/s pendant ${BOOTSTRAP_TX_SECONDS}s…"
timeout "$BOOTSTRAP_TX_SECONDS" env PYTHONPATH="$ROOT" KAFKA_BOOTSTRAP="$KAFKA_BOOTSTRAP" \
  "$ROOT/.venv/bin/python" -m producer.main --mode hybrid --rate "$PRODUCER_RATE" \
  >>"$RUN_DIR/producer.log" 2>&1 || true

if [[ "$KEEP_PRODUCER" == "1" ]]; then
  log "Producteur continu (arrière-plan)…"
  nohup env PYTHONPATH="$ROOT" KAFKA_BOOTSTRAP="$KAFKA_BOOTSTRAP" \
    "$ROOT/.venv/bin/python" -m producer.main --mode hybrid --rate "$PRODUCER_RATE" \
    >>"$RUN_DIR/producer.log" 2>&1 &
  echo $! >"$RUN_DIR/producer.pid"
fi

sleep 2

log "Consolidation bronze → Postgres…"
PYTHONPATH="$ROOT" DATABASE_URL="$DATABASE_URL" BRONZE_DIR="$BRONZE_DIR" \
  "$ROOT/.venv/bin/python" - <<'PY'
from momoshield.batch.bronze_loader import consolidate_day
import json
print(json.dumps(consolidate_day(), indent=2, default=str))
PY

if "$ROOT/.venv/bin/python" -c "import dbt" 2>/dev/null; then
  log "dbt seed + run…"
  (
    cd "$ROOT/dbt"
    export POSTGRES_HOST=localhost POSTGRES_USER=momoshield POSTGRES_PASSWORD=momoshield_dev
    export POSTGRES_DB=momoshield POSTGRES_PORT=15432
    "$ROOT/.venv/bin/dbt" seed --quiet || true
    "$ROOT/.venv/bin/dbt" run --quiet
  )
else
  log "dbt absent — ignoré (INSTALL_DBT=1 au prochain run)"
fi

if [[ "$START_STREAMLIT" == "1" ]]; then
  log "Dashboard Streamlit…"
  "$ROOT/.venv/bin/pip" install -q -e ".[streamlit]" 2>/dev/null || true
  momoshield_stop_streamlit "$ROOT"
  rm -f "$RUN_DIR/streamlit.pid"
  nohup env PYTHONPATH="$ROOT" DATABASE_URL="$DATABASE_URL" \
    "$ROOT/.venv/bin/streamlit" run "$ROOT/dashboards/app.py" \
    --server.address 0.0.0.0 --server.port 8501 --server.headless true \
    >>"$RUN_DIR/streamlit.log" 2>&1 &
  echo $! >"$RUN_DIR/streamlit.pid"
fi

log "Terminé."
log "  Consumer PID: $(cat "$RUN_DIR/consumer.pid" 2>/dev/null || echo n/a) — logs: $RUN_DIR/consumer.log"
log "  Producer PID: $(cat "$RUN_DIR/producer.pid" 2>/dev/null || echo n/a)"
log "  Streamlit: http://localhost:8501 (PID $(cat "$RUN_DIR/streamlit.pid" 2>/dev/null || echo n/a))"
if [[ "$START_AIRFLOW" == "1" ]]; then
  log "  Airflow: http://localhost:${AIRFLOW_WEB_PORT:-8088} (admin / admin par défaut)"
  log "  Kafka: $KAFKA_BOOTSTRAP (topics via docker kafka-init)"
fi
log "  Postgres: $DATABASE_URL"
log "  Bronze: $BRONZE_DIR"
log "  Arrêt services locaux: make bootstrap-stop"