"""
Data loading module — supports PostgreSQL (with SSH tunnel) and CSV fallback.
Adapted for the geonews schema: timestamp, message, geoname, lat, long,
category, data_source, translations (ru/en/he), news_id.
"""

import logging
from pathlib import Path
from contextlib import contextmanager

import pandas as pd
from sqlalchemy import create_engine, inspect

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import PG_CONFIG, SSH_CONFIG, CSV_DATA_PATH

logger = logging.getLogger(__name__)

COLUMN_MAP = {
    "timestamp": "date",
    "message": "text",
    "geoname": "location",
    "data_source": "channel",
    "translation_ru": "text_ru",
    "translation_en": "text_en",
    "translation_he": "text_he",
    "news_id": "id",
}

_active_tunnel = None


def _start_ssh_tunnel():
    """Create and start an SSH tunnel to the remote PostgreSQL server."""
    global _active_tunnel

    if _active_tunnel and _active_tunnel.is_active:
        return _active_tunnel.local_bind_port

    from sshtunnel import SSHTunnelForwarder

    ssh_kwargs = {
        "ssh_address_or_host": (SSH_CONFIG["host"], SSH_CONFIG["port"]),
        "ssh_username": SSH_CONFIG["user"],
        "remote_bind_address": (PG_CONFIG["host"], PG_CONFIG["remote_port"]),
    }

    if SSH_CONFIG["key_path"]:
        key_path = Path(SSH_CONFIG["key_path"])
        if key_path.exists():
            ssh_kwargs["ssh_pkey"] = str(key_path)
            logger.info(f"Using SSH key: {key_path}")
        else:
            logger.warning(f"SSH key not found at {key_path}, trying password auth")

    if SSH_CONFIG["password"]:
        ssh_kwargs["ssh_password"] = SSH_CONFIG["password"]

    logger.info(f"Opening SSH tunnel to {SSH_CONFIG['host']}:{SSH_CONFIG['port']} → "
                f"{PG_CONFIG['host']}:{PG_CONFIG['remote_port']}")

    tunnel = SSHTunnelForwarder(**ssh_kwargs)
    tunnel.start()
    _active_tunnel = tunnel

    local_port = tunnel.local_bind_port
    logger.info(f"SSH tunnel established: localhost:{local_port} → "
                f"{PG_CONFIG['host']}:{PG_CONFIG['remote_port']}")
    return local_port


def _stop_ssh_tunnel():
    """Stop the SSH tunnel if active."""
    global _active_tunnel
    if _active_tunnel and _active_tunnel.is_active:
        _active_tunnel.stop()
        _active_tunnel = None
        logger.info("SSH tunnel closed")


def get_pg_engine():
    """Create SQLAlchemy engine, with SSH tunnel if configured."""
    if SSH_CONFIG["enabled"]:
        local_port = _start_ssh_tunnel()
        host = "127.0.0.1"
        port = local_port
    else:
        host = PG_CONFIG["host"]
        port = PG_CONFIG["port"]

    url = (
        f"postgresql://{PG_CONFIG['user']}:{PG_CONFIG['password']}"
        f"@{host}:{port}/{PG_CONFIG['database']}"
    )
    return create_engine(url)


def discover_schema(engine) -> dict:
    """Auto-discover tables and columns in the database."""
    inspector = inspect(engine)
    schema = {}
    for table in inspector.get_table_names():
        columns = [col["name"] for col in inspector.get_columns(table)]
        schema[table] = columns
    return schema


def load_from_csv(path: str = None) -> pd.DataFrame:
    """Load data from the geonews CSV format."""
    csv_path = Path(path or CSV_DATA_PATH)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    df = pd.read_csv(csv_path, parse_dates=["timestamp"])
    return _normalize_dataframe(df)


def load_from_postgres(table_name: str = None, query: str = None) -> pd.DataFrame:
    """Load data from PostgreSQL (via SSH tunnel if enabled)."""
    engine = get_pg_engine()

    if query:
        df = pd.read_sql(query, engine)
    elif table_name:
        df = pd.read_sql(f'SELECT * FROM "{table_name}"', engine)
    elif PG_CONFIG.get("table_name"):
        df = pd.read_sql(f'SELECT * FROM "{PG_CONFIG["table_name"]}"', engine)
    else:
        df = pd.read_sql('SELECT * FROM geonews_v1.geonews_v1_0', engine)

    logger.info(f"Loaded {len(df)} rows from PostgreSQL")
    return _normalize_dataframe(df)


def _pick_best_table(schema: dict) -> str:
    """Pick the table most likely to contain messages."""
    priority = ["geonews", "messages", "news", "posts", "telegram_messages", "tg_messages"]
    for name in priority:
        for table in schema:
            if name in table.lower():
                return table
    return max(schema.items(), key=lambda x: len(x[1]))[0]


def _normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize DataFrame to standard column names."""
    rename_map = {k: v for k, v in COLUMN_MAP.items() if k in df.columns}
    df = df.rename(columns=rename_map)

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce", utc=True)
        df = df.dropna(subset=["date"])
        df = df.sort_values("date").reset_index(drop=True)

    if "text" in df.columns:
        df["text"] = df["text"].astype(str).str.strip()
        df = df[df["text"].str.len() > 0]

    for col in ["text_ru", "text_en", "text_he"]:
        if col in df.columns:
            df[col] = df[col].fillna("").astype(str).str.strip()

    if "lat" in df.columns:
        df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    if "long" in df.columns:
        df["long"] = pd.to_numeric(df["long"], errors="coerce")

    drop_cols = ["geom", "wikigeom", "wikilat", "wikilong"]
    df = df.drop(columns=[c for c in drop_cols if c in df.columns], errors="ignore")

    return df


def load_from_cache() -> pd.DataFrame:
    """Load preprocessed data from parquet cache (fastest option)."""
    from config import CACHE_PATH
    cache_path = Path(CACHE_PATH)
    if not cache_path.exists():
        raise FileNotFoundError(f"Cache not found: {cache_path}")

    df = pd.read_parquet(cache_path, engine="pyarrow")
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce", utc=True)
    logger.info(f"Loaded {len(df)} rows from cache ({cache_path})")
    return df


def load_data(source: str = "auto", **kwargs) -> pd.DataFrame:
    """
    Universal data loader. Priority: cache > postgres > csv.
    source: 'cache', 'postgres', 'csv', or 'auto'
    """
    if source == "csv":
        return load_from_csv(**kwargs)

    if source == "postgres":
        return load_from_postgres(**kwargs)

    if source == "cache":
        return load_from_cache()

    from config import CACHE_PATH
    cache_path = Path(CACHE_PATH)
    if cache_path.exists():
        logger.info("Loading from cache...")
        return load_from_cache()

    if SSH_CONFIG["enabled"]:
        try:
            logger.info("SSH enabled — connecting to PostgreSQL via tunnel...")
            return load_from_postgres(**kwargs)
        except Exception as e:
            logger.warning(f"PostgreSQL via SSH failed ({e}), trying CSV fallback...")
            csv_path = Path(kwargs.get("path", CSV_DATA_PATH))
            if csv_path.exists():
                return load_from_csv(path=str(csv_path))
            raise

    csv_path = Path(kwargs.get("path", CSV_DATA_PATH))
    if csv_path.exists():
        logger.info(f"Loading from CSV: {csv_path}")
        return load_from_csv(path=str(csv_path))

    try:
        logger.info("CSV not found, trying PostgreSQL...")
        return load_from_postgres(**kwargs)
    except Exception as e:
        raise FileNotFoundError(
            f"No data found. Place CSV at {CSV_DATA_PATH} or configure PostgreSQL in .env\n"
            f"Error: {e}"
        )
