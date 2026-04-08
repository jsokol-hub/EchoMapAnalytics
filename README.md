# EchoMap Analytics

Wartime news analytics pipeline and interactive dashboard for conflict coverage in Israel.

Built with **dbt** (data transformation) and **Streamlit** (visualisation), backed by PostgreSQL.

---

## Architecture

```
Source (PostgreSQL)          dbt (transform)                Dashboard (Streamlit)
┌──────────────────┐   ┌─────────────────────────┐   ┌──────────────────────────┐
│  geonews_v1_0    │──▶│  stg_geonews (view)     │   │  Summary                 │
│  (raw news rows) │   │         │                │   │  Timeline                │
└──────────────────┘   │  int_geonews_base (view) │──▶│  Hourly patterns         │
                       │         │                │   │  Geography               │
                       │  9 mart tables (tables)  │   │                          │
                       └─────────────────────────┘   └──────────────────────────┘
```

**Data flow:** `source` → `staging` → `intermediate` → `marts` → `dashboard`

| Layer | Purpose |
|-------|---------|
| **staging** | Rename, cast, timezone conversion (UTC → Asia/Jerusalem), coordinate normalisation, quality flags |
| **intermediate** | Analytics window filter (dbt vars), war day numbering, sentiment / category / data source normalisation, credibility and multi-source flags |
| **marts** | Aggregated tables optimised for dashboard queries (daily volume, categories, sentiment, hourly activity, geography, sources, full-period summary) |

## Project structure

```
EchoMapAnalytics/
├── echomap_dbt/              # dbt project
│   ├── dbt_project.yml       # project config + analytics window vars
│   ├── models/
│   │   ├── staging/          # stg_geonews
│   │   ├── intermediate/     # int_geonews_base
│   │   └── marts/            # 9 mart models
│   ├── tests/                # singular data tests
│   └── docs/METHODOLOGY.md   # methodology reference
│
├── dashboard/                # Streamlit app
│   ├── app.py                # main dashboard (4 tabs)
│   ├── db.py                 # PostgreSQL connection + data loading
│   ├── i18n.py               # EN/RU internationalisation
│   ├── narrative.py          # bilingual summary narrative
│   ├── requirements.txt      # Python dependencies
│   └── .env.example          # connection template
│
└── README.md                 # this file
```

## Quick start

### Prerequisites

- PostgreSQL with the `geonews_v1.geonews_v1_0` source table populated
- Python 3.10+
- dbt-core with dbt-postgres adapter

### 1. Configure dbt

```bash
cd echomap_dbt

# Set up your ~/.dbt/profiles.yml with a profile named echomap_dbt
# pointing to your PostgreSQL instance.

dbt deps        # install packages (if any)
dbt run         # build all models
dbt test        # validate data quality
```

### 2. Run the dashboard

```bash
cd dashboard
cp .env.example .env
# Edit .env — set ECHOMAP_DBT_SCHEMA and DB credentials

python -m venv .venv
.venv/Scripts/activate        # Windows
# source .venv/bin/activate   # macOS / Linux

pip install -r requirements.txt
streamlit run app.py
```

Open http://localhost:8501.

## Dashboard

Four tabs, bilingual (EN / RU toggle in the sidebar):

| Tab | Content |
|-----|---------|
| **Summary** | Full-period narrative, KPIs, sentiment and coordinate source pies, top categories |
| **Timeline** | Daily volume with anomaly detection, quality indicators, categories bar, sentiment and source area charts |
| **Hourly patterns** | Hour × date heatmap, average hourly distribution |
| **Geography** | Interactive scatter map (OpenStreetMap), location table |

### Configuration (env vars)

| Variable | Default | Description |
|----------|---------|-------------|
| `ECHOMAP_DBT_SCHEMA` | `public` | PostgreSQL schema where dbt materialises marts |
| `DATABASE_URL` | — | Full connection string (alternative to individual vars) |
| `DB_HOST` / `DB_PORT` / `DB_NAME` / `DB_USER` / `DB_PASSWORD` | localhost defaults | Individual connection parameters |
| `ECHOMAP_DASH_CACHE_SEC` | `600` | Data cache TTL in seconds |
| `ECHOMAP_DASH_LOC_LIMIT` | `350` | Max location rows fetched from DB |

## dbt models

### Staging

| Model | Description |
|-------|-------------|
| `stg_geonews` | Cleans raw data: renames columns, casts types, converts UTC → Israel time, normalises coordinates, adds quality flags |

### Intermediate

| Model | Description |
|-------|-------------|
| `int_geonews_base` | Central fact table — filters to analytics window, adds `war_day_number`, normalises `sentiment_clean`, `category_clean`, `data_source_clean`, credibility and multi-source flags |

### Marts

| Model | Grain | Description |
|-------|-------|-------------|
| `mart_daily_news_volume` | date | Daily count, avg credibility, quality shares |
| `mart_category_daily` | date × category | News count per category per day |
| `mart_hourly_activity` | date × hour | News count per hour (Israel time) |
| `mart_location_summary` | geoname | Location ranking with coordinates |
| `mart_sentiment_daily` | date × sentiment | Sentiment breakdown per day |
| `mart_data_source_daily` | date × source | Primary data source per day |
| `mart_coordinate_source_daily` | date × coord_source | Coordinate pipeline (parser/wiki/none) per day |
| `mart_war_window_summary` | 1 row | Full-period aggregates for the summary narrative |
| `mart_top_categories_period` | category | Category ranking with share of total |

## Analytics window

Configured in `echomap_dbt/dbt_project.yml`:

```yaml
vars:
  analytics_start_local: "2026-02-28 02:00:00"   # Israel local time
  break_1_local: "2026-04-08 08:00:00"
```

All timestamps in the pipeline use **Asia/Jerusalem** local time for display and filtering.

## Methodology

See [`echomap_dbt/docs/METHODOLOGY.md`](echomap_dbt/docs/METHODOLOGY.md) for detailed documentation on:
- Unit of observation
- Timezone handling
- Coordinate normalisation
- Credibility scoring
- Sentiment classification
- War day numbering

## License

This project is provided for educational and analytical purposes.
