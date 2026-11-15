with transfer_stats as (
    select
        count(*) filter (where dest_id is null) as null_dest,
        count(*) as total
    from {{ ref('stg_momoshield__transactions') }}
    where type = 'TRANSFER'
)

select 1 as failure
from transfer_stats
where total > 0
  and null_dest::numeric / total > 0.4