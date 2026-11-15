#!/usr/bin/env bash
# Résout le binaire Kaggle (.venv) et vérit le token (nouveau KGAT_ ou kaggle.json).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_KAGGLE="${ROOT}/.venv/bin/kaggle"
KAGGLE_DIR="${KAGGLE_CONFIG_DIR:-$HOME/.kaggle}"
ACCESS_TOKEN="${KAGGLE_DIR}/access_token"
KAGGLE_JSON="${KAGGLE_DIR}/kaggle.json"

ensure_kaggle_cli() {
  if [[ -x "$VENV_KAGGLE" ]]; then
    return 0
  fi
  if command -v kaggle >/dev/null 2>&1; then
    VENV_KAGGLE="$(command -v kaggle)"
    return 0
  fi
  if [[ -x "${ROOT}/.venv/bin/pip" ]]; then
    echo "Installation du CLI Kaggle dans .venv ..."
    "${ROOT}/.venv/bin/pip" install -q -U "kaggle>=1.6" six
  fi
  if [[ -x "$VENV_KAGGLE" ]]; then
    return 0
  fi
  echo "Impossible d'installer kaggle. Lancez :" >&2
  echo "  cd $ROOT && .venv/bin/pip install -U kaggle" >&2
  exit 1
}

has_kaggle_credentials() {
  [[ -n "${KAGGLE_API_TOKEN:-}" ]] && return 0
  [[ -f "$ACCESS_TOKEN" ]] && [[ -s "$ACCESS_TOKEN" ]] && return 0
  [[ -f "$KAGGLE_JSON" ]] && return 0
  return 1
}

ensure_kaggle_credentials() {
  if has_kaggle_credentials; then
    if [[ -f "$ACCESS_TOKEN" ]]; then
      chmod 600 "$ACCESS_TOKEN" 2>/dev/null || true
    fi
    if [[ -f "$KAGGLE_JSON" ]]; then
      chmod 600 "$KAGGLE_JSON" 2>/dev/null || true
    fi
    return 0
  fi

  echo "Identifiants Kaggle manquants." >&2
  echo "" >&2
  echo "Nouveau format (recommandé) — https://www.kaggle.com/settings → API Tokens :" >&2
  echo "  mkdir -p ~/.kaggle" >&2
  echo '  echo "VOTRE_KGAT_xxxxxxxx" > ~/.kaggle/access_token' >&2
  echo "  chmod 600 ~/.kaggle/access_token" >&2
  echo "" >&2
  echo "Ou variable de session :" >&2
  echo '  export KAGGLE_API_TOKEN="VOTRE_KGAT_xxxxxxxx"' >&2
  echo "" >&2
  echo "Ancien format : ~/.kaggle/kaggle.json (téléchargé depuis les settings)" >&2
  echo "" >&2
  echo "Sans API : make ingest-momtsim-zip /chemin/vers/archive.zip" >&2
  exit 1
}

ensure_kaggle_cli
ensure_kaggle_credentials
KAGGLE_BIN="$VENV_KAGGLE"
export KAGGLE_BIN