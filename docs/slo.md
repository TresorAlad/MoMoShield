# Objectifs de niveau de service (SLO)

Voir `momoshield/metrics/slo.py` pour l'enregistrement des mesures.

| SLI | Cible v1 | Source |
|-----|----------|--------|
| Débit simulateur | 1000 evt/s (profil full) | Producer → `meta.sli_samples` |
| Latence détection p95 | < 5 s | Alertes vs `event_time` |
| Consumer lag | < 10k (dev) | Métrique supervision |
| Fraîcheur gold | J+0 après DAG 02:00 | GE freshness |
| DLQ rate | < 0,1 % | Compteur ingress |