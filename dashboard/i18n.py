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
        "en": "Conflict news coverage · Israel local time",
        "ru": "Освещение конфликта · местное время Израиля",
    },

    # -- intro blurb (markdown) --
    "intro_blurb": {
        "en": "Each row is one news item. Time zone: **Asia/Jerusalem**. Adjust the date range in the sidebar.",
        "ru": "Каждая строка — одна новость. Часовой пояс: **Asia/Jerusalem**. Диапазон дат — слева.",
    },
    "intro_blurb_analyst": {
        "en": "One row = one news item (`news_id`). **Asia/Jerusalem**. Sidebar: date range and chart limits.",
        "ru": "Строка = одна новость (`news_id`). **Asia/Jerusalem**. Слева: диапазон дат и лимиты графиков.",
    },

    # -- display mode --
    "sidebar_mode": {"en": "View", "ru": "Режим"},
    "mode_viewer": {"en": "Viewer — highlights", "ru": "Обзор — главное"},
    "mode_analyst": {"en": "Analyst — full", "ru": "Аналитик — полный"},

    # -- hero / value screen --
    "hero_kicker": {"en": "At a glance · full dataset", "ru": "Сводка · весь период в данных"},
    "hero_events": {"en": "news events", "ru": "событий"},
    "hero_places": {"en": "Hotspots", "ru": "Основные точки"},
    "hero_drop": {
        "en": "{date} — sharp drop (−{pct} vs prior day). Treat nearby days carefully.",
        "ru": "{date} — резкий спад (−{pct} к пред. дню). Соседние дни — с осторожностью.",
    },
    "hero_charts_note": {
        "en": "Charts below use the **selected date range** (sidebar).",
        "ru": "Графики ниже — по **выбранному диапазону** (сайдбар).",
    },

    # -- three insights (short) --
    "insight_where_title": {"en": "Where it happens", "ru": "Где происходит"},
    "insight_where_caption": {"en": "Geographic concentration of mentions (coordinates when available).", "ru": "География упоминаний (если есть координаты)."},
    "insight_when_title": {"en": "When it happens", "ru": "Когда происходит"},
    "insight_when_caption": {"en": "Daily volume in Israel local time.", "ru": "Суточный объём, местное время Израиля."},
    "insight_how_title": {"en": "How it’s covered", "ru": "Как освещается"},
    "insight_how_caption": {
        "en": "Tone (model) + topic mix (top groups; rest → Other).",
        "ru": "Тональность (модель) + темы (топ; остальное → Прочее).",
    },

    "category_other": {"en": "Other", "ru": "Прочее"},

    # -- tabs --
    "tab_overview": {"en": "Overview", "ru": "Обзор"},
    "tab_summary": {"en": "Summary", "ru": "Сводка"},
    "tab_timeline": {"en": "Timeline", "ru": "Хронология"},
    "tab_hourly": {"en": "Hourly patterns", "ru": "По часам"},
    "tab_geography": {"en": "Geography", "ru": "Карта"},

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
    "metric_avg_signal": {"en": "Avg credibility score", "ru": "Средняя оценка достоверности"},
    "metric_total_news": {"en": "Total news", "ru": "Всего новостей"},
    "metric_calendar_days": {"en": "Calendar days", "ru": "Календарных дней"},
    "metric_active_days": {"en": "Active days", "ru": "Активных дней"},

    # -- tooltips for metrics --
    "tip_signal": {
        "en": "Credibility score (0–1). Higher values mean the item is backed by stronger evidence.",
        "ru": "Оценка достоверности (0–1). Чем выше — тем надёжнее подтверждена новость.",
    },
    "tip_high_signal": {
        "en": "Share of news with credibility score >= 0.7 (considered reliable).",
        "ru": "Доля новостей с оценкой достоверности >= 0.7 (считаются надёжными).",
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

    # -- tab intros --
    "intro_summary": {
        "en": "Full-window quality breakdown and category table (analyst).",
        "ru": "Качество данных и таблица категорий за весь период (аналитика).",
    },
    "intro_timeline": {
        "en": "Volume, quality mix, categories, sentiment, sources — for the selected range.",
        "ru": "Объём, качество, категории, тональность, источники — за выбранный диапазон.",
    },
    "intro_hourly": {
        "en": "Heatmap: hour × date. Bar: average news per hour.",
        "ru": "Теплокарта: час × дата. Столбцы: среднее по часу.",
    },
    "intro_geography": {
        "en": "Mentioned locations with coordinates — bubble size = volume.",
        "ru": "Локации с координатами — размер = число новостей.",
    },

    # -- section explanations within tabs --
    "explain_daily_volume": {
        "en": "One point = one day (Israel).",
        "ru": "Одна точка = один день (Израиль).",
    },
    "explain_quality_mix": {
        "en": "High credibility (≥0.7), multi-source, with coordinates — daily share of volume.",
        "ru": "Высокая достоверность (≥0.7), несколько источников, координаты — доля по дням.",
    },
    "explain_categories": {
        "en": "Topic labels from the pipeline (selected range).",
        "ru": "Темы из конвейера данных (выбранный диапазон).",
    },
    "explain_sentiment": {
        "en": "Model-assigned tone over time.",
        "ru": "Тональность модели по дням.",
    },
    "explain_sources": {
        "en": "Which feeds dominate over time (top N in sidebar).",
        "ru": "Какие ленты доминируют (топ N в сайдбаре).",
    },
    "explain_coord_pipeline": {
        "en": "parser / wiki / none — how coordinates were resolved.",
        "ru": "parser / wiki / none — откуда координаты.",
    },
    "explain_heatmap": {
        "en": "Rows: day or week. Columns: hour 0–23 (Israel).",
        "ru": "Строки: день или неделя. Столбцы: час 0–23 (Израиль).",
    },
    "explain_hourly_avg": {
        "en": "Mean items per clock hour in the selected range.",
        "ru": "Среднее по часам в выбранном диапазоне.",
    },
    "explain_map": {
        "en": "Bubble size ∝ news count at that geoname.",
        "ru": "Размер ∝ числу новостей по геониму.",
    },

    # -- volume anomaly --
    "volume_drop_callout": {
        "en": (
            "**Sharp volume change.** Around **{date}** the daily volume dropped by "
            "**{pct}** (from {before} to {after} news/day). "
            "This may reflect changes in the data collection pipeline, source activity, "
            "or events on the ground. Metrics in this period should be interpreted with caution."
        ),
        "ru": (
            "**Резкое изменение объёма.** Примерно **{date}** суточный объём упал на "
            "**{pct}** (с {before} до {after} новостей/день). "
            "Это может быть связано с изменениями в конвейере сбора данных, активности источников "
            "или событиями на местах. Метрики в этом периоде следует интерпретировать с осторожностью."
        ),
    },
    "volume_drop_annotation": {
        "en": "Volume drop",
        "ru": "Падение объёма",
    },

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
    "expander_raw_data": {"en": "Raw data table", "ru": "Таблица с данными"},
    "heatmap_weekly_note": {
        "en": "Long range ({n} days): heatmap aggregated by **week** (rows = week starting Monday).",
        "ru": "Длинный диапазон ({n} дней): тепловая карта агрегирована по **неделям** (строки — начало недели, понедельник).",
    },
    "summary_full_period_note": {
        "en": "Full dbt window here. Sidebar dates affect Overview / Timeline / Hourly / Geography.",
        "ru": "Здесь весь период dbt. Даты слева — для Обзор / Хронология / Часы / Карта.",
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
    "signal_strength": {"en": "Credibility score", "ru": "Оценка достоверности"},
    "avg_signal_strength": {"en": "Avg credibility", "ru": "Ср. достоверность"},
    "high_signal_share": {"en": "High-credibility share", "ru": "Доля с высокой достоверностью"},
    "multi_source_share": {"en": "Multi-source share", "ru": "Доля из неск. источников"},
    "with_coordinates_share": {"en": "With-coordinates share", "ru": "Доля с координатами"},
    "high_signal_count": {"en": "High-credibility count", "ru": "Кол-во с высокой достоверностью"},
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
    "high_signal_share": {"en": "High credibility", "ru": "Высокая достоверность"},
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
