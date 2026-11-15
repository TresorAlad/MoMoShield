# ADR 001 — Architecture Lambda (speed + batch)

## Contexte

Fraude à détecter en quasi temps réel tout en consolidant pour l'analytique quotidienne.

## Décision

- **Speed** : Kafka + consumer (Spark en profil `full`, Python en `core`).
- **Batch** : Airflow + dbt + Great Expectations sur bronze/silver/gold.

## Conséquences

- Même contrat `TransactionEvent` sur les deux chemins.
- Le batch réconcilie et n'écrase pas les alertes streaming.