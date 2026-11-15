#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
URL="${DATABASE_URL:-postgresql://momoshield:momoshield_dev@localhost:15432/momoshield}"
for f in "${ROOT}/scripts/sql/001_staging.sql" "${ROOT}/scripts/sql/002_staging_extend.sql"; do
  [ -f "$f" ] && psql "$URL" -f "$f"
done
echo "Schéma staging / quarantine appliqué (Postgres : make up-infra si besoin)."