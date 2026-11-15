.PHONY: up up-infra up-apps down ci ci-full lint-fix test-integration download-paysim download-momtsim ingest-paysim-zip ingest-momtsim-zip import-references import-all sources-status apply-staging-schema paysim-replay producer-hybrid bootstrap bootstrap-stop streamlit up-airflow

PYTHON ?= .venv/bin/python
KAFKA_BOOTSTRAP ?= localhost:9092
PRODUCER_RATE ?= 500

bootstrap:
	chmod +x scripts/bootstrap_local.sh scripts/bootstrap_stop.sh
	./scripts/bootstrap_local.sh

bootstrap-stop:
	chmod +x scripts/bootstrap_stop.sh
	./scripts/bootstrap_stop.sh

streamlit:
	chmod +x scripts/run_streamlit.sh
	./scripts/run_streamlit.sh

up-airflow:
	docker compose --profile infra --profile full up -d --build \
		airflow-init airflow-webserver airflow-scheduler

apply-staging-schema:
	chmod +x scripts/apply_staging_schema.sh
	./scripts/apply_staging_schema.sh

import-all: import-references

sources-status:
	@test -f data/references/sources_inventory.json || $(MAKE) import-references
	@PYTHONPATH=. python3 -c "import json; d=json.load(open('data/references/sources_inventory.json')); s=d.get('cdc_sources',{}); print(json.dumps({k:v.get('status') for k,v in s.items()}, indent=2)); print('pipeline:', d.get('pipeline_primary_ready'))"

setup-kaggle:
	chmod +x scripts/kaggle_cli.sh
	.venv/bin/pip install -q "kaggle>=1.6" six
	@test -f $$HOME/.kaggle/kaggle.json || (echo "Manque ~/.kaggle/kaggle.json — voir scripts/kaggle_cli.sh"; exit 1)

download-momtsim:
	chmod +x scripts/download_momtsim.sh scripts/kaggle_cli.sh
	./scripts/download_momtsim.sh

ingest-momtsim-zip:
	chmod +x scripts/ingest_momtsim_zip.sh
	./scripts/ingest_momtsim_zip.sh

import-references:
	chmod +x scripts/import_reference_data.sh
	./scripts/import_reference_data.sh

ingest-paysim-zip:
	chmod +x scripts/ingest_paysim_zip.sh
	./scripts/ingest_paysim_zip.sh

download-paysim:
	chmod +x scripts/download_paysim.sh
	./scripts/download_paysim.sh

# Infra seule (images officielles, sans pip build — Postgres port 15432)
up-infra:
	docker compose --profile infra up -d

# Apps Python (build Docker ; nécessite DNS vers PyPI) — infra incluse pour depends_on postgres/kafka
up-apps:
	docker compose --profile infra --profile apps up -d --build

# Producteur local (après make up-infra) — pas de commande `python` système requise
producer-hybrid:
	PYTHONPATH=. KAFKA_BOOTSTRAP=$(KAFKA_BOOTSTRAP) $(PYTHON) -m producer.main --mode hybrid --rate $(PRODUCER_RATE)

up:
	docker compose --profile infra --profile apps up -d --build

# Équivalent historique sans rebuild si images déjà présentes
up-nobuild:
	docker compose --profile infra --profile apps up -d

up-full:
	docker compose --profile full up -d --build

down:
	docker compose --profile infra --profile apps --profile full --profile ci down

ci:
	docker compose --profile ci run --rm ci

ci-full:
	RUN_INTEGRATION=1 docker compose --profile ci run --rm -e RUN_INTEGRATION=1 ci

lint-fix:
	docker compose --profile ci run --rm ci ruff format .

test-integration:
	docker compose --profile core up -d
	RUN_INTEGRATION=1 pytest tests/integration -m integration -q