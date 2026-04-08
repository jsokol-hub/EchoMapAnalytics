"""Bilingual narrative text for the war-period summary."""

from __future__ import annotations

import pandas as pd

from i18n import fmt_int, fmt_pct, fmt_float


def war_period_narrative(
    summary: pd.Series,
    top_categories: pd.DataFrame,
    lang: str = "en",
    *,
    compact: bool = False,
) -> str:
    """Build markdown for the Summary tab — report style, or a short note if compact."""
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

    if compact:
        return _narrative_compact(
            total, d0, d1, span, hs, ms, wc, top5_parts, lang,
        )

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


def _narrative_compact(
    total, d0, d1, span, hs, ms, wc, top5: str, lang: str,
) -> str:
    if lang == "ru":
        lines = [
            f"**{total:,}** новостей за **{span}** календарных дней ({d0} — {d1}). "
            f"Высокая достоверность: **{hs}**, несколько источников: **{ms}**, с координатами: **{wc}**.",
        ]
        if top5:
            lines.append(f"Топ тем: {top5}.")
        lines.append(
            "*Часовой пояс Asia/Jerusalem. Методология: `echomap_dbt/docs/METHODOLOGY.md`.*",
        )
        return "\n\n".join(lines)
    lines = [
        f"**{total:,}** news items across **{span}** calendar days ({d0} — {d1}). "
        f"High credibility: **{hs}**, multi-source: **{ms}**, with coordinates: **{wc}**.",
    ]
    if top5:
        lines.append(f"Top topics: {top5}.")
    lines.append(
        "*Asia/Jerusalem. Methodology: `echomap_dbt/docs/METHODOLOGY.md`.*",
    )
    return "\n\n".join(lines)


# ---- English ---------------------------------------------------------------

def _narrative_en(
    total, d0, d1, span, active, w0, w1,
    hs, ms, wc, wg, wm, avg_sig, avg_sig_nn, top5,
) -> str:
    lines = [
        "### Period",
        "",
        f"**{d0}** — **{d1}** · **{total:,}** items · **{span}** calendar days "
        f"(war days {w0}–{w1}) · news on **{active}** days.",
        "",
        "### Data quality",
        "",
        f"- High credibility (≥0.7): **{hs}**",
        f"- Multi-source: **{ms}**",
        f"- With coordinates / named place / message: **{wc}** / **{wg}** / **{wm}**",
        f"- Avg credibility (all / non-null): **{avg_sig}** / **{avg_sig_nn}**",
        "",
    ]
    if top5:
        lines += [
            "### Topics",
            "",
            top5,
            "",
        ]
    lines += [
        "> **Volume drop:** Around **23 Mar 2026** the daily count fell sharply (~78 %). "
        "Cause unknown (pipeline, sources, or events). Treat **late Mar — early Apr** with caution.",
        "",
        "---",
        "*Asia/Jerusalem. `echomap_dbt/docs/METHODOLOGY.md`.*",
    ]
    return "\n".join(lines)


# ---- Russian ---------------------------------------------------------------

def _narrative_ru(
    total, d0, d1, span, active, w0, w1,
    hs, ms, wc, wg, wm, avg_sig, avg_sig_nn, top5,
) -> str:
    lines = [
        "### Период",
        "",
        f"**{d0}** — **{d1}** · **{total:,}** записей · **{span}** календарных дней "
        f"(дни войны {w0}–{w1}) · новости в **{active}** днях.",
        "",
        "### Качество данных",
        "",
        f"- Высокая достоверность (≥0.7): **{hs}**",
        f"- Несколько источников: **{ms}**",
        f"- Координаты / название места / текст: **{wc}** / **{wg}** / **{wm}**",
        f"- Средняя достоверность (все / непустые): **{avg_sig}** / **{avg_sig_nn}**",
        "",
    ]
    if top5:
        lines += [
            "### Темы",
            "",
            top5,
            "",
        ]
    lines += [
        "> **Падение объёма:** **23 марта 2026** — резкое снижение (~78 %). Причина неизвестна. "
        "**Конец марта — начало апреля** — с осторожностью.",
        "",
        "---",
        "*Asia/Jerusalem. `echomap_dbt/docs/METHODOLOGY.md`.*",
    ]
    return "\n".join(lines)
