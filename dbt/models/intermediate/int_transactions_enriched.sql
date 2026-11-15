with base as (
    select * from {{ ref('stg_momoshield__transactions') }}
),

windows as (
    select
        *,
        count(*) over (
            partition by account_id, event_date
        ) as tx_count_1d,
        sum(amount_fcfa) over (
            partition by account_id, event_date
        ) as sum_amount_1d
    from base
)

select * from windows