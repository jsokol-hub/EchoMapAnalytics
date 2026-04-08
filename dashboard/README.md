# EchoMap dashboard (Streamlit)

Reads dbt **mart** tables from PostgreSQL (same database/schema where `dbt run` materializes marts).

## Setup

1. Build marts:

   ```bash
   cd echomap_dbt
   dbt run
   ```

2. Configure connection — copy `.env.example` to `.env` and set:

   - **`ECHOMAP_DBT_SCHEMA`** — target schema from your dbt profile (often `public` or a custom schema name).
   - Either **`DATABASE_URL`** (`postgresql+psycopg2://...`) or **`DB_HOST`**, **`DB_PORT`**, **`DB_NAME`**, **`DB_USER`**, **`DB_PASSWORD`**.

3. Install and run:

   ```bash
   cd dashboard
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   streamlit run app.py
   ```

Open the URL shown in the terminal (usually http://localhost:8501).

## Performance & tuning

- Data is loaded **once per cache window** (default **600s**) with **narrow SQL** and a **single DB session** — use env **`ECHOMAP_DASH_CACHE_SEC`** to change TTL.
- Locations: only the top **N** rows by `news_count` are fetched (**`ECHOMAP_DASH_LOC_LIMIT`**, default `350`).
- Long date ranges: the **hourly** heatmap switches to **weekly** rows when there are more than **45** distinct days in the filter.

## Tabs

- **Summary** — Russian narrative + KPI table from `mart_war_window_summary`, pies (sentiment / coordinate source), top categories (`mart_top_categories_period`). Describes the **full** dbt window (not sidebar dates).
- **Overview** — daily volume, share metrics, table.
- **Categories** — top categories in the selected date range.
- **Sentiment** — `mart_sentiment_daily` (stacked area, filtered dates).
- **Sources** — `mart_data_source_daily` and `mart_coordinate_source_daily` (stacked areas).
- **Hourly** — heatmap of news count by Israel date × hour.
- **Locations** — map + table (top *N* by `news_count`).

After pulling new marts, run **`dbt run`** (or `dbt run --select marts`) so Postgres has `mart_sentiment_daily`, `mart_data_source_daily`, `mart_coordinate_source_daily`, `mart_war_window_summary`, `mart_top_categories_period`.

Methodology: `echomap_dbt/docs/METHODOLOGY.md`.
