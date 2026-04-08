# echomap_dbt

dbt project for the EchoMap wartime news analytics pipeline.

## Model lineage

```
source: geonews_v1.geonews_v1_0
        │
        ▼
  stg_geonews  (view)
        │
        ▼
  int_geonews_base  (view, analytics window filter)
        │
        ├──▶ mart_daily_news_volume      (table)
        ├──▶ mart_category_daily         (table)
        ├──▶ mart_hourly_activity        (table)
        ├──▶ mart_location_summary       (table)
        ├──▶ mart_sentiment_daily        (table)
        ├──▶ mart_data_source_daily      (table)
        ├──▶ mart_coordinate_source_daily (table)
        ├──▶ mart_war_window_summary     (table, 1 row)
        └──▶ mart_top_categories_period  (table)
```

## Usage

```bash
# Full build
dbt run

# Rebuild only marts (after changing mart SQL)
dbt run --select marts

# Run all tests
dbt test

# Run tests for a specific model
dbt test --select int_geonews_base
```

## Key design decisions

- **Staging is thin.** Renaming, type casting, timezone conversion, coordinate coalesce, and boolean quality flags only. No business logic.
- **Intermediate centralises logic.** `int_geonews_base` is the single source of truth for all marts — analytics window filtering, war day numbering, and dimension normalisation happen here.
- **Marts are aggregates.** Each mart serves one dashboard section. All materialised as tables for query speed.
- **Timezone handling.** Raw data is UTC. Staging converts to `timestamptz` and derives Israel local columns (`_il` suffix). All downstream models use `published_date_il` and `published_hour_il`.
- **Analytics window via vars.** `analytics_start_local` and `break_1_local` in `dbt_project.yml` control the time boundaries (Israel local time strings).

## Configuration

Edit `dbt_project.yml` to change the analytics window:

```yaml
vars:
  analytics_start_local: "2026-02-28 02:00:00"
  break_1_local: "2026-04-08 08:00:00"
```

## Tests

- **Schema tests**: `not_null`, `unique`, `accepted_values` on key columns (see `schema.yml` in each model directory).
- **Singular tests**: grain uniqueness assertions, war day positivity check, single-row validation for summary mart.

## Documentation

- [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md) — full methodology reference
- `schema.yml` files — column-level descriptions for every model
