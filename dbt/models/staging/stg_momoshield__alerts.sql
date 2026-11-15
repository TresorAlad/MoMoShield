select
    alert_id,
    tx_id,
    account_id,
    rule_id,
    score,
    context,
    cast(detected_at as timestamptz) as detected_at,
    coalesce(event_date, cast(detected_at as date)) as event_date
from {{ source('momoshield', 'stg_alerts') }}