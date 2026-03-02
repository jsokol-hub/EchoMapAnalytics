"""
Text preprocessing for the geonews dataset.
Since translations are already provided, we use them directly
instead of running language detection.
"""

import re
import logging

import pandas as pd

logger = logging.getLogger(__name__)

URL_PATTERN = re.compile(r"https?://\S+|www\.\S+")
TELEGRAM_ENTITIES = re.compile(r"@\w+|#\w+")
EXTRA_WHITESPACE = re.compile(r"\s+")


def clean_text(text: str) -> str:
    """Remove URLs, Telegram entities, excessive whitespace."""
    text = URL_PATTERN.sub("", text)
    text = TELEGRAM_ENTITIES.sub("", text)
    text = EXTRA_WHITESPACE.sub(" ", text)
    return text.strip()


def detect_source_language(row: pd.Series) -> str:
    """Detect original language based on channel name and content heuristics."""
    channel = str(row.get("channel", ""))
    text = str(row.get("text", ""))

    if any(c in channel for c in ["ИнтеллиНьюз", "Интелли", "интелли"]):
        return "ru"

    has_hebrew = bool(re.search(r"[\u0590-\u05FF]", text[:100]))
    has_cyrillic = bool(re.search(r"[а-яА-ЯёЁ]", text[:100]))

    if has_hebrew and not has_cyrillic:
        return "he"
    if has_cyrillic and not has_hebrew:
        return "ru"
    if has_hebrew:
        return "he"

    return "en"


CATEGORY_MAP = {
    "security": "security",
    "безопасность": "security",
    "ביטחון": "security",
    "security alert": "security",
    "security incident": "security",
    "public safety": "security",
    "safety": "security",
    "defense": "security",
    "security/conflict": "security",
    "security/defense": "security",
    "security/military": "security",
    "security/politics": "security",
    "national": "security",

    "military": "military",
    "military conflict": "military",
    "military/conflict": "military",
    "military & security": "military",
    "military & defense": "military",
    "military & conflict": "military",
    "military/security": "military",
    "military/defense/security": "military",
    "военные действия": "military",
    "военные": "military",
    "военный конфликт": "military",
    "военные учения": "military",

    "conflict": "conflict",
    "конфликт": "conflict",
    "war": "conflict",
    "война": "conflict",
    "conflict & war": "conflict",
    "war and conflict": "conflict",
    "war/conflict": "conflict",
    "conflict/war": "conflict",
    "conflict/security": "conflict",
    "conflict/attack": "conflict",
    "conflict/terrorism": "conflict",
    "terrorism": "conflict",
    "israel-hamas war": "conflict",

    "politics": "politics",
    "политика": "politics",
    "פוליטיקה": "politics",
    "politics/security": "politics",
    "politics/conflict": "politics",
    "diplomacy": "politics",
    "geopolitics": "politics",
    "international relations": "politics",

    "accident": "accident",
    "происшествия": "accident",
    "incident": "accident",
    "incidents": "accident",
    "disaster": "accident",
    "emergency": "accident",
    "emergencies": "accident",
    "fire": "accident",
    "natural disaster": "accident",
    "чрезвычайные ситуации": "accident",
    "crisis": "accident",

    "international": "international",
    "международный": "international",

    "humanitarian": "humanitarian",
    "humanitarian aid": "humanitarian",
    "гуманитарная помощь": "humanitarian",

    "crime": "crime",
    "криминал": "crime",
    "פלילים": "crime",
    "law enforcement": "crime",

    "general": "general",
    "general news": "general",
    "news": "general",
    "новости": "general",
    "local": "general",
    "local news": "general",
}


def _normalize_category(cat: str) -> str:
    """Normalize the messy LLM-generated categories to a standard set."""
    if not cat or not isinstance(cat, str):
        return "general"
    cat_lower = cat.lower().strip()

    if cat_lower in CATEGORY_MAP:
        return CATEGORY_MAP[cat_lower]

    for key, val in CATEGORY_MAP.items():
        if key in cat_lower:
            return val

    return "other"


def preprocess_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Full preprocessing pipeline for geonews data.
    Uses existing translations — no need for external language detection.
    """
    df = df.copy()

    df["language"] = df.apply(detect_source_language, axis=1)

    text_col = "text_ru"
    if text_col not in df.columns:
        text_col = "text"

    df["text_clean"] = df[text_col].apply(clean_text)

    for col in ["text_en", "text_he"]:
        if col in df.columns:
            df[f"{col}_clean"] = df[col].apply(clean_text)

    if "date" in df.columns:
        df["date_day"] = df["date"].dt.date
        df["date_hour"] = df["date"].dt.hour
        df["date_weekday"] = df["date"].dt.day_name()
        df["date_week"] = df["date"].dt.isocalendar().week.astype(int)
        df["date_month"] = df["date"].dt.strftime("%Y-%m")

    df["text_length"] = df["text_clean"].str.len()
    df["word_count"] = df["text_clean"].str.split().str.len()

    if "category" in df.columns:
        df["category_raw"] = df["category"]
        df["category"] = df["category"].apply(_normalize_category)

    lang_counts = df["language"].value_counts()
    logger.info(f"Language distribution:\n{lang_counts}")

    if "category" in df.columns:
        cat_counts = df["category"].value_counts()
        logger.info(f"Category distribution:\n{cat_counts}")

    return df
