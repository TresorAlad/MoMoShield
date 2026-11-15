with tx as (
    select * from {{ ref('int_transactions_enriched') }}
),

alerts as (
    select * from {{ ref('stg_momoshield__alerts') }}
),

joined as (
    select
        tx.*,
        coalesce(agg.alert_count, 0) as alert_count,
        agg.max_rule_score,
        agg.regles_declenchees,
        map.famille_fraude_gsma,
        case
            when map.famille_fraude_gsma is not null
                then 'Typologie GSMA : ' || map.famille_fraude_gsma
            else null
        end as observation_typologie
    from tx
    left join (
        select
            tx_id,
            count(*) as alert_count,
            max(score) as max_rule_score,
            string_agg(distinct rule_id, ',' order by rule_id) as regles_declenchees,
            min(rule_id) as first_rule_id
        from alerts
        group by tx_id
    ) agg on tx.tx_id = agg.tx_id
    left join {{ ref('gsma_rule_map') }} map on map.rule_id = agg.first_rule_id
)

select * from joined