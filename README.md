# MoMoShield

**Pipeline data de détection de fraude Mobile Money** (données synthétiques et hybrides, contexte togolais).

> **Projet portfolio Data Engineering** — démonstration bout en bout d’un pipeline moderne (lambda : temps réel + batch), documenté pour recruteurs et pairs techniques. **Aucune donnée client réelle** : jeux synthétiques, échantillons PaySim et scénarios MoMTSim.

## Sommaire

- [Portfolio : objectif et compétences](#portfolio--objectif-et-compétences)
- [Fonctionnalités](#fonctionnalités)
- [Architecture](#architecture)
- [Stack technique](#stack-technique)
- [Prérequis](#prérequis)
- [Démarrage rapide](#démarrage-rapide)
- [Accès aux services](#accès-aux-services)
- [Structure du dépôt](#structure-du-dépôt)
- [Commandes Make](#commandes-make)
- [Orchestration Airflow](#orchestration-airflow)
- [Sources de données](#sources-de-données)
- [Tests et qualité](#tests-et-qualité)
- [Documentation](#documentation)
- [Licence des données](#licence-des-données)

## Portfolio : objectif et compétences

Ce dépôt illustre ce qu’un **ingénieur data** peut livrer sur un sujet **fraude Mobile Money** (contexte **Togo**), sans accès à des flux de production :

| Angle | Ce que le projet montre |
|-------|-------------------------|
| **Architecture** | Ingestion événementielle, medallion (bronze → staging → marts), batch orchestré |
| **Qualité** | Contrats JSON, quarantaine, dbt tests, contrôles GE, mart qualité |
| **Observabilité métier** | SLO documentés, dashboard Streamlit orienté décision |
| **Industrialisation** | Docker Compose par profils, `make bootstrap`, CI reproductible |
| **Gouvernance données** | Dictionnaires FR, politique de transformation, ADR |

**Pistes pour un entretien ou une vitrine :**

- Schéma d’architecture : [`docs/architecture-momoshield.jpg`](docs/architecture-momoshield.jpg)
- Fiche projet courte : [`docs/portfolio-fiche.md`](docs/portfolio-fiche.md)
- Article / narration (optionnel) : [`docs/linkedin-article.md`](docs/linkedin-article.md)

**Limites assumées (honnêteté portfolio)** : producteur et consumer tournent souvent en **local + venv** ; certains DAG Airflow restent des **squelettes** à durcir ; le jeu PaySim complet est **hors dépôt** (licence Kaggle).

## Fonctionnalités

- Génération / rejeu de transactions Mobile Money (Togo, PaySim, scénarios hybrides).
- Règles de fraude en streaming (Kafka) et écriture bronze + alertes.
- Consolidation batch vers PostgreSQL (staging, quarantaine).
- Modèles **dbt** (staging → intermediate → marts) avec colonnes et libellés métier en français.
- Contrôles qualité (Great Expectations léger + mart qualité).
- Dashboard **Streamlit** : KPI, carte du Togo, analyses fraude et qualité.
- CI locale via image Docker (`make ci`), sans GitHub Actions obligatoire.

## Architecture

Schéma d’architecture (temps réel · batch · consommation) :

![Schéma d’architecture MoMoShield](docs/architecture-momoshield.jpg)

Vue détaillée (Mermaid, rendu GitHub) :

```mermaid
flowchart LR
  subgraph speed [Temps réel]
    P[Producteur] --> K{{Kafka}}
    K --> C[Consumer streaming]
    C --> A[transactions.alerts]
    C --> B[Bronze NDJSON]
  end
  subgraph batch [Batch]
    B --> AF[Airflow]
    AF --> PG[(PostgreSQL)]
    PG --> DBT[dbt]
    DBT --> M[Marts]
    AF --> GE[Qualité GE]
  end
  subgraph viz [Consommation]
    PG --> ST[Streamlit]
    M --> ST
  end
```

Détail : [docs/architecture.md](docs/architecture.md).

## Stack technique

| Domaine | Outils |
|---------|--------|
| Messagerie | Apache Kafka, Schema Registry |
| Stockage | PostgreSQL, fichiers bronze NDJSON |
| Streaming | Python, règles fraude |
| Orchestration | Apache Airflow 2.8 |
| Transformation | dbt (Postgres) |
| Qualité | Great Expectations (profil léger) |
| Visualisation | Streamlit, Plotly |
| Conteneurs | Docker Compose (profils `infra`, `apps`, `full`, `ci`) |

## Prérequis

- **Docker** et **Docker Compose** (v2).
- **Python 3.11+** (pour `make bootstrap` via `.venv`).
- **Make**, **Git**.
- **Réseau** : accès PyPI pour la première installation locale ; le build Docker Airflow peut utiliser des wheels embarquées si PyPI est indisponible dans l’image.
- Optionnel : compte [Kaggle](https://www.kaggle.com/docs/api) pour PaySim / MoMTSim complets.

## Démarrage rapide

Chemin recommandé en local (infra Docker + consumer/producer Python, sans rebuild des apps Docker) :

```bash
git clone <url-du-repo> MoMoShield && cd MoMoShield
cp .env.example .env   # adapter si besoin
make bootstrap
```

`make bootstrap` :

1. Monte Kafka + Postgres (profil `infra`).
2. Peut démarrer Airflow (`START_AIRFLOW=1` par défaut).
3. Applique le schéma staging / quarantaine.
4. Lance le consumer et le producteur (mode hybride).
5. Consolidation bronze → Postgres, **dbt seed + run**, Streamlit sur le port 8501.

Arrêt des processus locaux (consumer, producteur, Streamlit) :

```bash
make bootstrap-stop
```

Stack applicative entièrement Docker (build des images Python) :

```bash
make up    # équivalent make up-apps
```

Si le build Docker échoue (DNS, proxy), **`make bootstrap` suffit** pour le pipeline data et le dashboard.

## Accès aux services

| Service | URL | Identifiants (défaut local) |
|---------|-----|---------------------------|
| **Streamlit** | http://localhost:8501 | Aucun |
| **Airflow** | http://localhost:8088 | `admin` / `admin` |
| **Postgres** | `localhost:15432` | `momoshield` / `momoshield_dev`, base `momoshield` |
| **Kafka** | `localhost:9092` | Topics : `transactions.raw`, `transactions.alerts`, `transactions.dlq` |
| **Schema Registry** | http://localhost:8081 | — |

Variables utiles : `DATABASE_URL=postgresql://momoshield:momoshield_dev@localhost:15432/momoshield`, `KAFKA_BOOTSTRAP=localhost:9092`.

Airflow seul (Kafka déjà up) :

```bash
make up-airflow
```

Profil complet (Spark + Airflow, build lourd) :

```bash
make up-full
```

## Structure du dépôt

```text
MoMoShield/
├── producer/              # Producteur Kafka (synthetic, hybrid, paysim, …)
├── streaming/             # Consumer, règles fraude
├── momoshield/            # Logique batch, contrats, transforms, qualité
├── airflow/dags/          # DAGs Airflow
├── dbt/                   # Projet dbt (models, seeds, tests)
├── dashboards/            # Application Streamlit
├── scripts/               # bootstrap, schéma, CI, imports références
├── data/                  # bronze, staging, références (gitignoré en partie)
├── docker/                # Dockerfiles
├── docs/                  # Architecture, dictionnaires, SLO, sources
└── tests/                 # Unitaires, intégration, validation DAGs
```

## Commandes Make

| Commande | Description |
|----------|-------------|
| `make bootstrap` | Stack locale complète (recommandé) — stoppe les orphelins avant redémarrage |
| `make bootstrap-stop` | Arrêt consumer / producteur / Streamlit (PID + orphelins du repo) |
| `make up-infra` | Kafka + Postgres uniquement |
| `make up-airflow` | Airflow web + scheduler (port 8088) |
| `make producer-hybrid` | Producteur hybride via `.venv` |
| `make up` / `make up-apps` | Infra + apps Docker (build) |
| `make up-full` | Profil `full` (Airflow, Spark, …) |
| `make down` | Arrêt des conteneurs Compose |
| `make apply-staging-schema` | SQL staging / quarantaine sur Postgres |
| `make import-references` | Métadonnées GSMA / références |
| `make ci` | Pipeline CI P0–P4 (image Docker) |
| `make ci-full` | CI + tests d’intégration |

Producteur manuel après infra :

```bash
export KAFKA_BOOTSTRAP=localhost:9092
.venv/bin/python -m producer.main --mode hybrid --rate 500
```

## Orchestration Airflow

| DAG | Rôle |
|-----|------|
| `daily_consolidation` | Bronze → Postgres (staging) |
| `dbt_transformations` | Exécution dbt (à enrichir pour prod) |
| `data_quality_checks` | Contrôles GE sur staging |
| `fraud_evaluation` | Métriques d’évaluation fraude |
| `maintenance` | Entretien hebdomadaire |

Schéma batch : `scripts/apply_staging_schema.sh`, puis DAGs ci-dessus ; en local, `make bootstrap` et `dbt run` couvrent déjà l’essentiel.

## Sources de données

| Source | Usage |
|--------|--------|
| Générateur Togo | `--mode synthetic` |
| **Mode hybrid (défaut)** | Togo + échantillon PaySim + scénarios MoMTSim |
| PaySim | Échantillon en test ; jeu complet via Kaggle |
| MoMTSim | `make download-momtsim` |
| GSMA, AMLSim, AI4FCF | `make import-references` |

Détails : [docs/data-sources.md](docs/data-sources.md), conformité CDC : [docs/sources-cdc-compliance.md](docs/sources-cdc-compliance.md).

### PaySim (optionnel)

1. Configurer l’API Kaggle (`~/.kaggle/kaggle.json`).
2. `make download-paysim` ou `make ingest-paysim-zip`.
3. Rejeu : `.venv/bin/python -m producer.main --mode paysim --rate 1000 --loop`

Limites et citation : [docs/paysim-limits.md](docs/paysim-limits.md).

> Lopez-Rojas, Elmir & Axelsson, *PaySim: A financial mobile money simulator for fraud detection*, EMSS 2016.

## Tests et qualité

```bash
python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"
export PYTHONPATH=.
.venv/bin/pytest tests/unit --cov=streaming/rules --cov-fail-under=70
.venv/bin/python -m momoshield.contracts.validate
.venv/bin/python -m tests.validate_dags
```

Lint (conteneur CI) : `make lint-fix`.

## Documentation

| Document | Contenu |
|----------|---------|
| [docs/architecture.md](docs/architecture.md) | Vue d’ensemble des couches |
| [docs/data-dictionary.md](docs/data-dictionary.md) | Dictionnaire technique |
| [docs/dictionnaire-colonnes-fr.md](docs/dictionnaire-colonnes-fr.md) | Colonnes métier (FR) |
| [docs/transformation-policy.md](docs/transformation-policy.md) | Politique de transformation |
| [docs/slo.md](docs/slo.md) | Objectifs de service |
| [docs/portfolio-fiche.md](docs/portfolio-fiche.md) | Résumé vitrine / entretien |

## Licence des données

- **Code du dépôt** : à définir par l’auteur (fichier `LICENSE` à ajouter si publication open source).
- **PaySim** : respecter la licence Kaggle ; ne pas redistribuer le CSV complet sans autorisation. Le dépôt inclut un **échantillon** sous `tests/data/`.
- Autres jeux de référence : voir métadonnées dans `data/references/` après `make import-references`.

---