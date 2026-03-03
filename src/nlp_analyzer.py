"""
NLP analysis module — sentiment analysis, NER, and topic classification.
Uses multilingual transformer models (XLM-RoBERTa) for Russian, English, Hebrew.
"""

import logging
from functools import lru_cache

import numpy as np
import pandas as pd
from tqdm import tqdm
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import SENTIMENT_MODEL, NER_MODEL

logger = logging.getLogger(__name__)

_sentiment_pipeline = None
_ner_pipeline = None


def _get_sentiment_pipeline():
    global _sentiment_pipeline
    if _sentiment_pipeline is None:
        logger.info(f"Loading sentiment model: {SENTIMENT_MODEL}")
        _sentiment_pipeline = pipeline(
            "sentiment-analysis",
            model=SENTIMENT_MODEL,
            tokenizer=SENTIMENT_MODEL,
            top_k=None,
            truncation=True,
            max_length=512,
        )
    return _sentiment_pipeline


def _get_ner_pipeline():
    global _ner_pipeline
    if _ner_pipeline is None:
        logger.info(f"Loading NER model: {NER_MODEL}")
        _ner_pipeline = pipeline(
            "ner",
            model=NER_MODEL,
            tokenizer=NER_MODEL,
            aggregation_strategy="simple",
            truncation=True,
            max_length=512,
        )
    return _ner_pipeline


def analyze_sentiment_batch(
    texts: list[str],
    batch_size: int = 32,
    progress_callback=None,
) -> list[dict]:
    """
    Analyze sentiment for a batch of texts.
    progress_callback(batch_index, total_batches) called each batch if provided.
    """
    pipe = _get_sentiment_pipeline()
    results = []
    total_batches = (len(texts) + batch_size - 1) // batch_size

    for i in tqdm(range(0, len(texts), batch_size), desc="Sentiment"):
        batch = texts[i:i + batch_size]
        batch = [t[:512] if len(t) > 512 else t for t in batch]
        try:
            batch_results = pipe(batch)
            for pred in batch_results:
                sorted_pred = sorted(pred, key=lambda x: x["score"], reverse=True)
                results.append({
                    "sentiment_label": sorted_pred[0]["label"],
                    "sentiment_score": sorted_pred[0]["score"],
                    "sentiment_positive": next(
                        (p["score"] for p in sorted_pred if p["label"] == "positive"), 0
                    ),
                    "sentiment_negative": next(
                        (p["score"] for p in sorted_pred if p["label"] == "negative"), 0
                    ),
                    "sentiment_neutral": next(
                        (p["score"] for p in sorted_pred if p["label"] == "neutral"), 0
                    ),
                })
        except Exception as e:
            logger.warning(f"Sentiment batch failed: {e}")
            results.extend([{
                "sentiment_label": "unknown",
                "sentiment_score": 0,
                "sentiment_positive": 0,
                "sentiment_negative": 0,
                "sentiment_neutral": 0,
            }] * len(batch))
        if progress_callback:
            batch_idx = i // batch_size
            progress_callback(batch_idx + 1, total_batches)

    return results


def extract_entities_batch(
    texts: list[str],
    batch_size: int = 16,
) -> list[list[dict]]:
    """
    Extract named entities from texts.
    Returns list of entity lists, each entity has: word, entity_group, score.
    """
    pipe = _get_ner_pipeline()
    results = []

    for i in tqdm(range(0, len(texts), batch_size), desc="NER"):
        batch = texts[i:i + batch_size]
        batch = [t[:512] if len(t) > 512 else t for t in batch]
        try:
            batch_results = pipe(batch)
            for entities in batch_results:
                results.append([
                    {
                        "word": ent["word"],
                        "entity_group": ent["entity_group"],
                        "score": float(ent["score"]),
                    }
                    for ent in entities
                    if ent["score"] > 0.5
                ])
        except Exception as e:
            logger.warning(f"NER batch failed: {e}")
            results.extend([[]] * len(batch))

    return results


def add_sentiment_to_df(df: pd.DataFrame, progress_callback=None) -> pd.DataFrame:
    """Add sentiment columns to DataFrame. progress_callback(batch, total_batches) optional."""
    df = df.copy()
    texts = df["text_clean"].tolist()
    sentiments = analyze_sentiment_batch(texts, progress_callback=progress_callback)
    sentiment_df = pd.DataFrame(sentiments)
    for col in sentiment_df.columns:
        df[col] = sentiment_df[col].values
    return df


def add_entities_to_df(df: pd.DataFrame) -> pd.DataFrame:
    """Add NER results to DataFrame."""
    df = df.copy()
    texts = df["text_clean"].tolist()
    entities = extract_entities_batch(texts)
    df["entities"] = entities
    df["entity_count"] = df["entities"].apply(len)

    df["persons"] = df["entities"].apply(
        lambda ents: [e["word"] for e in ents if e["entity_group"] == "PER"]
    )
    df["locations"] = df["entities"].apply(
        lambda ents: [e["word"] for e in ents if e["entity_group"] == "LOC"]
    )
    df["organizations"] = df["entities"].apply(
        lambda ents: [e["word"] for e in ents if e["entity_group"] == "ORG"]
    )

    return df


def build_sentiment_timeseries(df: pd.DataFrame, freq: str = "D") -> pd.DataFrame:
    """Aggregate sentiment scores by time period."""
    if "sentiment_negative" not in df.columns:
        raise ValueError("Run add_sentiment_to_df first")

    ts = df.set_index("date").resample(freq).agg(
        mean_negative=("sentiment_negative", "mean"),
        mean_positive=("sentiment_positive", "mean"),
        mean_neutral=("sentiment_neutral", "mean"),
        pct_negative=("sentiment_label", lambda x: (x == "negative").mean()),
        pct_positive=("sentiment_label", lambda x: (x == "positive").mean()),
        message_count=("text_clean", "count"),
    )

    ts["negativity_index"] = ts["mean_negative"] - ts["mean_positive"]

    return ts


def get_top_entities(
    df: pd.DataFrame,
    entity_type: str = None,
    top_n: int = 20,
) -> pd.DataFrame:
    """Get most frequently mentioned entities."""
    col_map = {"PER": "persons", "LOC": "locations", "ORG": "organizations"}

    if entity_type and entity_type in col_map:
        col = col_map[entity_type]
        if col not in df.columns:
            return pd.DataFrame()
        all_entities = df[col].explode().dropna()
    elif "entities" in df.columns:
        all_entities = df["entities"].explode().dropna()
        if len(all_entities) > 0 and isinstance(all_entities.iloc[0], dict):
            all_entities = all_entities.apply(lambda e: e.get("word", ""))
    else:
        return pd.DataFrame()

    counts = all_entities.value_counts().head(top_n)
    return counts.reset_index().rename(columns={"index": "entity", 0: "count"})
