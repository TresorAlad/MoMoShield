#!/usr/bin/env bash
# Artefacts CDC §6 : références téléchargeables (GSMA, AMLSim, bibliographie).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REF_DIR="${ROOT}/data/references"
mkdir -p "$REF_DIR"

cp -f "${ROOT}/config/reference_sources.yaml" "${REF_DIR}/reference_sources.yaml"
cp -f "${ROOT}/config/ai4fcf_opensources.yaml" "${REF_DIR}/ai4fcf_opensources.yaml"
cp -f "${ROOT}/config/gsma_rule_mapping.yaml" "${REF_DIR}/gsma_rule_mapping.yaml"
cp -f "${ROOT}/config/momtsim_scenarios.yaml" "${REF_DIR}/momtsim-metadata.yaml"
cp -f "${ROOT}/docs/paysim-limits.md" "${REF_DIR}/paysim-citation.md" 2>/dev/null || true

UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
fetch() {
  local url="$1" out="$2"
  if command -v curl >/dev/null 2>&1; then
    curl -fsSL --retry 2 --connect-timeout 30 -A "$UA" -L "$url" -o "$out" && echo "OK $out" || echo "SKIP $out"
  fi
}

# IBM AMLSim
fetch "https://raw.githubusercontent.com/IBM/AMLSim/master/README.md" "${REF_DIR}/AMLSim-README.md"

# GSMA — typologies fraude MoMo (CDC)
fetch \
  "https://www.gsma.com/solutions-and-impact/connectivity-for-good/mobile-for-development/wp-content/uploads/2024/03/GSMA-Fraud-Typologies-04-03-24.pdf" \
  "${REF_DIR}/gsma-fraud-typologies-2024.pdf"

fetch \
  "https://www.gsma.com/solutions-and-impact/connectivity-for-good/mobile-for-development/wp-content/uploads/2020/04/Mitigating-common-fraud-risks-best-practices-for-the-mobile-money-industry_4.pdf" \
  "${REF_DIR}/gsma-mitigating-common-fraud-risks-2020.pdf"

# PaySim article (page publique ResearchGate — métadonnées HTML légères)
fetch \
  "https://www.researchgate.net/publication/306772897_PaySim_A_financial_mobile_money_simulator_for_fraud_detection" \
  "${REF_DIR}/paysim-paper-researchgate.html" || true

# MoMTSim — fiche article PMC (métadonnées)
fetch "https://pmc.ncbi.nlm.nih.gov/articles/PMC12036017/" "${REF_DIR}/momtsim-pmc-article.html"

chmod +x "${ROOT}/scripts/fetch_gsma_pdfs.sh"
"${ROOT}/scripts/fetch_gsma_pdfs.sh" || true

# Inventaire CDC
export PYTHONPATH="${ROOT}:${PYTHONPATH:-}"
python3 -c "from momoshield.io.sources_compliance import write_inventory; write_inventory(); print('Wrote sources_inventory.json')"

echo ""
echo "Références dans ${REF_DIR}/"
ls -lh "${REF_DIR}" 2>/dev/null | tail -n +2 || true
echo ""
echo "PaySim Kafka : data/paysim/*.csv (make ingest-paysim-zip)"
echo "MoMTSim CSV  : téléchargement manuel Mendeley/Kaggle (voir config/momtsim_scenarios.yaml)"