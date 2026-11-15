#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REF="${ROOT}/data/references"
mkdir -p "$REF"
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

fetch() {
  local url="$1" out="$2"
  if curl -fsSL --retry 2 -A "$UA" -L "$url" -o "$out"; then
    echo "OK $out ($(wc -c <"$out") bytes)"
  else
    echo "ÉCHEC $out — télécharger manuellement :" >&2
    echo "  $url" >&2
    return 1
  fi
}

fetch \
  "https://www.gsma.com/solutions-and-impact/connectivity-for-good/mobile-for-development/wp-content/uploads/2024/03/GSMA-Fraud-Typologies-04-03-24.pdf" \
  "${REF}/gsma-fraud-typologies-2024.pdf" || true

fetch \
  "https://www.gsma.com/solutions-and-impact/connectivity-for-good/mobile-for-development/wp-content/uploads/2020/04/Mitigating-common-fraud-risks-best-practices-for-the-mobile-money-industry_4.pdf" \
  "${REF}/gsma-mitigating-common-fraud-risks-2020.pdf" || true