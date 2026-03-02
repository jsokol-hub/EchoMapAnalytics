"""
Preload data from PostGIS into a local parquet file.
Run via cron every 5-10 minutes on the server:
  */5 * * * * cd /app && python scripts/preload_cache.py
"""

import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def main():
    from src.data_loader import load_from_postgres, _stop_ssh_tunnel
    from src.preprocessor import preprocess_dataframe
    from src.geo_analyzer import add_region_column
    from config import CACHE_PATH

    cache_path = Path(CACHE_PATH)
    cache_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        logger.info("Loading from PostGIS...")
        df = load_from_postgres()
        logger.info(f"Loaded {len(df)} rows")

        logger.info("Preprocessing...")
        df = preprocess_dataframe(df)
        df = add_region_column(df)

        logger.info(f"Saving to {cache_path}...")
        df.to_parquet(cache_path, index=False, engine="pyarrow")

        size_mb = cache_path.stat().st_size / 1024 / 1024
        logger.info(f"Cache saved: {size_mb:.1f} MB, {len(df)} rows")

    except Exception as e:
        logger.error(f"Preload failed: {e}")
        raise
    finally:
        try:
            _stop_ssh_tunnel()
        except Exception:
            pass


if __name__ == "__main__":
    main()
