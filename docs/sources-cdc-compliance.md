# Conformité sources de données (cahier des charges §6)

Toutes les sources CDC ont une **implémentation** dans le dépôt. Les jeux lourds se complètent via les mêmes identifiants Kaggle que PaySim.

| Source CDC | Implémentation | Données locales |
|------------|----------------|-----------------|
| **PaySim (Kaggle)** | `paysim_mapping` + `--mode paysim` | `make ingest-paysim-zip` / `archive.zip` |
| **MoMTSim (Makerere)** | `momtsim_mapping` + `--mode momtsim` | `make download-momtsim` ou `make ingest-momtsim-zip` |
| **Générateur Togo (Faker)** | `togo_generator` + `--mode synthetic` | code |
| **Scénarios fraude F3 / MoMTSim** | `fraud_injector.momtsim_scenario_pack` | code |
| **GSMA** | `config/gsma_rule_mapping.yaml` → R1–R6 | `make import-references` (+ PDF si `fetch_gsma_pdfs`) |
| **IBM AMLSim / AI4FCF** | `config/ai4fcf_opensources.yaml` + README | `data/references/AMLSim-README.md` |
| **Article PaySim** | `docs/paysim-limits.md` + README | citation |

## Mode agrégateur CDC

```bash
# Les 3 flux transactionnels + injection fraude
.venv/bin/python -m producer.main --mode hybrid --rate 500
```

Rotation : **Togo** → **PaySim** → **MoMTSim** (1 événement sur 3 chacun) + paquets fraude MoMTSim.

## Compléter MoMTSim (même compte Kaggle)

```bash
make download-momtsim
# ou ZIP Mendeley dans data/momtsim/ puis :
make ingest-momtsim-zip chemin/vers/fichier.zip
```

## Vérification

```bash
make import-references
make sources-status
```

Le fichier `data/references/sources_inventory.json` détaille chaque source (`ok`, `sample_or_missing`, `partial`).

**PaySim** : vous avez déjà le CSV complet. **MoMTSim** : exécutez `make download-momtsim` une fois le token Kaggle configuré pour passer de l’échantillon test au jeu complet (~4M lignes).