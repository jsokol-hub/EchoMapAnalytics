# EchoMap — Methodology

Aligned with the dbt models `stg_geonews` → `int_geonews_base` → marts.
Update this file when SQL logic changes.

## Unit of observation

- **One news item = one row.**
- Identifier: **`news_id`** from the parser's source table (not a hash or surrogate key).
- `int_geonews_base`: at most one row per `news_id` inside the configured analytics window.

## Analytics window and war day

- Bounds set in **`dbt_project.yml`**: `analytics_start_local`, `break_1_local` — strings in **Israel local time** (wall-clock semantics).
- **`int_geonews_base`** keeps only rows where  
  `published_at_il >= analytics_start_local` and `published_at_il < break_1_local` (end is **exclusive**).
- **`war_day_number`**:  
  `published_date_il − date(analytics_start_local) + 1`.  
  Day **1** is the first Israel calendar day of the analytics window.

## Timezone

- Raw storage is **UTC** → staging produces **`published_at`** as `timestamptz`.
- For analytics we use **Asia/Jerusalem**:  
  **`published_at_il`** (wall-clock timestamp), **`published_date_il`** (calendar date), **`published_hour_il`** (0–23).
- Window boundary vars are compared against `published_at_il` directly.

## Coordinates

- **`final_lat`** / **`final_lon`**: `coalesce(parser_pair, wiki_pair)`.
- **`final_geom`**: `coalesce(geom, wikigeom)`.
- **`coordinate_source`**:
  - **parser** — full parser coordinate pair present.
  - **wiki** — no parser pair, but full wiki pair present.
  - **none** — no complete pair from either source.

## Credibility score (signal_strength)

- Source field: **`signal_strength`** (real, 0–1).
- Higher values indicate stronger evidence / more credible sourcing.
- **`is_high_signal`**: `true` if `signal_strength >= 0.7`, else `false` (including NULL).
- In the dashboard this is displayed as **"credibility score"** (not "signal strength").

## Multi-source

- Source field: **`source_count`** (integer).
- **`is_multi_source`**: `true` if `source_count > 1`, else `false`.

## Sentiment classification

- Raw `sentiment` field is normalised to **4 categories** in `int_geonews_base`:
  - `positive` — raw value is "positive"
  - `negative` — raw value is "negative"
  - `neutral` — raw value is "neutral" or "general"
  - `unknown` — NULL, empty, or any other value
- Column: **`sentiment_clean`**.

## Category normalisation

- **`category_clean`**: `lower(trim(category))`, NULL mapped to `'unknown'`.

## Data source normalisation

- Raw `data_source` field may contain **comma-separated lists** of channel names (when a news item appears in multiple sources).
- **`data_source_clean`**: extracts the **first (primary) source** from the list using `split_part(data_source, ',', 1)`, trimmed, NULL/empty mapped to `'unknown'`.

## Exclusion filters (int_geonews_base)

The intermediate model excludes:
1. **Rocket alert messages** (Tzeva Adom / צבע אדום) — detected via `ILIKE` patterns in message and translation fields.
2. **Short comma-heavy listings** — messages under 800 characters with 5+ commas (typically location lists from alert systems, not news).

## Marts

Built from **`int_geonews_base`** (same analytics window):

| Mart | Grain | Dashboard use |
|------|-------|---------------|
| `mart_daily_news_volume` | date | Daily count, avg credibility, quality shares |
| `mart_category_daily` | date × category | Category breakdown per day |
| `mart_hourly_activity` | date × hour | Heatmap of hourly activity (Israel time) |
| `mart_location_summary` | geoname | Location ranking with coordinates |
| `mart_sentiment_daily` | date × sentiment | Sentiment distribution per day |
| `mart_data_source_daily` | date × source | Primary data source per day |
| `mart_coordinate_source_daily` | date × coord_source | Coordinate pipeline (parser/wiki/none) per day |
| `mart_war_window_summary` | 1 row | Full-period aggregates for the summary narrative |
| `mart_top_categories_period` | category | Category ranking with share of total |

## Known data quality notes

- A sharp volume drop was observed around March 23, 2026 (~78% decrease). The exact cause is undetermined — it may reflect changes in the data collection pipeline, source channel activity, or real-world events. Metrics from approximately March 23 to April 2 should be interpreted with caution.
