with base as (

    select *
    from {{ ref('int_geonews_base') }}
    where has_final_coordinates
      and geoname is not null

)

select
    geoname,
    final_lat,
    final_lon,
    final_geom,
    coordinate_source,

    count(*) as news_count,
    avg(signal_strength) as avg_signal_strength,
    sum(case when is_high_signal then 1 else 0 end) as high_signal_count,
    sum(case when is_multi_source then 1 else 0 end) as multi_source_count,

    min(published_at) as first_seen_at,
    max(published_at) as last_seen_at

from base
group by 1, 2, 3, 4, 5
order by news_count desc