# EchoMap — methodology (short)

Aligned with the dbt models `stg_geonews` → `int_geonews_base` → marts. Update this file when SQL logic changes.

## Unit of observation

- **One news item = one row.**
- Identifier: **`news_id`** from the parser’s source table (not a hash or surrogate key).
- Intermediate model **`int_geonews_base`**: at most one row per `news_id` inside the configured analytics window.

## Analytics window and “war day”

- Bounds are set in **`dbt_project.yml`**: `analytics_start_local`, `break_1_local` — strings in **Israel local time** (wall-clock semantics).
- **`int_geonews_base`** keeps only rows with  
  `published_at_il >= analytics_start_local` and `published_at_il < break_1_local` (end is **exclusive**).
- **`war_day_number`**:  
  `published_date_il − date(analytics_start_local) + 1`,  
  where `date(...)` is the calendar date from the same var string (`::timestamp::date`).  
  Day **1** is the first Israel calendar day relative to that start date.

## Time zone

- Raw storage is **UTC** → in staging **`published_at`** is `timestamptz`.
- For charts and day/hour breakdowns we use **Asia/Jerusalem**:  
  **`published_at_il`**, **`published_date_il`**, **`published_hour_il`**.
- Window boundaries are compared on **`published_at_il`** (same semantics as the var strings).

## Coordinates

- **`final_lat`** / **`final_lon`**: `coalesce` parser pair, then wiki pair:  
  parser `lat`/`lon`, else `wikilat`/`wikilong`.
- **`final_geom`**: `coalesce(geom, wikigeom)`.
- **`coordinate_source`**:  
  **parser** — full parser coordinate pair;  
  **wiki** — no full parser pair, but a full wiki pair;  
  **none** — otherwise (including mixed incomplete pairs).

## high_signal

- Source field: **`signal_strength`** (real).
- In int: **`is_high_signal = true`** if `signal_strength >= 0.7`, else **false** (including when NULL).

## multi_source

- Source field: **`source_count`** (integer).
- In int: **`is_multi_source = true`** if `source_count > 1`, else **false**.

## Marts (dashboard-facing)

Built from **`int_geonews_base`** (same analytics window):

| Mart | Use |
|------|-----|
| `mart_daily_news_volume` | Daily KPIs and quality shares |
| `mart_category_daily` | Category × day |
| `mart_hourly_activity` | Date × hour heatmap |
| `mart_location_summary` | Map / table by place + coordinates |
| `mart_sentiment_daily` | Sentiment × day |
| `mart_data_source_daily` | Source label × day |
| `mart_coordinate_source_daily` | parser/wiki/none × day |
| `mart_war_window_summary` | **One row** — full-window aggregates for narrative / KPIs |
| `mart_top_categories_period` | Category ranking + share of total over the window |

---

*Product next steps (outside this file): overview dashboard → geography → events/categories → expand methodology for publication.*
