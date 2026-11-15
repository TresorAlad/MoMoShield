#!/usr/bin/env bash
set -euo pipefail

SERVICE="${1:?service name}"
TIMEOUT="${2:-120}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

deadline=$((SECONDS + TIMEOUT))
while (( SECONDS < deadline )); do
  if docker compose ps --status running --format json 2>/dev/null | grep -q "\"$SERVICE\""; then
    health="$(docker inspect --format='{{.State.Health.Status}}' "$(docker compose ps -q "$SERVICE" 2>/dev/null | head -1)" 2>/dev/null || echo "none")"
    if [[ "$health" == "healthy" || "$health" == "none" ]]; then
      echo "$SERVICE ready"
      exit 0
    fi
  fi
  sleep 2
done
echo "Timeout waiting for $SERVICE" >&2
exit 1