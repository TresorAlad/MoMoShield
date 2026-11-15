select
    {{ colonnes_transaction_fr() }},
    amount_fcfa_bucket as tranche_montant_fcfa
from {{ ref('stg_momoshield__transactions') }}