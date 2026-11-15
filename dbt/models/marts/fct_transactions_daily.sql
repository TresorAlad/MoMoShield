select
    event_date as date_evenement,
    count(*) as nombre_transactions,
    sum(amount_fcfa) as montant_total_fcfa,
    sum(case when is_fraud_label then 1 else 0 end) as nombre_fraudes_label
from {{ ref('int_transactions_with_alerts') }}
group by event_date