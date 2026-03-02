"""
Geographic analysis module.
Leverages lat/long and geoname from the geonews dataset
for spatial event mapping and hotspot detection.
"""

import logging
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

KNOWN_REGIONS = {
    "Israel": {"lat_range": (29.5, 33.5), "lon_range": (34.0, 36.0)},
    "Iran": {"lat_range": (25.0, 40.0), "lon_range": (44.0, 63.5)},
    "Gulf States": {"lat_range": (22.0, 30.0), "lon_range": (48.0, 60.0)},
    "Lebanon": {"lat_range": (33.0, 34.7), "lon_range": (35.0, 36.7)},
}


def classify_region(lat: float, lon: float) -> str:
    """Classify a coordinate into a named region."""
    if pd.isna(lat) or pd.isna(lon):
        return "Unknown"
    for region, bounds in KNOWN_REGIONS.items():
        lat_min, lat_max = bounds["lat_range"]
        lon_min, lon_max = bounds["lon_range"]
        if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
            return region
    return "Other"


def add_region_column(df: pd.DataFrame) -> pd.DataFrame:
    """Add a 'region' column based on lat/long."""
    df = df.copy()
    if "lat" in df.columns and "long" in df.columns:
        df["region"] = df.apply(lambda r: classify_region(r["lat"], r["long"]), axis=1)
    return df


def get_location_stats(df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
    """Get most frequently mentioned locations."""
    if "location" not in df.columns:
        return pd.DataFrame()

    counts = df["location"].value_counts().head(top_n).reset_index()
    counts.columns = ["location", "count"]

    if "lat" in df.columns and "long" in df.columns:
        coords = df.groupby("location")[["lat", "long"]].median().reset_index()
        counts = counts.merge(coords, on="location", how="left")

    if "category" in df.columns:
        dominant_cat = (
            df.groupby("location")["category"]
            .agg(lambda x: x.value_counts().index[0] if len(x) > 0 else "unknown")
            .reset_index()
        )
        dominant_cat.columns = ["location", "dominant_category"]
        counts = counts.merge(dominant_cat, on="location", how="left")

    return counts


def build_geo_timeseries(df: pd.DataFrame, freq: str = "D") -> pd.DataFrame:
    """Build timeseries of events by region."""
    if "region" not in df.columns:
        df = add_region_column(df)

    if "region" not in df.columns:
        return pd.DataFrame()

    pivot = (
        df.set_index("date")
        .groupby([pd.Grouper(freq=freq), "region"])
        .size()
        .unstack(fill_value=0)
    )
    return pivot


def get_map_data(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare data for map visualization."""
    if "lat" not in df.columns or "long" not in df.columns:
        return pd.DataFrame()

    map_df = df[["date", "lat", "long", "location", "text_clean", "category"]].copy()
    map_df = map_df.dropna(subset=["lat", "long"])
    map_df = map_df[(map_df["lat"] != 0) & (map_df["long"] != 0)]

    return map_df
