#!/usr/bin/env bash
# Télécharge le jeu PaySim (Kaggle) : https://www.kaggle.com/datasets/ealaxi/paysim1
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=scripts/kaggle_cli.sh
source "${ROOT}/scripts/kaggle_cli.sh"

DATA_DIR="${ROOT}/data/paysim"
mkdir -p "$DATA_DIR"

echo "Téléchargement ealaxi/paysim1 vers $DATA_DIR ..."
"$KAGGLE_BIN" datasets download -d ealaxi/paysim1 -p "$DATA_DIR" --unzip

CSV="$(find "$DATA_DIR" -maxdepth 1 -name '*.csv' -type f | head -1)"
if [[ -z "$CSV" ]]; then
  echo "Aucun CSV trouvé après extraction." >&2
  exit 1
fi

echo "Fichier prêt : $CSV"
echo "  .venv/bin/python -m producer.main --mode paysim --rate 500 --loop"