select
    published_date_il,
    war_day_number,
    sentiment_clean,

    count(*) as news_count,
    avg(signal_strength) as avg_signal_strength,
    sum(case when is_high_signal then 1 else 0 end) as high_signal_count

from {{ ref('int_geonews_base') }}
group by 1, 2, 3
order by published_date_il, sentiment_clean
