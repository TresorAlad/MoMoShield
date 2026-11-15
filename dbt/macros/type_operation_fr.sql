{% macro type_operation_libelle(type_column) %}
    case upper(trim({{ type_column }}))
        when 'CASH_IN' then 'depot'
        when 'CASH_OUT' then 'retrait'
        when 'TRANSFER' then 'transfert'
        when 'PAYMENT' then 'paiement'
        when 'DEBIT' then 'debit'
        else lower(trim({{ type_column }}))
    end
{% endmacro %}