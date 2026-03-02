"""
Run the full analysis pipeline without the dashboard.
Outputs results to data/ folder as CSV files.
"""

import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


def main():
    from src.data_loader import load_data
    from src.preprocessor import preprocess_dataframe
    from src.frequency_analyzer import (
        build_keyword_timeseries,
        build_category_timeseries,
        detect_anomalies,
        find_crescendo_patterns,
    )
    from src.nlp_analyzer import add_sentiment_to_df, add_entities_to_df, build_sentiment_timeseries
    from src.signal_scorer import build_composite_signal, generate_retrospective_report, estimate_lead_time
    from config import IRAN_KEYWORDS, ESCALATION_CATEGORIES, DATA_DIR
    import json

    logger.info("=== Step 1: Loading data ===")
    df = load_data()
    logger.info(f"Loaded {len(df)} messages")

    logger.info("=== Step 2: Preprocessing ===")
    df = preprocess_dataframe(df)

    logger.info("=== Step 3: Frequency analysis ===")
    keyword_ts = build_keyword_timeseries(df, IRAN_KEYWORDS)
    category_ts = build_category_timeseries(df, ESCALATION_CATEGORIES)
    anomalies = detect_anomalies(keyword_ts["keyword_hits"])
    crescendo = find_crescendo_patterns(category_ts)

    keyword_ts.to_csv(DATA_DIR / "keyword_timeseries.csv")
    category_ts.to_csv(DATA_DIR / "category_timeseries.csv")
    anomalies.to_csv(DATA_DIR / "anomalies.csv")
    logger.info("Frequency analysis saved")

    logger.info("=== Step 4: Sentiment analysis ===")
    df = add_sentiment_to_df(df)
    sentiment_ts = build_sentiment_timeseries(df)
    sentiment_ts.to_csv(DATA_DIR / "sentiment_timeseries.csv")

    logger.info("=== Step 5: Named Entity Recognition ===")
    df = add_entities_to_df(df)

    logger.info("=== Step 6: Composite signal ===")
    signals = build_composite_signal(keyword_ts, category_ts, sentiment_ts)
    signals.to_csv(DATA_DIR / "signals.csv")

    logger.info("=== Step 7: Retrospective report ===")
    report = generate_retrospective_report(signals)
    with open(DATA_DIR / "retrospective_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2, default=str)
    logger.info(f"Alert level: {report.get('alert_level', 'N/A')}")

    for threshold in [0.3, 0.5, 0.7]:
        lt = estimate_lead_time(signals, threshold=threshold)
        if lt["lead_time_days"]:
            logger.info(f"Lead time at {threshold}: {lt['lead_time_days']} days")

    df.to_csv(DATA_DIR / "processed_messages.csv", index=False)
    logger.info(f"\n✅ All results saved to {DATA_DIR}/")


if __name__ == "__main__":
    main()
