-- Alias compatibilité : délègue au mart français
select * from {{ ref('mart_fraude_par_dimensions') }}