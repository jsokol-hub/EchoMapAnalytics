"""Bilingual narrative text for the war-period summary."""

from __future__ import annotations

import pandas as pd

from i18n import fmt_int, fmt_pct, fmt_float


def war_period_narrative(
    summary: pd.Series,
    top_categories: pd.DataFrame,
    lang: str = "en",
) -> str:
    """Build markdown for the Summary tab — report style, not a data dump."""
    total = int(summary["total_news"])
    d0 = summary["first_date_il"]
    d1 = summary["last_date_il"]
    span = int(summary["calendar_days_span"])
    active = int(summary["distinct_news_days"])
    w0 = int(summary["min_war_day"])
    w1 = int(summary["max_war_day"])

    hs = fmt_pct(summary.get("high_signal_share"))
    ms = fmt_pct(summary.get("multi_source_share"))
    wc = fmt_pct(summary.get("with_coordinates_share"))
    wg = fmt_pct(summary.get("with_geoname_share"))
    wm = fmt_pct(summary.get("with_message_share"))
    avg_sig = fmt_float(summary.get("avg_signal_strength"))
    avg_sig_nn = fmt_float(summary.get("avg_signal_strength_nonnull"))

    top5_parts = _top_categories(top_categories, lang)

    if lang == "ru":
        return _narrative_ru(
            total, d0, d1, span, active, w0, w1,
            hs, ms, wc, wg, wm, avg_sig, avg_sig_nn, top5_parts,
        )
    return _narrative_en(
        total, d0, d1, span, active, w0, w1,
        hs, ms, wc, wg, wm, avg_sig, avg_sig_nn, top5_parts,
    )


def _top_categories(df: pd.DataFrame, lang: str) -> str:
    if df is None or df.empty:
        return ""
    top5 = df.head(5)
    parts: list[str] = []
    for _, row in top5.iterrows():
        name = row["category_clean"]
        cnt = fmt_int(row["news_count"])
        sh = row.get("share_of_total")
        sh_str = fmt_pct(sh) if sh is not None and pd.notna(sh) else ""
        if sh_str:
            parts.append(f"**{name}** ({cnt}, {sh_str})")
        else:
            parts.append(f"**{name}** ({cnt})")
    return ", ".join(parts)


# ---- English ---------------------------------------------------------------

def _narrative_en(
    total, d0, d1, span, active, w0, w1,
    hs, ms, wc, wg, wm, avg_sig, avg_sig_nn, top5,
) -> str:
    lines = [
        "### Analytics window overview",
        "",
        f"Between **{d0}** and **{d1}** ({span} calendar days, war days {w0}–{w1}), "
        f"the dataset contains **{total:,}** news items. "
        f"News was recorded on **{active}** of those days.",
        "",
        "#### Data quality at a glance",
        "",
        f"- **{hs}** of news have a high signal (strength >= 0.7) — "
        "these are considered the most credible items.",
        f"- **{ms}** are confirmed by multiple sources.",
        f"- **{wc}** include geographic coordinates; **{wg}** mention a named location.",
        f"- **{wm}** contain message text.",
        f"- Average signal strength across all items: **{avg_sig}** "
        f"(non-null only: **{avg_sig_nn}**).",
        "",
    ]
    if top5:
        lines += [
            "#### Most covered topics",
            "",
            f"Top categories for the full period: {top5}.",
            "",
        ]
    lines += [
        "---",
        "*All timestamps use Asia/Jerusalem local time. "
        "Methodology: `echomap_dbt/docs/METHODOLOGY.md`.*",
    ]
    return "\n".join(lines)


# ---- Russian ---------------------------------------------------------------

def _narrative_ru(
    total, d0, d1, span, active, w0, w1,
    hs, ms, wc, wg, wm, avg_sig, avg_sig_nn, top5,
) -> str:
    lines = [
        "### Обзор аналитического окна",
        "",
        f"За период **{d0}** — **{d1}** ({span} календарных дней, дни войны {w0}–{w1}) "
        f"в выборке **{total:,}** новостных единиц. "
        f"Новости зафиксированы в **{active}** из этих дней.",
        "",
        "#### Качество данных",
        "",
        f"- **{hs}** новостей имеют высокий сигнал (>= 0.7) — "
        "это наиболее достоверные записи.",
        f"- **{ms}** подтверждены несколькими источниками.",
        f"- **{wc}** содержат географические координаты; **{wg}** упоминают название места.",
        f"- **{wm}** содержат текст сообщения.",
        f"- Средняя сила сигнала по всем записям: **{avg_sig}** "
        f"(только непустые: **{avg_sig_nn}**).",
        "",
    ]
    if top5:
        lines += [
            "#### Самые освещённые темы",
            "",
            f"Топ категорий за весь период: {top5}.",
            "",
        ]
    lines += [
        "---",
        "*Часовой пояс: Asia/Jerusalem. "
        "Методология: `echomap_dbt/docs/METHODOLOGY.md`.*",
    ]
    return "\n".join(lines)
