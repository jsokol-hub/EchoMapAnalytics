with source as (

    select *
    from {{ source('geonews_v1', 'geonews_v1_0') }}

),

base as (

    select
        *,
        "timestamp" AT TIME ZONE 'UTC' as published_at
    from source

),

with_tz as (

    select
        *,
        published_at AT TIME ZONE 'Asia/Jerusalem' as published_at_il
    from base

),

cleaned as (

    select
        news_id,

        published_at,
        published_at_il,
        published_at_il::date as published_date_il,
        extract(hour from published_at_il) as published_hour_il,

        nullif(trim(message), '') as message,
        nullif(trim(translation_ru), '') as translation_ru,
        nullif(trim(translation_en), '') as translation_en,
        nullif(trim(translation_he), '') as translation_he,

        coalesce(
            nullif(trim(translation_en), ''),
            nullif(trim(translation_ru), ''),
            nullif(trim(translation_he), ''),
            nullif(trim(message), '')
        ) as analysis_text,

        nullif(trim(geoname), '') as geoname,
        nullif(trim(category), '') as category,
        nullif(trim(topics), '') as topics,
        nullif(trim(sentiment), '') as sentiment,

        signal_strength,

        nullif(trim(data_source), '') as data_source,
        nullif(trim(data_source_link), '') as data_source_link,
        nullif(trim(data_source_links), '') as data_source_links,
        source_count,

        case
            when nullif(trim(lat), '') ~ '^[-+]?[0-9]*\.?[0-9]+$'
                then cast(trim(lat) as numeric)
            else null
        end as lat_num,

        case
            when nullif(trim("long"), '') ~ '^[-+]?[0-9]*\.?[0-9]+$'
                then cast(trim("long") as numeric)
            else null
        end as lon_num,

        case
            when nullif(trim(wikilat), '') ~ '^[-+]?[0-9]*\.?[0-9]+$'
                then cast(trim(wikilat) as numeric)
            else null
        end as wikilat_num,

        case
            when nullif(trim(wikilong), '') ~ '^[-+]?[0-9]*\.?[0-9]+$'
                then cast(trim(wikilong) as numeric)
            else null
        end as wikilon_num,

        geom,
        wikigeom

    from with_tz

)

select
    news_id,

    published_at,
    published_at_il,
    published_date_il,
    published_hour_il,

    message,
    translation_ru,
    translation_en,
    translation_he,
    analysis_text,

    geoname,
    category,
    topics,
    sentiment,
    signal_strength,

    data_source,
    data_source_link,
    data_source_links,
    source_count,

    lat_num,
    lon_num,
    wikilat_num,
    wikilon_num,

    coalesce(lat_num, wikilat_num) as final_lat,
    coalesce(lon_num, wikilon_num) as final_lon,

    geom,
    wikigeom,
    coalesce(geom, wikigeom) as final_geom,

    case
        when lat_num is not null and lon_num is not null then 'parser'
        when wikilat_num is not null and wikilon_num is not null then 'wiki'
        else 'none'
    end as coordinate_source,

    case when message is not null then true else false end as has_message,
    case when geoname is not null then true else false end as has_geoname,
    case when lat_num is not null and lon_num is not null then true else false end as has_parser_coordinates,
    case when wikilat_num is not null and wikilon_num is not null then true else false end as has_wiki_coordinates,
    case
        when coalesce(lat_num, wikilat_num) is not null
         and coalesce(lon_num, wikilon_num) is not null
        then true
        else false
    end as has_final_coordinates

from cleaned