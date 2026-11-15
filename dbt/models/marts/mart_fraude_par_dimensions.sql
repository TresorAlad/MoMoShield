select
    event_date as date_evenement,
    city as ville,
    operator as operateur,
    {{ type_operation_libelle('type') }} as type_operation,
    count(*) as nombre_transactions,
    sum(case when is_fraud_label then 1 else 0 end) as nombre_fraudes_label,
    sum(alert_count) as nombre_alertes,
    case
        when sum(alert_count) > 10
            then 'Volume d alertes élevé — vérifier règles R1–R6'
        else null
    end as observation_metier
from {{ ref('int_transactions_with_alerts') }}
group by event_date, city, operator, type