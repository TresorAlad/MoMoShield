#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ZIP="${1:-}"
DATA_DIR="${ROOT}/data/momtsim"
mkdir -p "$DATA_DIR"

if [[ -z "$ZIP" ]]; then
  for guess in \
    "$ROOT/data/momtsim"/*.zip \
    "$ROOT"/momtsim*.zip \
    "$ROOT"/*momtsim*.zip \
    "$ROOT"/archive-momtsim.zip \
    "$ROOT"/synthetic*.zip; do
    [[ -f "$guess" ]] && ZIP="$guess" && break
  done
fi

if [[ -z "$ZIP" ]] || [[ ! -f "$ZIP" ]]; then
  echo "Usage: $0 /chemin/vers/momtsim.zip" >&2
  exit 1
fi

unzip -o -q "$ZIP" -d "$DATA_DIR"
CSV="$(find "$DATA_DIR" -name '*.csv' -type f -printf '%s %p\n' 2>/dev/null | sort -rn | head -1 | cut -d' ' -f2-)"
[[ -z "$CSV" ]] && CSV="$(find "$DATA_DIR" -name '*.csv' -type f | head -1)"
echo "MoMTSim : $CSV"