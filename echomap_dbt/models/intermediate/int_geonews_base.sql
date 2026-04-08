with base as (

    select *
    from {{ ref('stg_geonews') }}

)

select
    news_id,
    published_at,
    published_at_il,
    published_date_il,
    published_hour_il,

    (
        published_date_il
        - ('{{ var("analytics_start_local") }}'::timestamp::date)
        + 1
    ) as war_day_number,

    message,
    geoname,

    category,
    coalesce(lower(trim(category)), 'unknown') as category_clean,

    topics,

    sentiment,
    case
        when lower(trim(sentiment)) = 'positive' then 'positive'
        when lower(trim(sentiment)) = 'negative' then 'negative'
        when lower(trim(sentiment)) in ('neutral', 'general') then 'neutral'
        when sentiment is null or trim(sentiment) = '' then 'unknown'
        else 'unknown'
    end as sentiment_clean,

    signal_strength,
    case
        when signal_strength >= 0.7 then true
        else false
    end as is_high_signal,

    data_source,
    coalesce(
        nullif(trim(split_part(data_source, ',', 1)), ''),
        'unknown'
    ) as data_source_clean,
    data_source_link,
    data_source_links,

    source_count,
    case
        when source_count > 1 then true
        else false
    end as is_multi_source,

    final_lat,
    final_lon,
    final_geom,
    coordinate_source,

    has_message,
    has_geoname,
    has_final_coordinates,

    case when category is not null then true else false end as has_category,
    case when sentiment is not null then true else false end as has_sentiment

from base
where published_at_il >= '{{ var("analytics_start_local") }}'::timestamp
  and published_at_il < '{{ var("break_1_local") }}'::timestamp
  -- исключаем ракетные оповещения (Цева Адом / Tzeva Adom / צבע אדום) и короткие перечисления населённых пунктов
  and not (
      coalesce(message, '') ilike '%цева адом%'
      or coalesce(translation_ru, '') ilike '%цева адом%'
      or coalesce(message, '') ilike '%tzeva adom%'
      or coalesce(translation_en, '') ilike '%tzeva adom%'
      or coalesce(message, '') ilike '%צבע אדום%'
      or coalesce(translation_he, '') ilike '%צבע אדום%'
      or coalesce(message, '') ilike '%צה"א אדום%'
      or coalesce(translation_he, '') ilike '%צה"א אדום%'
  )
  and not (
      length(coalesce(message, '')) <= 800
      and (
          length(coalesce(message, ''))
          - length(replace(coalesce(message, ''), ',', ''))
      ) >= 5
  )