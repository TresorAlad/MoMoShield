# Brouillon LinkedIn

J’ai conçu **MoMoShield**, un pipeline data complet pour la surveillance de transactions Mobile Money (contexte togolais, données synthétiques).

Architecture Lambda : détection quasi temps réel (Kafka + streaming) et consolidation quotidienne (Airflow + dbt + qualité).

Objectifs : alertes sous 5 secondes, medallion bronze/silver/gold, plus de 10 contrôles qualité, CI reproductible dans Docker.

Code ouvert — démarrage en une commande `make up`.