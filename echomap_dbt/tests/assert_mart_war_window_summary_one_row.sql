select *
from (
    select count(*)::bigint as n from {{ ref('mart_war_window_summary') }}
) x
where x.n <> 1
