{% macro nullif_blank(column_expr) %}
    nullif(trim({{ column_expr }}), '')
{% endmacro %}

{% macro amount_fcfa_bucket(amount_expr) %}
    case
        when {{ amount_expr }} < 10000 then 'moins_10k'
        when {{ amount_expr }} < 100000 then '10k_100k'
        when {{ amount_expr }} < 500000 then '100k_500k'
        else 'plus_500k'
    end
{% endmacro %}