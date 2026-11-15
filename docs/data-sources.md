# Sources de données (cahier des charges §6)

En attendant le CSV Kaggle complet, le pipeline peut tourner avec le **générateur Togo**, l’**échantillon PaySim** (`tests/data/paysim_sample.csv`) et le mode **`hybrid`**.

| Source | Rôle | Lien / commande |
|--------|------|-----------------|
| **PaySim (Kaggle)** | Volume, types, label `isFraud` | [ealaxi/paysim1](https://www.kaggle.com/datasets/ealaxi/paysim1) — `make download-paysim` |
| **Générateur Python (Faker)** | Contexte togolais + fraude F3 | `python -m producer.main --mode synthetic` |
| **Mode hybrid** | PaySim (si dispo) + Togo + scénarios MoMTSim | `python -m producer.main --mode hybrid` |
| **MoMTSim (Makerere)** | Inspiration SIM swap / takeover | [PubMed](https://pubmed.ncbi.nlm.nih.gov/) — requête « mobile money simulator fraud » ; logique dans `producer/fraud_injector.py` |
| **GSMA** | Typologie fraude MoMo | [Ressources GSMA M4D](https://www.gsma.com/solutions-and-impact/connectivity-for-good/mobile-for-development/resources/) |
| **IBM AMLSim** | Jeu ouvert complémentaire (citation) | [IBM/AMLSim](https://github.com/IBM/AMLSim) — `make import-references` (métadonnées) |
| **Catalogue AI4FCF** | Autres jeux (carte, etc.) | Voir conférences *AI4FCF* / ICDM ; exemple carte : [ULB creditcardfraud](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud) (hors périmètre contrat v1) |

## Ordre de résolution PaySim

1. Variable `PAYSIM_CSV`
2. Fichiers Kaggle connus (`PS_20174319_…csv` ou `PS_20174392719_…_log.csv`)
3. Le **plus gros** `data/paysim/*.csv` (import : `make ingest-paysim-zip` avec `archive.zip` à la racine)
4. `tests/data/paysim_sample.csv` (5 lignes)

## Enrichissement Togo sur PaySim

PaySim n’a pas de géographie : chaque ligne rejeuée reçoit ville, opérateur et `sim_id` depuis `config/cities_operators.yaml` (`PAYSIM_ENRICH_TOGO=1`, défaut activé).

## Références

- Lopez-Rojas, Elmir & Axelsson, *PaySim: A financial mobile money simulator for fraud detection*, EMSS 2016.
- Limites : [paysim-limits.md](paysim-limits.md).