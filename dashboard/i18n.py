"""Internationalisation helpers for the EchoMap dashboard (EN / RU)."""

from __future__ import annotations

from typing import Any

LANGS = ("en", "ru")
DEFAULT_LANG = "en"

# ---------------------------------------------------------------------------
# Master dictionary: key -> {en: ..., ru: ...}
# ---------------------------------------------------------------------------
_STRINGS: dict[str, dict[str, str]] = {
    # -- page / chrome --
    "page_title": {
        "en": "EchoMap Analytics",
        "ru": "EchoMap — Аналитика",
    },
    "main_title": {
        "en": "EchoMap",
        "ru": "EchoMap",
    },
    "subtitle": {
        "en": "Wartime news analytics — Israel, local time (Asia/Jerusalem)",
        "ru": "Аналитика военных новостей — Израиль, местное время (Asia/Jerusalem)",
    },

    # -- intro blurb (markdown) --
    "intro_blurb": {
        "en": (
            "This dashboard shows **news coverage** during the armed conflict in Israel. "
            "Each row in the data represents one news item (`news_id`). "
            "All dates and hours use **Israel local time**. "
            "Use the sidebar to adjust the date range."
        ),
        "ru": (
            "Дашборд показывает **покрытие новостей** во время вооружённого конфликта в Израиле. "
            "Каждая строка — одна новость (`news_id`). "
            "Все даты и часы указаны по **местному времени Израиля**. "
            "Используйте боковую панель для изменения диапазона дат."
        ),
    },

    # -- tabs --
    "tab_summary": {"en": "Summary", "ru": "Сводка"},
    "tab_timeline": {"en": "Timeline", "ru": "Хронология"},
    "tab_hourly": {"en": "Hourly patterns", "ru": "Активность по часам"},
    "tab_geography": {"en": "Geography", "ru": "География"},

    # -- sidebar --
    "sidebar_filters": {"en": "Filters", "ru": "Фильтры"},
    "sidebar_date_range": {"en": "Date range (Israel)", "ru": "Диапазон дат (Израиль)"},
    "sidebar_top_categories": {"en": "Top categories", "ru": "Топ категорий"},
    "sidebar_locations": {"en": "Locations on map / table", "ru": "Локации на карте / в таблице"},
    "sidebar_top_sources": {"en": "Top data sources (chart)", "ru": "Топ источников (график)"},
    "sidebar_loc_hint": {
        "en": "Max location rows from DB (`ECHOMAP_DASH_LOC_LIMIT`): **{n}**.",
        "ru": "Макс. строк локаций из БД (`ECHOMAP_DASH_LOC_LIMIT`): **{n}**.",
    },
    "sidebar_language": {"en": "Language / Язык", "ru": "Язык / Language"},

    # -- metrics --
    "metric_news_in_range": {"en": "News in range", "ru": "Новости в диапазоне"},
    "metric_days_in_range": {"en": "Days in range", "ru": "Дней в диапазоне"},
    "metric_avg_signal": {"en": "Avg signal strength", "ru": "Средняя сила сигнала"},
    "metric_total_news": {"en": "Total news", "ru": "Всего новостей"},
    "metric_calendar_days": {"en": "Calendar days", "ru": "Календарных дней"},
    "metric_active_days": {"en": "Active days", "ru": "Активных дней"},

    # -- tooltips for metrics --
    "tip_signal": {
        "en": "Signal strength ranges 0–1. Higher values indicate stronger evidence / credibility.",
        "ru": "Сила сигнала от 0 до 1. Высокие значения означают более достоверную новость.",
    },
    "tip_high_signal": {
        "en": "Share of news with signal strength >= 0.7 (considered reliable).",
        "ru": "Доля новостей с силой сигнала >= 0.7 (считаются надёжными).",
    },
    "tip_multi_source": {
        "en": "Share of news confirmed by more than one source.",
        "ru": "Доля новостей, подтверждённых более чем одним источником.",
    },
    "tip_with_coords": {
        "en": "Share of news that have geographic coordinates.",
        "ru": "Доля новостей с географическими координатами.",
    },
    "tip_with_geoname": {
        "en": "Share of news that mention a named location.",
        "ru": "Доля новостей с указанием названия места.",
    },
    "tip_with_message": {
        "en": "Share of news that contain message text.",
        "ru": "Доля новостей с текстом сообщения.",
    },
    "tip_sentiment": {
        "en": "Automated sentiment classification: positive / negative / neutral / unknown.",
        "ru": "Автоматическая классификация тональности: позитивная / негативная / нейтральная / неизвестная.",
    },
    "tip_category": {
        "en": "News category assigned during data collection (e.g. military, politics).",
        "ru": "Категория новости, присвоенная при сборе данных (например, военные, политика).",
    },
    "tip_coordinate_source": {
        "en": "'parser' — coordinates extracted automatically; 'wiki' — looked up from Wikipedia; 'none' — no coordinates.",
        "ru": "'parser' — координаты извлечены автоматически; 'wiki' — найдены в Википедии; 'none' — координат нет.",
    },

    # -- chart titles --
    "chart_daily_volume": {"en": "Daily news volume", "ru": "Объём новостей по дням"},
    "chart_quality_mix": {
        "en": "Data quality indicators (share of daily volume)",
        "ru": "Показатели качества данных (доля от дневного объёма)",
    },
    "chart_categories": {"en": "News by category", "ru": "Новости по категориям"},
    "chart_sentiment_daily": {"en": "Sentiment over time", "ru": "Тональность по дням"},
    "chart_sources_daily": {"en": "Data sources over time", "ru": "Источники по дням"},
    "chart_coord_pipeline": {
        "en": "Coordinate origin (parser / wiki / none)",
        "ru": "Источник координат (parser / wiki / none)",
    },
    "chart_heatmap": {"en": "Activity heatmap (hour × date)", "ru": "Тепловая карта активности (час × дата)"},
    "chart_hourly_avg": {"en": "Average news per hour", "ru": "Среднее кол-во новостей по часам"},
    "chart_top_locations": {"en": "Top locations", "ru": "Топ локаций"},
    "chart_sentiment_pie": {"en": "Sentiment breakdown (full period)", "ru": "Распределение тональности (весь период)"},
    "chart_coord_pie": {"en": "Coordinate source (full period)", "ru": "Источник координат (весь период)"},
    "chart_top_categories_period": {"en": "Top categories (full period)", "ru": "Топ категорий (весь период)"},

    # -- misc UI --
    "empty_no_data": {"en": "No data in this date range.", "ru": "Нет данных в этом диапазоне дат."},
    "empty_run_dbt": {
        "en": "No data available — run `dbt run` in `echomap_dbt`.",
        "ru": "Данных нет — выполните `dbt run` в `echomap_dbt`.",
    },
    "error_db": {
        "en": "Could not load data. Check `.env`, database connection, and `ECHOMAP_DBT_SCHEMA`.",
        "ru": "Не удалось загрузить данные. Проверьте `.env`, подключение к БД и `ECHOMAP_DBT_SCHEMA`.",
    },
    "expander_raw_data": {"en": "Raw data", "ru": "Сырые данные"},
    "heatmap_weekly_note": {
        "en": "Long range ({n} days): heatmap aggregated by **week** (rows = week starting Monday).",
        "ru": "Длинный диапазон ({n} дней): тепловая карта агрегирована по **неделям** (строки — начало недели, понедельник).",
    },
    "summary_full_period_note": {
        "en": "The **Summary** tab covers the full analytics window (dbt vars). The date filter on the left affects other tabs.",
        "ru": "Вкладка **Сводка** охватывает весь аналитический период (переменные dbt). Фильтр дат слева влияет на остальные вкладки.",
    },
    "summary_key_metrics": {"en": "Key metrics", "ru": "Ключевые показатели"},
}


# ---------------------------------------------------------------------------
# Sentiment colours — consistent everywhere
# ---------------------------------------------------------------------------
SENTIMENT_COLORS = {
    "positive": "#22c55e",
    "negative": "#ef4444",
    "neutral":  "#94a3b8",
    "unknown":  "#d4d4d8",
}

# ---------------------------------------------------------------------------
# Column renames for st.dataframe — human-readable
# ---------------------------------------------------------------------------
_COL_RENAMES: dict[str, dict[str, str]] = {
    "published_date_il": {"en": "Date (Israel)", "ru": "Дата (Израиль)"},
    "published_hour_il": {"en": "Hour (Israel)", "ru": "Час (Израиль)"},
    "war_day_number": {"en": "War day", "ru": "День войны"},
    "news_count": {"en": "News count", "ru": "Кол-во новостей"},
    "category_clean": {"en": "Category", "ru": "Категория"},
    "sentiment_clean": {"en": "Sentiment", "ru": "Тональность"},
    "data_source_clean": {"en": "Data source", "ru": "Источник данных"},
    "coordinate_source": {"en": "Coordinate source", "ru": "Источник координат"},
    "signal_strength": {"en": "Signal strength", "ru": "Сила сигнала"},
    "avg_signal_strength": {"en": "Avg signal", "ru": "Ср. сигнал"},
    "high_signal_share": {"en": "High-signal share", "ru": "Доля с высоким сигналом"},
    "multi_source_share": {"en": "Multi-source share", "ru": "Доля из неск. источников"},
    "with_coordinates_share": {"en": "With-coordinates share", "ru": "Доля с координатами"},
    "high_signal_count": {"en": "High-signal count", "ru": "Кол-во с высоким сигналом"},
    "geoname": {"en": "Location name", "ru": "Название места"},
    "final_lat": {"en": "Latitude", "ru": "Широта"},
    "final_lon": {"en": "Longitude", "ru": "Долгота"},
    "share_of_total": {"en": "Share of total", "ru": "Доля от всего"},
    "total_news": {"en": "Total news", "ru": "Всего новостей"},
    "first_date_il": {"en": "First date (IL)", "ru": "Первая дата (Изр.)"},
    "last_date_il": {"en": "Last date (IL)", "ru": "Последняя дата (Изр.)"},
    "calendar_days_span": {"en": "Calendar days span", "ru": "Календарных дней"},
    "distinct_news_days": {"en": "Active news days", "ru": "Дней с новостями"},
}


# ---------------------------------------------------------------------------
# Quality-mix line renames
# ---------------------------------------------------------------------------
QUALITY_RENAMES: dict[str, dict[str, str]] = {
    "high_signal_share": {"en": "High signal", "ru": "Высокий сигнал"},
    "multi_source_share": {"en": "Multi-source", "ru": "Неск. источников"},
    "with_coordinates_share": {"en": "With coordinates", "ru": "С координатами"},
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def t(key: str, lang: str = DEFAULT_LANG, **kwargs: Any) -> str:
    """Look up a translated string. Falls back to English, then to the key."""
    entry = _STRINGS.get(key)
    if entry is None:
        return key
    text = entry.get(lang, entry.get("en", key))
    if kwargs:
        text = text.format(**kwargs)
    return text


def col_rename(lang: str = DEFAULT_LANG) -> dict[str, str]:
    """Return {raw_column: human_label} for the active language."""
    return {k: v.get(lang, v.get("en", k)) for k, v in _COL_RENAMES.items()}


def quality_rename(lang: str = DEFAULT_LANG) -> dict[str, str]:
    return {k: v.get(lang, v.get("en", k)) for k, v in QUALITY_RENAMES.items()}


def fmt_pct(value: float | None, na: str = "—") -> str:
    """Format a 0-1 fraction as a readable percentage."""
    import pandas as pd
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return na
    return f"{float(value) * 100:.1f} %"


def fmt_int(value: int | float | None, na: str = "—") -> str:
    """Format an integer with thousand separators."""
    import pandas as pd
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return na
    return f"{int(value):,}"


def fmt_float(value: float | None, decimals: int = 3, na: str = "—") -> str:
    import pandas as pd
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return na
    return f"{float(value):.{decimals}f}"
