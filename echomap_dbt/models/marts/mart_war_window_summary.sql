select
    count(*)::bigint as total_news,

    min(published_date_il) as first_date_il,
    max(published_date_il) as last_date_il,

    min(war_day_number) as min_war_day,
    max(war_day_number) as max_war_day,

    (max(published_date_il) - min(published_date_il) + 1) as calendar_days_span,
    count(distinct published_date_il) as distinct_news_days,

    avg(signal_strength) as avg_signal_strength,
    avg(signal_strength) filter (where signal_strength is not null) as avg_signal_strength_nonnull,

    sum(case when is_high_signal then 1 else 0 end)::double precision
        / nullif(count(*)::double precision, 0) as high_signal_share,

    sum(case when is_multi_source then 1 else 0 end)::double precision
        / nullif(count(*)::double precision, 0) as multi_source_share,

    sum(case when has_final_coordinates then 1 else 0 end)::double precision
        / nullif(count(*)::double precision, 0) as with_coordinates_share,

    sum(case when has_geoname then 1 else 0 end)::double precision
        / nullif(count(*)::double precision, 0) as with_geoname_share,

    sum(case when has_message then 1 else 0 end)::double precision
        / nullif(count(*)::double precision, 0) as with_message_share,

    sum(case when has_sentiment then 1 else 0 end)::double precision
        / nullif(count(*)::double precision, 0) as raw_sentiment_present_share

from {{ ref('int_geonews_base') }}
