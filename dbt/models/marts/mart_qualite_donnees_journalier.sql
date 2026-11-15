with tx as (
    select * from {{ ref('stg_momoshield__transactions') }}
),

stats as (
    select
        event_date,
        count(*) as nb_lignes,
        avg(case when dest_id is null then 1.0 else 0.0 end) as taux_dest_null,
        avg(case when note_transformation is not null then 1.0 else 0.0 end) as taux_note_transformation,
        max(ingested_at) as derniere_ingestion
    from tx
    group by event_date
)

select
    event_date as date_evenement,
    nb_lignes,
    round(taux_dest_null::numeric, 4) as taux_valeurs_manquantes_dest,
    round(taux_note_transformation::numeric, 4) as taux_transformations_documentees,
    extract(epoch from (now() - derniere_ingestion)) / 3600.0 as fraicheur_heures,
    case
        when taux_dest_null > 0.4
            then 'Plus de 40 % dest_id null — vérifier types TRANSFER'
        else 'Qualité dans les seuils attendus'
    end as observation
from stats