with base as (

    select *
    from {{ ref('int_geonews_base') }}

),

agg as (

    select
        published_date_il,
        war_day_number,

        count(*) as news_count,

        avg(signal_strength) as avg_signal_strength,

        sum(case when is_high_signal then 1 else 0 end) as high_signal_count,
        sum(case when is_multi_source then 1 else 0 end) as multi_source_count,
        sum(case when has_final_coordinates then 1 else 0 end) as with_coordinates_count,

        count(distinct geoname) as unique_geonames_count,
        count(distinct data_source) as unique_sources_count

    from base
    group by 1, 2

)

select
    published_date_il,
    war_day_number,
    news_count,
    avg_signal_strength,
    high_signal_count,
    multi_source_count,
    with_coordinates_count,
    unique_geonames_count,
    unique_sources_count,

    high_signal_count::numeric / nullif(news_count, 0) as high_signal_share,
    multi_source_count::numeric / nullif(news_count, 0) as multi_source_share,
    with_coordinates_count::numeric / nullif(news_count, 0) as with_coordinates_share

from agg
order by published_date_il