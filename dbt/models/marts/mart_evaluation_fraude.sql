select
    event_date as date_evenement,
    sum(case when is_fraud_label and alert_count > 0 then 1 else 0 end) as vrais_positifs,
    sum(case when not is_fraud_label and alert_count > 0 then 1 else 0 end) as faux_positifs,
    sum(case when is_fraud_label and alert_count = 0 then 1 else 0 end) as faux_negatifs,
    sum(case when not is_fraud_label and alert_count = 0 then 1 else 0 end) as vrais_negatifs,
    case
        when sum(case when alert_count > 0 or is_fraud_label then 1 else 0 end) = 0
            then 0.0
        else round(
            sum(case when is_fraud_label and alert_count > 0 then 1.0 else 0 end)
            / nullif(sum(case when alert_count > 0 then 1 else 0 end), 0),
            4
        )
    end as precision,
    case
        when sum(case when is_fraud_label then 1 else 0 end) = 0
            then 0.0
        else round(
            sum(case when is_fraud_label and alert_count > 0 then 1.0 else 0 end)
            / nullif(sum(case when is_fraud_label then 1 else 0 end), 0),
            4
        )
    end as rappel,
    case
        when sum(case when not is_fraud_label then 1 else 0 end) = 0
            then 0.0
        else round(
            sum(case when not is_fraud_label and alert_count > 0 then 1.0 else 0 end)
            / nullif(sum(case when not is_fraud_label then 1 else 0 end), 0),
            4
        )
    end as taux_faux_positifs
from {{ ref('int_transactions_with_alerts') }}
group by event_date