# Architecture MoMoShield

![Schéma d’architecture](architecture-momoshield.jpg)

Voir aussi le diagramme Mermaid dans le [README](../README.md#architecture). Fichier portfolio : `architecture-momoshield.jpg` (source locale possible : `linkedin/architecture.jpg`, non versionnée).

Couches :

1. Producteurs → Kafka (`transactions.raw`)
2. Streaming → alertes + bronze NDJSON
3. Airflow → silver PostgreSQL → dbt gold
4. Great Expectations → `meta.ge_validation_runs`
5. Streamlit → consommation