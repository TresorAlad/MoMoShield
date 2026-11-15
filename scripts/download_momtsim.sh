#!/usr/bin/env bash
# MoMTSim sur Kaggle : denishazamuke/synthetic-mobile-money-transaction-dataset
# Mendeley alternatif : https://data.mendeley.com/datasets/zhj366m53p/2
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=scripts/kaggle_cli.sh
source "${ROOT}/scripts/kaggle_cli.sh"

DATA_DIR="${ROOT}/data/momtsim"
mkdir -p "$DATA_DIR"

echo "Téléchargement MoMTSim (Kaggle) vers $DATA_DIR ..."
"$KAGGLE_BIN" datasets download -d denishazamuke/synthetic-mobile-money-transaction-dataset -p "$DATA_DIR" --unzip

CSV="$(find "$DATA_DIR" -name '*.csv' -type f -printf '%s %p\n' 2>/dev/null | sort -rn | head -1 | cut -d' ' -f2-)"
if [[ -z "$CSV" ]]; then
  CSV="$(find "$DATA_DIR" -name '*.csv' -type f | head -1)"
fi
if [[ -z "$CSV" ]]; then
  echo "Aucun CSV MoMTSim après extraction." >&2
  exit 1
fi

echo "MoMTSim prêt : $CSV"
echo "  .venv/bin/python -m producer.main --mode momtsim --rate 500 --loop"