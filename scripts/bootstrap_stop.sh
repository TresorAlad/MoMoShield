#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=lib_local_services.sh
source "$ROOT/scripts/lib_local_services.sh"

momoshield_stop_local_services "$ROOT" "$ROOT/.run"
printf '[bootstrap-stop] Services locaux arrêtés (consumer, producer, streamlit).\n'