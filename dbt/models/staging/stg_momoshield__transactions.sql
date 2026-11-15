with source as (
    select * from {{ source('momoshield', 'stg_transactions') }}
),

cleaned as (
    select
        tx_id,
        trim(account_id) as account_id,
        {{ nullif_blank('dest_id') }} as dest_id,
        upper(trim(type)) as type,
        cast(amount_fcfa as numeric(18, 2)) as amount_fcfa,
        upper(trim(operator)) as operator,
        trim(city) as city,
        trim(sim_id) as sim_id,
        cast(event_time as timestamptz) as event_time,
        coalesce(event_date, cast(event_time as date)) as event_date,
        coalesce(is_fraud_label, false) as is_fraud_label,
        trim(lower(source_system)) as source_system,
        note_transformation,
        ingested_at,
        extract(hour from cast(event_time as timestamptz) at time zone 'UTC')::int as event_hour_utc,
        case
            when extract(dow from cast(event_time as timestamptz)) in (0, 6) then true
            else false
        end as is_weekend,
        {{ amount_fcfa_bucket('cast(amount_fcfa as numeric(18, 2))') }} as amount_fcfa_bucket
    from source
    where amount_fcfa > 0
)

select * from cleaned