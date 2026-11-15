"""
Job Spark Structured Streaming (profil full).
Exécution : spark-submit avec image docker spark (profil full).
"""

from __future__ import annotations

# Stub documenté : l'image Spark exécute ce module en production.
# Le consumer Python couvre le profil core avec la même logique de règles.

SPARK_README = """
1. readStream Kafka transactions.raw
2. withWatermark event_time 5 minutes
3. groupBy account_id + window 1 min / 5 min → agrégats
4. foreachBatch → RuleEngine + bronze MinIO + alerts topic
"""

if __name__ == "__main__":
    print(SPARK_README)