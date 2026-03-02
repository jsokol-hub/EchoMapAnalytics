"""
Composite signal scoring and predictive analysis.
Combines frequency, sentiment, and entity signals into an escalation index.
"""

import logging

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from scipy.signal import find_peaks

logger = logging.getLogger(__name__)


SIGNAL_WEIGHTS = {
    "keyword_frequency": 0.20,
    "keyword_acceleration": 0.15,
    "sentiment_negativity": 0.10,
    "category_military_action": 0.20,
    "category_casualties_damage": 0.10,
    "category_diplomatic_political": 0.05,
    "category_missile_defense": 0.10,
    "category_regional_escalation": 0.10,
}


def build_composite_signal(
    keyword_ts: pd.DataFrame,
    category_ts: pd.DataFrame,
    sentiment_ts: pd.DataFrame = None,
    weights: dict = None,
) -> pd.DataFrame:
    """
    Build a composite escalation signal from multiple indicators.
    All timeseries must share the same date index.
    """
    if weights is None:
        weights = SIGNAL_WEIGHTS

    signals = pd.DataFrame(index=keyword_ts.index)

    signals["keyword_frequency"] = _normalize_series(keyword_ts["keyword_hits"])
    signals["keyword_acceleration"] = _normalize_series(
        keyword_ts["keyword_hits"].diff().rolling(7, min_periods=1).mean()
    )

    for cat_col in category_ts.columns:
        key = f"category_{cat_col}"
        if key in weights:
            signals[key] = _normalize_series(category_ts[cat_col])

    if sentiment_ts is not None and "negativity_index" in sentiment_ts.columns:
        aligned = sentiment_ts["negativity_index"].reindex(signals.index)
        signals["sentiment_negativity"] = _normalize_series(aligned.fillna(0))
    else:
        signals["sentiment_negativity"] = 0

    composite = pd.Series(0.0, index=signals.index)
    for signal_name, weight in weights.items():
        if signal_name in signals.columns:
            composite += signals[signal_name] * weight

    signals["composite_escalation_index"] = composite
    signals["composite_smoothed"] = composite.rolling(3, min_periods=1).mean()

    return signals


def _normalize_series(s: pd.Series) -> pd.Series:
    """Normalize series to 0-1 range."""
    s = s.fillna(0)
    min_val, max_val = s.min(), s.max()
    if max_val == min_val:
        return pd.Series(0.0, index=s.index)
    return (s - min_val) / (max_val - min_val)


def classify_alert_level(score: float) -> str:
    """Map composite score to alert level."""
    if score >= 0.8:
        return "CRITICAL"
    if score >= 0.6:
        return "HIGH"
    if score >= 0.4:
        return "ELEVATED"
    if score >= 0.2:
        return "GUARDED"
    return "LOW"


def find_signal_peaks(
    signals: pd.DataFrame,
    column: str = "composite_escalation_index",
    prominence: float = 0.15,
    distance: int = 5,
) -> pd.DataFrame:
    """Find significant peaks in the escalation signal."""
    values = signals[column].fillna(0).values
    peaks, properties = find_peaks(
        values,
        prominence=prominence,
        distance=distance,
    )

    peak_data = []
    for idx in peaks:
        date = signals.index[idx]
        score = values[idx]
        peak_data.append({
            "date": date,
            "score": score,
            "alert_level": classify_alert_level(score),
            "prominence": properties["prominences"][list(peaks).index(idx)],
        })

    return pd.DataFrame(peak_data)


def generate_retrospective_report(
    signals: pd.DataFrame,
    event_date: str = "2026-02-28",
) -> dict:
    """
    Generate a retrospective analysis:
    What signals were present before the event?
    """
    event_dt = pd.Timestamp(event_date, tz="UTC")
    pre_event = signals[signals.index < event_dt]

    if pre_event.empty:
        return {"error": "No data before event date"}

    report = {
        "event_date": event_date,
        "data_range": {
            "start": str(pre_event.index.min()),
            "end": str(pre_event.index.max()),
            "days": len(pre_event),
        },
    }

    last_30 = pre_event.tail(30)
    last_7 = pre_event.tail(7)
    last_1 = pre_event.tail(1)

    report["escalation_index"] = {
        "last_day": float(last_1["composite_escalation_index"].iloc[0]) if len(last_1) > 0 else None,
        "last_7d_avg": float(last_7["composite_escalation_index"].mean()),
        "last_30d_avg": float(last_30["composite_escalation_index"].mean()),
        "last_7d_trend": "rising" if last_7["composite_escalation_index"].is_monotonic_increasing else
                         "falling" if last_7["composite_escalation_index"].is_monotonic_decreasing else "mixed",
        "max_last_30d": float(last_30["composite_escalation_index"].max()),
        "max_date": str(last_30["composite_escalation_index"].idxmax()),
    }

    signal_cols = [c for c in signals.columns if c not in ("composite_escalation_index", "composite_smoothed")]
    top_signals = {}
    for col in signal_cols:
        top_signals[col] = {
            "last_7d_avg": float(last_7[col].mean()),
            "last_30d_avg": float(last_30[col].mean()),
            "contribution": float(last_7[col].mean() * SIGNAL_WEIGHTS.get(col, 0)),
        }

    report["signal_breakdown"] = dict(
        sorted(top_signals.items(), key=lambda x: x[1]["contribution"], reverse=True)
    )

    peaks = find_signal_peaks(pre_event)
    if not peaks.empty:
        report["peaks"] = peaks.tail(10).to_dict("records")

    report["alert_level"] = classify_alert_level(
        report["escalation_index"]["last_7d_avg"]
    )

    return report


def estimate_lead_time(
    signals: pd.DataFrame,
    event_date: str = "2026-02-28",
    threshold: float = 0.5,
) -> dict:
    """
    Estimate how many days before the event the escalation index
    first crossed a given threshold.
    """
    event_dt = pd.Timestamp(event_date, tz="UTC")
    pre_event = signals[signals.index < event_dt]

    idx = pre_event["composite_escalation_index"]
    crossed = idx[idx >= threshold]

    if crossed.empty:
        return {
            "threshold": threshold,
            "first_crossed": None,
            "lead_time_days": None,
            "message": f"Signal never reached {threshold} before event",
        }

    first_cross = crossed.index[0]
    lead_time = (event_dt - first_cross).days

    sustained = True
    after_cross = idx[idx.index >= first_cross]
    if (after_cross < threshold * 0.7).any():
        sustained = False

    return {
        "threshold": threshold,
        "first_crossed": str(first_cross),
        "lead_time_days": lead_time,
        "sustained": sustained,
    }
