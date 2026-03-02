"""
Frequency analysis and anomaly detection.
Works with multilingual translations from geonews data.
"""

import logging
import numpy as np
import pandas as pd
from scipy.signal import find_peaks

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import IRAN_KEYWORDS, ESCALATION_CATEGORIES

logger = logging.getLogger(__name__)


def count_keyword_matches(row: pd.Series, keywords: dict[str, list[str]]) -> int:
    """Count keyword matches across all available translation columns."""
    hits = 0
    text_map = {
        "ru": str(row.get("text_clean", "") or row.get("text_ru", "")),
        "en": str(row.get("text_en_clean", "") or row.get("text_en", "")),
        "he": str(row.get("text_he_clean", "") or row.get("text_he", "")),
    }
    for lang, kw_list in keywords.items():
        text = text_map.get(lang, "").lower()
        if text:
            hits += sum(1 for kw in kw_list if kw in text)
    return hits


def build_keyword_timeseries(
    df: pd.DataFrame,
    keywords: dict[str, list[str]] = None,
    freq: str = "D",
) -> pd.DataFrame:
    """Build timeseries of keyword mention counts."""
    if keywords is None:
        keywords = IRAN_KEYWORDS

    df = df.copy()
    df["keyword_hits"] = df.apply(lambda r: count_keyword_matches(r, keywords), axis=1)
    df["has_keyword"] = df["keyword_hits"] > 0

    ts = df.set_index("date").resample(freq).agg(
        total_messages=("text_clean", "count"),
        keyword_messages=("has_keyword", "sum"),
        keyword_hits=("keyword_hits", "sum"),
    )
    ts["keyword_ratio"] = ts["keyword_messages"] / ts["total_messages"].clip(lower=1)

    return ts


def _match_category(row: pd.Series, cat_keywords: dict[str, list[str]]) -> bool:
    """Check if any category keyword matches in the row's translations."""
    text_ru = str(row.get("text_clean", "")).lower()
    text_en = str(row.get("text_en_clean", "") or row.get("text_en", "")).lower()

    for lang, kws in cat_keywords.items():
        text = text_ru if lang == "ru" else text_en
        if any(kw in text for kw in kws):
            return True
    return False


def build_category_timeseries(
    df: pd.DataFrame,
    categories: dict = None,
    freq: str = "D",
) -> pd.DataFrame:
    """Build timeseries for each escalation category."""
    if categories is None:
        categories = ESCALATION_CATEGORIES

    df = df.copy()
    results = {}

    for cat_name, cat_keywords in categories.items():
        df[f"cat_{cat_name}"] = df.apply(
            lambda r, kws=cat_keywords: _match_category(r, kws), axis=1
        )
        ts = df.set_index("date").resample(freq)[f"cat_{cat_name}"].sum()
        results[cat_name] = ts

    return pd.DataFrame(results)


def build_native_category_timeseries(df: pd.DataFrame, freq: str = "D") -> pd.DataFrame:
    """Build timeseries from the native 'category' column in the data."""
    if "category" not in df.columns:
        return pd.DataFrame()

    df = df.copy()
    cats = df["category"].unique()
    results = {}

    for cat in cats:
        ts = df.set_index("date").resample(freq).apply(
            lambda x, c=cat: (x["category"] == c).sum() if "category" in x.columns else 0
        )
        results[cat] = ts

    pivot = df.set_index("date").groupby([pd.Grouper(freq=freq), "category"]).size().unstack(fill_value=0)
    return pivot


def detect_anomalies(
    ts: pd.Series,
    window: int = 14,
    threshold_sigma: float = 2.5,
) -> pd.DataFrame:
    """Detect anomalous spikes using rolling z-score."""
    rolling_mean = ts.rolling(window=window, min_periods=3).mean()
    rolling_std = ts.rolling(window=window, min_periods=3).std()

    z_scores = (ts - rolling_mean) / rolling_std.clip(lower=0.01)

    anomalies = pd.DataFrame({
        "value": ts,
        "rolling_mean": rolling_mean,
        "rolling_std": rolling_std,
        "z_score": z_scores,
        "is_anomaly": z_scores > threshold_sigma,
        "anomaly_strength": z_scores.clip(lower=0),
    })

    n_anomalies = anomalies["is_anomaly"].sum()
    logger.info(f"Detected {n_anomalies} anomalous periods (>{threshold_sigma}σ)")

    return anomalies


def compute_acceleration(ts: pd.Series, window: int = 7) -> pd.Series:
    """Compute acceleration (second derivative) of a timeseries."""
    velocity = ts.diff()
    acceleration = velocity.diff()
    return acceleration.rolling(window=window, min_periods=1).mean()


def find_crescendo_patterns(
    category_ts: pd.DataFrame,
    lookback_days: int = 30,
) -> pd.DataFrame:
    """
    Detect 'crescendo' patterns — multiple categories accelerating simultaneously.
    A strong pre-conflict signal.
    """
    accelerations = pd.DataFrame()
    for col in category_ts.columns:
        accelerations[col] = compute_acceleration(category_ts[col])

    accelerations["composite_acceleration"] = accelerations.mean(axis=1)

    positive_cats = (accelerations[category_ts.columns] > 0).sum(axis=1)
    accelerations["n_accelerating_categories"] = positive_cats

    accelerations["crescendo_score"] = (
        accelerations["composite_acceleration"]
        * accelerations["n_accelerating_categories"]
    )

    return accelerations
