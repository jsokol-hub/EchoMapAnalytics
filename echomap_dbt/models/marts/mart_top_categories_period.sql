select
    category_clean,
    count(*) as news_count,
    count(*)::double precision
        / sum(count(*)) over () as share_of_total

from {{ ref('int_geonews_base') }}
group by 1
order by news_count desc
