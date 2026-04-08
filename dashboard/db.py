"""Postgres connection for the Streamlit dashboard."""

from __future__ import annotations

import os
import re
from functools import lru_cache
from urllib.parse import quote_plus

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError

load_dotenv()


def _schema() -> str:
    raw = os.environ.get("ECHOMAP_DBT_SCHEMA", "public").strip()
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", raw):
        raise ValueError("ECHOMAP_DBT_SCHEMA must be a simple Postgres identifier")
    return raw


@lru_cache(maxsize=1)
def get_engine():
    url = os.environ.get("DATABASE_URL")
    if url:
        return create_engine(
            url,
            pool_pre_ping=True,
            pool_size=2,
            max_overflow=2,
        )

    host = os.environ.get("DB_HOST", "localhost")
    port = os.environ.get("DB_PORT", "5432")
    name = os.environ.get("DB_NAME", "postgres")
    user = os.environ.get("DB_USER", "postgres")
    password = os.environ.get("DB_PASSWORD", "")
    pwd = quote_plus(password)
    conn = f"postgresql+psycopg2://{quote_plus(user)}:{pwd}@{host}:{port}/{quote_plus(name)}"
    return create_engine(
        conn,
        pool_pre_ping=True,
        pool_size=2,
        max_overflow=2,
    )


def table(name: str) -> str:
    sch = _schema()
    if not re.fullmatch(r"[a-z_][a-z0-9_]*", name):
        raise ValueError("Invalid table name")
    return f'"{sch}"."{name}"'


def read_df(sql: str, params: dict | None = None) -> pd.DataFrame:
    with get_engine().connect() as conn:
        return pd.read_sql(text(sql), conn, params=params or {})


def load_all_marts(location_limit: int = 350) -> dict[str, pd.DataFrame]:
    """
    One DB session, narrow selects. Fails fast if a mart table is missing (run dbt run).
    """
    lim = int(location_limit)
    if not (0 < lim <= 10_000):
        raise ValueError("location_limit must be between 1 and 10000")

    td = table("mart_daily_news_volume")
    tc = table("mart_category_daily")
    th = table("mart_hourly_activity")
    tl = table("mart_location_summary")
    ts = table("mart_sentiment_daily")
    tds = table("mart_data_source_daily")
    tcoord = table("mart_coordinate_source_daily")
    tw = table("mart_war_window_summary")
    ttop = table("mart_top_categories_period")

    sql_daily = f"""
        SELECT published_date_il, war_day_number, news_count, avg_signal_strength,
               high_signal_share, multi_source_share, with_coordinates_share
        FROM {td}
        ORDER BY published_date_il
    """
    sql_cat = f"""
        SELECT published_date_il, war_day_number, category_clean, news_count
        FROM {tc}
        ORDER BY published_date_il, category_clean
    """
    sql_hour = f"""
        SELECT published_date_il, published_hour_il, news_count
        FROM {th}
        ORDER BY published_date_il, published_hour_il
    """
    sql_loc = f"""
        SELECT geoname, final_lat, final_lon, coordinate_source, news_count
        FROM {tl}
        ORDER BY news_count DESC NULLS LAST
        LIMIT {lim}
    """
    sql_sent = f"""
        SELECT published_date_il, war_day_number, sentiment_clean, news_count,
               avg_signal_strength, high_signal_count
        FROM {ts}
        ORDER BY published_date_il, sentiment_clean
    """
    sql_dsrc = f"""
        SELECT published_date_il, war_day_number, data_source_clean, news_count,
               avg_signal_strength, high_signal_count
        FROM {tds}
        ORDER BY published_date_il, data_source_clean
    """
    sql_csrc = f"""
        SELECT published_date_il, war_day_number, coordinate_source, news_count, high_signal_count
        FROM {tcoord}
        ORDER BY published_date_il, coordinate_source
    """
    sql_summary = f"""
        SELECT total_news, first_date_il, last_date_il, min_war_day, max_war_day,
               calendar_days_span, distinct_news_days,
               avg_signal_strength, avg_signal_strength_nonnull,
               high_signal_share, multi_source_share, with_coordinates_share,
               with_geoname_share, with_message_share, raw_sentiment_present_share
        FROM {tw}
    """
    sql_top_cat = f"""
        SELECT category_clean, news_count, share_of_total
        FROM {ttop}
        ORDER BY news_count DESC
        LIMIT 30
    """

    out: dict[str, pd.DataFrame] = {}
    sch = _schema()
    try:
        with get_engine().connect() as conn:
            out["daily"] = pd.read_sql(text(sql_daily), conn)
            out["category"] = pd.read_sql(text(sql_cat), conn)
            out["hourly"] = pd.read_sql(text(sql_hour), conn)
            out["locations"] = pd.read_sql(text(sql_loc), conn)
            out["sentiment"] = pd.read_sql(text(sql_sent), conn)
            out["data_source"] = pd.read_sql(text(sql_dsrc), conn)
            out["coord_source"] = pd.read_sql(text(sql_csrc), conn)
            out["war_summary"] = pd.read_sql(text(sql_summary), conn)
            out["top_categories"] = pd.read_sql(text(sql_top_cat), conn)
    except ProgrammingError as e:
        err = str(e.orig) if getattr(e, "orig", None) else str(e)
        if "does not exist" in err:
            raise RuntimeError(
                f'Mart tables are missing in schema "{sch}". Set ECHOMAP_DBT_SCHEMA to match '
                "your dbt target `schema` in profiles.yml, or run `dbt run` in echomap_dbt "
                "against this database so marts are built in that schema."
            ) from e
        raise

    return out
