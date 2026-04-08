# EchoMap Dashboard

Interactive Streamlit dashboard for visualising dbt mart tables.

## Features

- **4 tabs**: Summary, Timeline, Hourly patterns, Geography
- **Bilingual**: EN / RU toggle in the sidebar (all labels, tooltips, chart titles, narratives)
- **Anomaly detection**: automatic annotation of sharp volume drops on the daily chart
- **Interactive map**: scatter map (OpenStreetMap) with bubble sizing by news count
- **Smart caching**: single DB session, narrow SELECTs, configurable TTL

## Setup

1. **Build dbt marts** (from the repo root):

   ```bash
   cd echomap_dbt
   dbt run
   ```

2. **Configure connection**:

   ```bash
   cd dashboard
   cp .env.example .env
   # Edit .env — set schema and credentials
   ```

3. **Install and run**:

   ```bash
   python -m venv .venv
   .venv/Scripts/activate          # Windows
   # source .venv/bin/activate     # macOS / Linux

   pip install -r requirements.txt
   streamlit run app.py
   ```

   Open http://localhost:8501.

## Tabs

| Tab | Data sources | What it shows |
|-----|-------------|---------------|
| **Summary** | `mart_war_window_summary`, `mart_top_categories_period`, `mart_sentiment_daily`, `mart_coordinate_source_daily` | Full-period overview: narrative, KPIs, sentiment and coordinate pies, top categories table |
| **Timeline** | `mart_daily_news_volume`, `mart_category_daily`, `mart_sentiment_daily`, `mart_data_source_daily`, `mart_coordinate_source_daily` | Day-by-day dynamics: volume line, quality indicators, categories bar, sentiment/source area charts |
| **Hourly patterns** | `mart_hourly_activity` | Heatmap (hour x date), average hourly bar chart |
| **Geography** | `mart_location_summary` | Interactive scatter map, location table |

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ECHOMAP_DBT_SCHEMA` | `public` | Schema where dbt materialises mart tables |
| `DATABASE_URL` | — | Full SQLAlchemy connection string |
| `DB_HOST` | `localhost` | PostgreSQL host |
| `DB_PORT` | `5432` | PostgreSQL port |
| `DB_NAME` | `postgres` | Database name |
| `DB_USER` | `postgres` | Database user |
| `DB_PASSWORD` | — | Database password |
| `ECHOMAP_DASH_CACHE_SEC` | `600` | Data cache TTL (seconds) |
| `ECHOMAP_DASH_LOC_LIMIT` | `350` | Max location rows fetched |

## File structure

| File | Role |
|------|------|
| `app.py` | Main dashboard — layout, tabs, charts, annotations |
| `db.py` | PostgreSQL connection, pooling, data loading |
| `i18n.py` | EN/RU translations, tooltips, column renames, formatters |
| `narrative.py` | Bilingual summary narrative generator |
| `requirements.txt` | Python dependencies |
| `.env.example` | Connection template |
| `.streamlit/config.toml` | Streamlit theme and performance settings |
