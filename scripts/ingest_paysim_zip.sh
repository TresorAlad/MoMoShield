#!/usr/bin/env bash
# Import manuel : placer archive.zip (Kaggle) à la racine du repo ou passer le chemin en arg.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ZIP="${1:-${ROOT}/archive.zip}"
DATA_DIR="${ROOT}/data/paysim"

if [[ ! -f "$ZIP" ]]; then
  echo "Archive introuvable : $ZIP" >&2
  echo "Usage: $0 [/chemin/vers/archive.zip]" >&2
  exit 1
fi

mkdir -p "$DATA_DIR"
echo "Extraction vers $DATA_DIR ..."
unzip -o -q "$ZIP" -d "$DATA_DIR"

CSV="$(find "$DATA_DIR" -maxdepth 1 -name '*.csv' -type f -printf '%s %p\n' 2>/dev/null | sort -rn | head -1 | cut -d' ' -f2-)"
if [[ -z "$CSV" ]]; then
  CSV="$(find "$DATA_DIR" -maxdepth 1 -name '*.csv' -type f | head -1)"
fi

if [[ -z "$CSV" ]]; then
  echo "Aucun CSV dans $DATA_DIR" >&2
  exit 1
fi

echo "PaySim prêt : $CSV"
echo "  .venv/bin/python -m producer.main --mode paysim --rate 500 --loop"