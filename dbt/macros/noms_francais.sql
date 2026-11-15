{% macro colonnes_transaction_fr(prefix='') %}
    {{ prefix }}tx_id as identifiant_transaction,
    {{ prefix }}account_id as compte_emetteur,
    {{ prefix }}dest_id as compte_destinataire,
    {{ prefix }}type as type_operation_code,
  {{ type_operation_libelle(prefix ~ 'type') }} as type_operation,
    {{ prefix }}amount_fcfa as montant_fcfa,
    {{ prefix }}operator as operateur,
    {{ prefix }}city as ville,
    {{ prefix }}sim_id as identifiant_sim,
    {{ prefix }}event_time as horodatage_evenement,
    {{ prefix }}event_date as date_evenement,
    {{ prefix }}event_hour_utc as heure_utc,
    {{ prefix }}is_fraud_label as est_fraude_reference,
    {{ prefix }}is_weekend as est_week_end,
    {{ prefix }}source_system as source_donnee,
    {{ prefix }}note_transformation as note_transformation
{% endmacro %}