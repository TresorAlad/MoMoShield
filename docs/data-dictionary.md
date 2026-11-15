# Dictionnaire de données — MoMoShield

## TransactionEvent (`transaction_v1`)

| Champ | Type | Description | Règles |
|-------|------|-------------|--------|
| `tx_id` | string | Identifiant unique transaction | Clé métier, idempotence |
| `account_id` | string | Compte émetteur | Clé partition Kafka |
| `dest_id` | string? | Compte destinataire | Optionnel selon type |
| `type` | enum | Type d'opération Mobile Money | Voir `cities_operators.yaml` |
| `amount_fcfa` | decimal | Montant en FCFA (synthétique) | > 0 |
| `operator` | enum | Opérateur togolais | MOOV_MONEY, MIXX_BY_YAS |
| `city` | string | Ville de l'opération | Liste configurée |
| `sim_id` | string | SIM utilisée | Requis pour R3 |
| `event_time` | datetime UTC | Horodatage événement | Watermark Spark |
| `is_fraud_label` | boolean | Vérité terrain synthétique | **Évaluation uniquement** |

### Champs PaySim / MoMTSim interdits (fuite label)

Ne jamais utiliser comme features de détection : soldes avant/après (`oldbalanceOrg`, `newbalanceOrig`, `oldBalInitiator`, `newBalRecipient`, etc.) ni `isFraud` brut — uniquement `is_fraud_label` pour l’évaluation.

## FraudAlert (`fraud_alert_v1`)

| Champ | Type | Description |
|-------|------|-------------|
| `alert_id` | string | Identifiant alerte |
| `tx_id` | string | Transaction liée |
| `account_id` | string | Compte concerné |
| `rule_id` | string | R1–R6 |
| `score` | float | Score 0–1 |
| `context` | object | Détails règle |
| `detected_at` | datetime UTC | Moment détection |

Dédup : (`tx_id`, `rule_id`).

## SLO (indicatifs)

| SLI | Cible |
|-----|-------|
| Latence détection p95 | < 5 s |
| Débit ingress (full) | ≥ 1000 evt/s |
| Taux DLQ | < 0,1 % |