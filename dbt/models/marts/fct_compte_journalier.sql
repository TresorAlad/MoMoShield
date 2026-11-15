select
    event_date as date_evenement,
    account_id as compte_emetteur,
    count(*) as nb_transactions,
    sum(amount_fcfa) as montant_total_fcfa,
    sum(alert_count) as nb_alertes,
    bool_or(is_fraud_label) as est_fraude_reference,
    percentile_cont(0.5) within group (order by amount_fcfa) as montant_mediane_fcfa,
    'Médiane sur historique du jour — non utilisée pour imputer les transactions' as observation
from {{ ref('int_transactions_with_alerts') }}
group by event_date, account_id