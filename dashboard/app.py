"""
EchoMap / GeoNews — analytics dashboard (Streamlit).

Run from this folder:
  pip install -r requirements.txt
  streamlit run app.py
"""

from __future__ import annotations

import os
import tomllib
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from db import load_all_marts
from i18n import (
    LANGS,
    SENTIMENT_COLORS,
    col_rename,
    fmt_int,
    fmt_pct,
    quality_rename,
    t,
)
from narrative import war_period_narrative

st.set_page_config(
    page_title="EchoMap Analytics",
    layout="wide",
    initial_sidebar_state="expanded",
)

LOC_LIMIT = int(os.environ.get("ECHOMAP_DASH_LOC_LIMIT", "350"))
CACHE_TTL = int(os.environ.get("ECHOMAP_DASH_CACHE_SEC", "600"))
HEATMAP_MAX_DAYS = 45

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _lang() -> str:
    return st.session_state.get("lang", "en")


def _streamlit_theme_base() -> str:
    """Match charts/metric CSS to `.streamlit/config.toml` ([theme] base)."""
    cfg = Path(__file__).resolve().parent / ".streamlit" / "config.toml"
    try:
        data = tomllib.loads(cfg.read_text(encoding="utf-8"))
        return str(data.get("theme", {}).get("base", "light")).strip().lower()
    except (OSError, UnicodeDecodeError, TypeError, tomllib.TOMLDecodeError):
        return "light"


def _charts_dark() -> bool:
    return _streamlit_theme_base() == "dark"


def _style_fig(
    fig: go.Figure,
    height: int = 400,
    *,
    margin_top: int | None = None,
    legend_y: float | None = None,
) -> go.Figure:
    mt = 36 if margin_top is None else margin_top
    ly = 1.02 if legend_y is None else legend_y
    if _charts_dark():
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="#161b22",
            font=dict(family="system-ui, -apple-system, sans-serif", size=13, color="#e6edf3"),
            margin=dict(l=56, r=28, t=mt, b=48),
            height=height,
            hoverlabel=dict(
                bgcolor="#30363d",
                font_size=13,
                font_family="system-ui",
                font_color="#f0f6fc",
            ),
            xaxis=dict(showgrid=True, gridcolor="#30363d", zeroline=False, color="#8b949e"),
            yaxis=dict(showgrid=True, gridcolor="#30363d", zeroline=False, color="#8b949e"),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=ly,
                xanchor="right",
                x=1,
                font=dict(color="#e6edf3"),
                bgcolor="rgba(22,27,34,0.9)",
            ),
        )
    else:
        fig.update_layout(
            template="plotly_white",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="#f7f9fb",
            font=dict(family="system-ui, -apple-system, sans-serif", size=13, color="#1c2330"),
            margin=dict(l=56, r=28, t=mt, b=48),
            height=height,
            hoverlabel=dict(bgcolor="white", font_size=13, font_family="system-ui"),
            xaxis=dict(showgrid=True, gridcolor="#e2e8f0", zeroline=False),
            yaxis=dict(showgrid=True, gridcolor="#e2e8f0", zeroline=False),
            legend=dict(orientation="h", yanchor="bottom", y=ly, xanchor="right", x=1),
        )
    return fig


@st.cache_data(ttl=CACHE_TTL, show_spinner="Loading data…")
def _cached_bundle() -> dict[str, pd.DataFrame]:
    return load_all_marts(location_limit=LOC_LIMIT)


def _inject_css() -> None:
    dark = _charts_dark()
    metric_block = (
        """
        div[data-testid="stMetricContainer"],
        div[data-testid="stMetric"] {
            background-color: #0e1117 !important;
            background-image: none !important;
            border: 1px solid rgba(255, 255, 255, 0.12) !important;
            border-radius: 12px !important;
            padding: 14px 16px !important;
            box-shadow: none !important;
        }
        div[data-testid="stMetricContainer"] { padding: 0 !important; }
        div[data-testid="stMetric"] * {
            background-color: transparent !important;
            background-image: none !important;
            box-shadow: none !important;
        }
        div[data-testid="stMetric"] {
            background-color: #0e1117 !important;
        }
        div[data-testid="stMetric"] label,
        div[data-testid="stMetric"] label p,
        div[data-testid="stMetric"] [data-testid="stMarkdownContainer"] p,
        div[data-testid="stMetric"] [data-testid="stMarkdownContainer"] span,
        div[data-testid="stMetricValue"],
        div[data-testid="stMetric"] [data-testid="stMetricValue"] {
            color: #fafafa !important;
        }
        div[data-testid="stMetric"] [data-testid="stMetricLabel"] p,
        div[data-testid="stMetric"] [data-testid="stMetricLabel"] {
            color: rgba(250, 250, 250, 0.72) !important;
        }
        """
        if dark
        else """
        div[data-testid="stMetric"] {
            background-color: var(--background-color, #ffffff) !important;
            background-image: none !important;
            border: 1px solid color-mix(in srgb, var(--text-color, #1a1a2e) 18%, transparent) !important;
            border-radius: 12px !important;
            padding: 14px 16px !important;
        }
        div[data-testid="stMetric"] > div,
        div[data-testid="stMetric"] > div > div {
            background-color: transparent !important;
            background-image: none !important;
            background: transparent !important;
        }
        div[data-testid="stMetric"] label,
        div[data-testid="stMetric"] label p,
        div[data-testid="stMetric"] [data-testid="stMarkdownContainer"] p,
        div[data-testid="stMetric"] [data-testid="stMarkdownContainer"] span,
        div[data-testid="stMetricValue"],
        div[data-testid="stMetric"] [data-testid="stMetricValue"] {
            color: var(--text-color, #1a1a2e) !important;
        }
        div[data-testid="stMetric"] [data-testid="stMetricLabel"] p,
        div[data-testid="stMetric"] [data-testid="stMetricLabel"] {
            color: color-mix(in srgb, var(--text-color, #1a1a2e) 80%, transparent) !important;
        }
        """
    )
    st.markdown(
        f"""
        <style>
        .main .block-container {{ padding-top: 1rem; padding-bottom: 2.5rem; max-width: 1200px; }}
        .main h1 {{ font-weight: 700; letter-spacing: -0.035em; color: var(--text-color, #0b1220); font-size: 2rem; }}
        .main h3 {{ font-weight: 650; color: var(--text-color, #0f172a); letter-spacing: -0.02em; margin-top: 1.25rem; }}
        {metric_block}
        .hero-wrap {{
            background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 55%, #0f172a 100%);
            color: #f8fafc;
            border-radius: 16px;
            padding: 1.35rem 1.5rem 1.2rem;
            margin-bottom: 1rem;
            box-shadow: 0 12px 40px rgba(15, 23, 42, 0.18);
        }}
        .hero-kicker {{
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.14em;
            opacity: 0.78;
            margin-bottom: 0.6rem;
        }}
        .hero-line {{ font-size: 1.05rem; line-height: 1.45; margin: 0.15rem 0; }}
        .hero-line.secondary {{ opacity: 0.92; font-size: 0.98rem; margin-top: 0.5rem; }}
        .hero-big {{
            font-size: clamp(2rem, 4vw, 2.75rem);
            font-weight: 750;
            letter-spacing: -0.03em;
            margin-right: 0.35rem;
        }}
        .hero-mid {{ font-weight: 500; opacity: 0.95; }}
        .hero-insight {{
            margin-top: 0.85rem;
            padding-top: 0.75rem;
            border-top: 1px solid rgba(248, 250, 252, 0.22);
            font-size: 0.95rem;
            line-height: 1.4;
        }}
        .hero-insight .decline {{ color: #fecaca; }}
        .insight-title {{ font-size: 1.25rem; font-weight: 650; color: var(--text-color, #0f172a); margin: 0 0 0.2rem 0; letter-spacing: -0.02em; }}
        .insight-caption {{ color: var(--text-color, #64748b); opacity: 0.75; font-size: 0.88rem; margin: 0 0 0.6rem 0; }}
        .product-subtitle {{ color: var(--text-color, #64748b); opacity: 0.8; font-size: 1rem; margin-top: -0.35rem; margin-bottom: 0.75rem; }}
        .tooltip-icon {{
            display: inline-block;
            width: 18px; height: 18px;
            border-radius: 50%;
            background: color-mix(in srgb, var(--text-color, #475569) 12%, transparent);
            color: var(--text-color, #475569);
            font-size: 12px;
            text-align: center;
            line-height: 18px;
            cursor: help;
            margin-left: 4px;
            vertical-align: middle;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _filter_days(
    df: pd.DataFrame, date_from, date_to, col: str = "published_date_il",
) -> pd.DataFrame:
    if df is None or df.empty:
        return df
    days = pd.to_datetime(df[col]).dt.date
    return df[(days >= date_from) & (days <= date_to)].copy()


def _human_df(df: pd.DataFrame, lang: str) -> pd.DataFrame:
    """Rename columns to human-readable labels for display."""
    renames = col_rename(lang)
    return df.rename(columns={c: renames.get(c, c) for c in df.columns})


def _empty(msg_key: str = "empty_no_data") -> None:
    lang = _lang()
    st.info(t(msg_key, lang))


def _plotly_cfg() -> dict:
    return {"displayModeBar": "hover"}


_DROP_THRESHOLD = -0.55  # -55 % day-over-day

def _detect_collection_gap(daily: pd.DataFrame) -> dict | None:
    """Find the biggest single-day percentage drop exceeding the threshold.

    Excludes the last 2 rows — the tail of the analytics window almost always
    has partial data and is not a real collection gap.
    """
    if len(daily) < 4:
        return None
    df = daily.sort_values("published_date_il").copy()
    df = df.iloc[:-2]  # drop last 2 days (edge of analytics window)
    df["_prev"] = df["news_count"].shift(1)
    df["_pct"] = (df["news_count"] - df["_prev"]) / df["_prev"]
    candidates = df.dropna(subset=["_pct"])
    candidates = candidates[candidates["_pct"] <= _DROP_THRESHOLD]
    if candidates.empty:
        return None
    worst = candidates.loc[candidates["_pct"].idxmin()]
    return {
        "date": worst["published_date_il"],
        "before": int(worst["_prev"]),
        "after": int(worst["news_count"]),
        "pct": f"{abs(worst['_pct']) * 100:.0f} %",
    }


def _rollup_categories(
    totals: pd.DataFrame,
    name_col: str,
    value_col: str,
    top_n: int,
    other_label: str,
) -> pd.DataFrame:
    """Keep top_n categories by volume; merge the rest into *other_label*."""
    if totals.empty:
        return totals
    tdf = totals.sort_values(value_col, ascending=False).reset_index(drop=True)
    if len(tdf) <= top_n:
        return tdf
    head = tdf.head(top_n).copy()
    rest_sum = int(tdf.iloc[top_n:][value_col].sum())
    if rest_sum > 0:
        head = pd.concat(
            [head, pd.DataFrame([{name_col: other_label, value_col: rest_sum}])],
            ignore_index=True,
        )
    return head


def _hero_block(bundle: dict[str, pd.DataFrame], daily: pd.DataFrame, lang: str) -> None:
    war_summary = bundle.get("war_summary")
    if war_summary is None or war_summary.empty:
        return
    row = war_summary.iloc[0]
    total = int(row["total_news"])
    span = int(row["calendar_days_span"])
    loc = bundle.get("locations", pd.DataFrame())
    places: list[str] = []
    if loc is not None and not loc.empty and "geoname" in loc.columns:
        places = loc.head(3)["geoname"].astype(str).tolist()
    places_str = " · ".join(places) if places else "—"

    gap = _detect_collection_gap(daily)
    gap_line = ""
    if gap:
        pct = str(gap["pct"]).replace(" ", "")
        gap_line = (
            f'<div class="hero-insight decline">📉 {t("hero_drop", lang, date=gap["date"], pct=pct)}</div>'
        )

    st.markdown(
        f"""
        <div class="hero-wrap">
          <div class="hero-kicker">{t("hero_kicker", lang)}</div>
          <div class="hero-line">
            <span class="hero-big">{fmt_int(total)}</span>
            <span class="hero-mid">{t("hero_events", lang)} · {span} {t("metric_calendar_days", lang).lower()}</span>
          </div>
          <div class="hero-line secondary">📍 {t("hero_places", lang)}: <strong>{places_str}</strong></div>
          {gap_line}
        </div>
        """,
        unsafe_allow_html=True,
    )


def _insight_heading(title_key: str, caption_key: str) -> None:
    lang = _lang()
    st.markdown(f'<p class="insight-title">{t(title_key, lang)}</p>', unsafe_allow_html=True)
    st.markdown(
        f'<p class="insight-caption">{t(caption_key, lang)}</p>',
        unsafe_allow_html=True,
    )


def _locations_map_figure(loc_top: pd.DataFrame, height: int = 480) -> go.Figure | None:
    if loc_top.empty:
        return None
    if loc_top["final_lat"].isna().all():
        return None
    max_count = loc_top["news_count"].max()
    df = loc_top.copy()
    df["_size"] = (df["news_count"] / max_count * 40 + 5) if max_count and max_count > 0 else 10
    fig = px.scatter_map(
        df,
        lat="final_lat",
        lon="final_lon",
        size="_size",
        color="news_count",
        color_continuous_scale="YlOrRd",
        hover_name="geoname",
        hover_data={
            "news_count": True,
            "coordinate_source": True,
            "_size": False,
            "final_lat": ":.4f",
            "final_lon": ":.4f",
        },
        zoom=6,
        height=height,
    )
    map_style = "carto-darkmatter" if _charts_dark() else "open-street-map"
    fig.update_layout(map_style=map_style, margin=dict(l=0, r=0, t=8, b=0))
    return fig


def _chart_daily_volume_fig(daily_f: pd.DataFrame, lang: str, height: int = 400) -> go.Figure | None:
    if daily_f.empty:
        return None
    cr = col_rename(lang)
    fig = px.line(
        daily_f,
        x="published_date_il",
        y="news_count",
        markers=True,
        labels={
            "published_date_il": cr.get("published_date_il", "Date"),
            "news_count": cr.get("news_count", "News"),
        },
    )
    fig.update_traces(line=dict(width=2.5), marker=dict(size=6))
    gap = _detect_collection_gap(daily_f)
    if gap:
        gap_x = str(gap["date"])
        fig.add_shape(
            type="line",
            x0=gap_x,
            x1=gap_x,
            y0=0,
            y1=1,
            yref="y domain",
            line=dict(width=2, dash="dash", color="#ef4444"),
        )
        fig.add_annotation(
            x=gap_x,
            y=1,
            yref="y domain",
            text=t("volume_drop_annotation", lang),
            showarrow=False,
            font=dict(size=12, color="#ef4444"),
            xanchor="left",
            yanchor="top",
            xshift=6,
        )
    _style_fig(fig, height=height)
    return fig


def _chart_how_coverage_fig(
    sent_f: pd.DataFrame,
    cat_totals: pd.DataFrame,
    lang: str,
    *,
    roll_top_n: int = 5,
    height: int = 520,
) -> go.Figure | None:
    """Sentiment over time + rolled topic mix when both exist (one composite figure)."""
    cr = col_rename(lang)
    other = t("category_other", lang)
    has_s = sent_f is not None and not sent_f.empty
    has_c = cat_totals is not None and not cat_totals.empty
    if not has_s and not has_c:
        return None

    if has_s and not has_c:
        fig = px.area(
            sent_f,
            x="published_date_il",
            y="news_count",
            color="sentiment_clean",
            color_discrete_map=SENTIMENT_COLORS,
            labels={
                "published_date_il": cr.get("published_date_il", "Date"),
                "news_count": cr.get("news_count", "News"),
                "sentiment_clean": cr.get("sentiment_clean", "Sentiment"),
            },
        )
        _style_fig(fig, height=height)
        return fig

    if has_c and not has_s:
        rolled = _rollup_categories(
            cat_totals, "category_clean", "news_count", roll_top_n, other,
        ).sort_values("news_count", ascending=True)
        fig = px.bar(
            rolled,
            x="news_count",
            y="category_clean",
            orientation="h",
            labels={
                "news_count": cr.get("news_count", "News"),
                "category_clean": "",
            },
            color="news_count",
            color_continuous_scale="Blues",
        )
        fig.update_layout(coloraxis_showscale=False, yaxis=dict(categoryorder="total ascending"))
        _style_fig(fig, height=min(120 + len(rolled) * 28, height))
        return fig

    fig = make_subplots(
        rows=2,
        cols=1,
        row_heights=[0.62, 0.38],
        vertical_spacing=0.11,
        subplot_titles=(
            t("chart_sentiment_daily", lang),
            t("chart_categories", lang),
        ),
    )
    for sentiment, sub in sent_f.groupby("sentiment_clean"):
        sub = sub.sort_values("published_date_il")
        fig.add_trace(
            go.Scatter(
                x=sub["published_date_il"],
                y=sub["news_count"],
                name=sentiment,
                stackgroup="one",
                mode="lines",
                line=dict(width=0.5),
                fillcolor=SENTIMENT_COLORS.get(sentiment, "#94a3b8"),
                hovertemplate="%{x}<br>%{fullData.name}: %{y:,}<extra></extra>",
            ),
            row=1,
            col=1,
        )

    rolled = _rollup_categories(
        cat_totals, "category_clean", "news_count", roll_top_n, other,
    ).sort_values("news_count", ascending=True)
    bar_color = "#58a6ff" if _charts_dark() else "#2563eb"
    fig.add_trace(
        go.Bar(
            x=rolled["news_count"],
            y=rolled["category_clean"],
            orientation="h",
            marker_color=bar_color,
            hovertemplate="%{y}: %{x:,}<extra></extra>",
            showlegend=False,
        ),
        row=2,
        col=1,
    )

    fig.update_xaxes(title_text=cr.get("published_date_il", "Date"), row=1, col=1)
    fig.update_yaxes(title_text=cr.get("news_count", "News"), row=1, col=1)
    fig.update_xaxes(title_text=cr.get("news_count", "News"), row=2, col=1)
    fig.update_yaxes(title_text="", row=2, col=1)
    _style_fig(fig, height, margin_top=56, legend_y=1.08)
    return fig


def _render_insight_map(
    bundle: dict[str, pd.DataFrame],
    top_n_loc: int,
    lang: str,
    *,
    show_table: bool,
    chart_key: str,
) -> None:
    loc = bundle["locations"]
    if loc.empty:
        _empty("empty_run_dbt")
        return
    loc_top = loc.head(top_n_loc).copy()
    fig = _locations_map_figure(loc_top, height=480)
    if fig is None:
        _empty()
        return
    st.plotly_chart(fig, use_container_width=True, config=_plotly_cfg(), key=chart_key)
    if not show_table:
        return
    display_cols = ["geoname", "news_count", "coordinate_source", "final_lat", "final_lon"]
    existing = [c for c in display_cols if c in loc_top.columns]
    st.dataframe(
        _human_df(loc_top[existing], lang),
        use_container_width=True,
        height=min(360, 60 + len(loc_top) * 35),
        hide_index=True,
    )


def _render_three_insights(
    bundle: dict[str, pd.DataFrame],
    daily_f: pd.DataFrame,
    date_from,
    date_to,
    top_n_loc: int,
    lang: str,
    *,
    show_map_table: bool,
    roll_top_n: int,
    plotly_keys_prefix: str,
) -> None:
    st.caption(t("hero_charts_note", lang))

    _insight_heading("insight_where_title", "insight_where_caption")
    _render_insight_map(
        bundle,
        top_n_loc,
        lang,
        show_table=show_map_table,
        chart_key=f"{plotly_keys_prefix}_insight_map",
    )

    st.divider()
    _insight_heading("insight_when_title", "insight_when_caption")
    fig_d = _chart_daily_volume_fig(daily_f, lang, height=380)
    if fig_d:
        st.plotly_chart(
            fig_d,
            use_container_width=True,
            config=_plotly_cfg(),
            key=f"{plotly_keys_prefix}_insight_daily",
        )
        gap = _detect_collection_gap(daily_f)
        if gap:
            st.warning(t(
                "volume_drop_callout", lang,
                date=gap["date"], pct=gap["pct"],
                before=f"{gap['before']:,}", after=f"{gap['after']:,}",
            ))
    else:
        _empty()

    st.divider()
    _insight_heading("insight_how_title", "insight_how_caption")
    cat = bundle["category"]
    cat_f = _filter_days(cat, date_from, date_to)
    sent = bundle.get("sentiment", pd.DataFrame())
    sent_f = _filter_days(sent, date_from, date_to)
    cat_tot = (
        cat_f.groupby("category_clean", as_index=False)["news_count"].sum()
        if not cat_f.empty
        else pd.DataFrame(columns=["category_clean", "news_count"])
    )
    fig_h = _chart_how_coverage_fig(
        sent_f, cat_tot, lang, roll_top_n=roll_top_n, height=520,
    )
    if fig_h:
        st.plotly_chart(
            fig_h,
            use_container_width=True,
            config=_plotly_cfg(),
            key=f"{plotly_keys_prefix}_insight_how",
        )
    else:
        _empty()


def _page_viewer(
    bundle: dict[str, pd.DataFrame],
    daily: pd.DataFrame,
    daily_f: pd.DataFrame,
    date_from,
    date_to,
    top_n_loc: int,
    top_n_cat: int,
    lang: str,
) -> None:
    _hero_block(bundle, daily, lang)
    _render_three_insights(
        bundle,
        daily_f,
        date_from,
        date_to,
        top_n_loc,
        lang,
        show_map_table=False,
        roll_top_n=top_n_cat,
        plotly_keys_prefix="viewer",
    )


def _tab_overview(
    bundle: dict[str, pd.DataFrame],
    daily: pd.DataFrame,
    daily_f: pd.DataFrame,
    date_from,
    date_to,
    top_n_loc: int,
    top_n_cat: int,
) -> None:
    lang = _lang()
    _hero_block(bundle, daily, lang)
    _render_three_insights(
        bundle,
        daily_f,
        date_from,
        date_to,
        top_n_loc,
        lang,
        show_map_table=False,
        roll_top_n=top_n_cat,
        plotly_keys_prefix="overview",
    )


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

def _sidebar(daily: pd.DataFrame) -> tuple:
    """Render sidebar and return (date_from, date_to, top_n_cat, top_n_loc, top_n_src)."""
    lang = _lang()
    if "display_mode" not in st.session_state:
        st.session_state.display_mode = "viewer"

    with st.sidebar:
        st.radio(
            t("sidebar_mode", lang),
            ("viewer", "analyst"),
            key="display_mode",
            format_func=lambda x: t("mode_viewer", lang) if x == "viewer" else t("mode_analyst", lang),
        )

        st.selectbox(
            t("sidebar_language", lang),
            LANGS,
            index=LANGS.index(lang),
            key="lang",
            format_func=lambda x: {"en": "English", "ru": "Русский"}[x],
        )
        lang = _lang()

        st.markdown(f"### {t('sidebar_filters', lang)}")

        dmin = pd.Timestamp(daily["published_date_il"].min()).date()
        dmax = pd.Timestamp(daily["published_date_il"].max()).date()

        dr = st.date_input(
            t("sidebar_date_range", lang),
            value=(dmin, dmax),
            min_value=dmin,
            max_value=dmax,
        )
        top_n_cat = st.slider(t("sidebar_top_categories", lang), 5, 30, 12)
        top_n_loc = st.slider(
            t("sidebar_locations", lang), 10, min(200, LOC_LIMIT), min(50, LOC_LIMIT),
        )
        top_n_src = st.slider(t("sidebar_top_sources", lang), 4, 15, 8)
        st.caption(t("sidebar_loc_hint", lang, n=LOC_LIMIT))

    if isinstance(dr, tuple) and len(dr) == 2:
        date_from, date_to = dr
    else:
        date_from = date_to = dr
    return date_from, date_to, top_n_cat, top_n_loc, top_n_src


# ---------------------------------------------------------------------------
# Tab: Summary
# ---------------------------------------------------------------------------

def _section(title_key: str, explain_key: str | None = None) -> None:
    """Render a section header with optional explanatory text below it."""
    lang = _lang()
    st.markdown(f"##### {t(title_key, lang)}")
    if explain_key:
        st.markdown(
            f"<p style='color:#64748b;font-size:0.92rem;margin-top:-0.35rem;"
            f"margin-bottom:0.75rem;'>{t(explain_key, lang)}</p>",
            unsafe_allow_html=True,
        )


def _tab_summary(bundle: dict[str, pd.DataFrame]) -> None:
    lang = _lang()

    st.caption(t("intro_summary", lang))
    st.caption(t("summary_full_period_note", lang))

    war_summary = bundle.get("war_summary")
    top_cat_full = bundle.get("top_categories", pd.DataFrame())

    if war_summary is None or war_summary.empty:
        _empty("empty_run_dbt")
        return

    row = war_summary.iloc[0]

    st.markdown(war_period_narrative(row, top_cat_full, lang=lang, compact=False))

    k1, k2, k3 = st.columns(3)
    with k1:
        st.metric(t("metric_total_news", lang), fmt_int(row.get("total_news")))
    with k2:
        st.metric(t("metric_calendar_days", lang), fmt_int(row.get("calendar_days_span")))
    with k3:
        st.metric(t("metric_active_days", lang), fmt_int(row.get("distinct_news_days")))

    st.divider()
    c1, c2 = st.columns(2)

    sent_tot = bundle.get("sentiment", pd.DataFrame())
    if not sent_tot.empty:
        s_agg = sent_tot.groupby("sentiment_clean", as_index=False)["news_count"].sum()
        fig_sp = px.pie(
            s_agg,
            values="news_count",
            names="sentiment_clean",
            hole=0.35,
            color="sentiment_clean",
            color_discrete_map=SENTIMENT_COLORS,
        )
        _style_fig(fig_sp, height=360)
        fig_sp.update_layout(title=t("chart_sentiment_pie", lang))
        fig_sp.update_traces(
            hovertemplate="%{label}: %{value:,} (%{percent})<extra></extra>",
        )
        with c1:
            st.plotly_chart(
                fig_sp,
                use_container_width=True,
                config=_plotly_cfg(),
                key="summary_pie_sentiment",
            )
            st.caption(t("tip_sentiment", lang))

    cs_tot = bundle.get("coord_source", pd.DataFrame())
    if not cs_tot.empty:
        c_agg = cs_tot.groupby("coordinate_source", as_index=False)["news_count"].sum()
        fig_cp = px.pie(
            c_agg,
            values="news_count",
            names="coordinate_source",
            hole=0.35,
        )
        _style_fig(fig_cp, height=360)
        fig_cp.update_layout(title=t("chart_coord_pie", lang))
        fig_cp.update_traces(
            hovertemplate="%{label}: %{value:,} (%{percent})<extra></extra>",
        )
        with c2:
            st.plotly_chart(
                fig_cp,
                use_container_width=True,
                config=_plotly_cfg(),
                key="summary_pie_coord_source",
            )
            st.caption(t("tip_coordinate_source", lang))

    if not top_cat_full.empty:
        st.divider()
        st.markdown(f"##### {t('chart_top_categories_period', lang)}")
        st.dataframe(
            _human_df(top_cat_full.head(20), lang),
            use_container_width=True,
            height=320,
            hide_index=True,
        )


# ---------------------------------------------------------------------------
# Tab: Timeline (was Overview + Categories + Sentiment + Sources)
# ---------------------------------------------------------------------------

def _tab_timeline(
    bundle: dict[str, pd.DataFrame],
    daily_f: pd.DataFrame,
    date_from,
    date_to,
    top_n_cat: int,
    top_n_src: int,
) -> None:
    lang = _lang()

    st.caption(t("intro_timeline", lang))

    # -- KPIs row -----------------------------------------------------------
    k1, k2, k3 = st.columns(3)
    with k1:
        st.metric(t("metric_news_in_range", lang), fmt_int(daily_f["news_count"].sum()))
    with k2:
        avg_sig = daily_f["avg_signal_strength"].mean()
        val = f"{float(avg_sig):.3f}" if pd.notna(avg_sig) else "—"
        st.metric(t("metric_avg_signal", lang), val, help=t("tip_signal", lang))
    with k3:
        st.metric(t("metric_days_in_range", lang), fmt_int(len(daily_f)))

    # -- Daily volume -------------------------------------------------------
    st.divider()
    _section("chart_daily_volume", "explain_daily_volume")
    if daily_f.empty:
        _empty()
    else:
        cr = col_rename(lang)
        fig = px.line(
            daily_f,
            x="published_date_il",
            y="news_count",
            markers=True,
            labels={
                "published_date_il": cr.get("published_date_il", "Date"),
                "news_count": cr.get("news_count", "News"),
            },
        )
        fig.update_traces(line=dict(width=2.5), marker=dict(size=6))

        gap = _detect_collection_gap(daily_f)
        if gap:
            gap_x = str(gap["date"])
            fig.add_shape(
                type="line", x0=gap_x, x1=gap_x, y0=0, y1=1,
                yref="y domain", line=dict(width=2, dash="dash", color="#ef4444"),
            )
            fig.add_annotation(
                x=gap_x, y=1, yref="y domain",
                text=t("volume_drop_annotation", lang),
                showarrow=False, font=dict(size=12, color="#ef4444"),
                xanchor="left", yanchor="top", xshift=6,
            )

        _style_fig(fig, height=400)
        st.plotly_chart(
            fig,
            use_container_width=True,
            config=_plotly_cfg(),
            key="timeline_daily_volume",
        )

        if gap:
            st.warning(t(
                "volume_drop_callout", lang,
                date=gap["date"], pct=gap["pct"],
                before=f"{gap['before']:,}", after=f"{gap['after']:,}",
            ))

    # -- Quality mix --------------------------------------------------------
    share_cols = [
        c for c in ("high_signal_share", "multi_source_share", "with_coordinates_share")
        if c in daily_f.columns
    ]
    if share_cols and not daily_f.empty:
        st.divider()
        _section("chart_quality_mix", "explain_quality_mix")
        qr = quality_rename(lang)
        daily_s = daily_f.rename(columns={k: qr.get(k, k) for k in share_cols})
        fig2 = px.line(
            daily_s,
            x="published_date_il",
            y=[qr.get(c, c) for c in share_cols],
            labels={
                "published_date_il": cr.get("published_date_il", "Date"),
                "value": fmt_pct.__name__,
                "variable": "",
            },
        )
        fig2.update_traces(mode="lines+markers", marker=dict(size=4))
        _style_fig(fig2, height=360)
        st.plotly_chart(
            fig2,
            use_container_width=True,
            config=_plotly_cfg(),
            key="timeline_quality_mix",
        )

    # -- Categories bar -----------------------------------------------------
    st.divider()
    cat = bundle["category"]
    cat_f = _filter_days(cat, date_from, date_to)
    _section("chart_categories", "explain_categories")
    if cat_f.empty:
        _empty()
    else:
        totals = (
            cat_f.groupby("category_clean", as_index=False)["news_count"]
            .sum()
            .sort_values("news_count", ascending=False)
        )
        other_l = t("category_other", lang)
        top = _rollup_categories(totals, "category_clean", "news_count", top_n_cat, other_l)
        fig_c = px.bar(
            top,
            x="news_count",
            y="category_clean",
            orientation="h",
            labels={
                "news_count": col_rename(lang).get("news_count", "News"),
                "category_clean": "",
            },
            color="news_count",
            color_continuous_scale="Blues",
        )
        fig_c.update_layout(coloraxis_showscale=False, yaxis=dict(categoryorder="total ascending"))
        _style_fig(fig_c, height=min(120 + top_n_cat * 28, 640))
        st.plotly_chart(
            fig_c,
            use_container_width=True,
            config=_plotly_cfg(),
            key="timeline_categories_bar",
        )

    # -- Sentiment stacked area ---------------------------------------------
    st.divider()
    sent = bundle.get("sentiment", pd.DataFrame())
    sent_f = _filter_days(sent, date_from, date_to)
    _section("chart_sentiment_daily", "explain_sentiment")
    if sent_f.empty:
        _empty()
    else:
        fig_s = px.area(
            sent_f,
            x="published_date_il",
            y="news_count",
            color="sentiment_clean",
            color_discrete_map=SENTIMENT_COLORS,
            labels={
                "published_date_il": col_rename(lang).get("published_date_il", "Date"),
                "news_count": col_rename(lang).get("news_count", "News"),
                "sentiment_clean": col_rename(lang).get("sentiment_clean", "Sentiment"),
            },
        )
        _style_fig(fig_s, height=400)
        st.plotly_chart(
            fig_s,
            use_container_width=True,
            config=_plotly_cfg(),
            key="timeline_sentiment_area",
        )

    # -- Data sources stacked area ------------------------------------------
    st.divider()
    dsrc = bundle.get("data_source", pd.DataFrame())
    dsrc_f = _filter_days(dsrc, date_from, date_to)
    _section("chart_sources_daily", "explain_sources")
    if dsrc_f.empty:
        _empty()
    else:
        top_labels = (
            dsrc_f.groupby("data_source_clean")["news_count"]
            .sum()
            .sort_values(ascending=False)
            .head(top_n_src)
            .index
        )
        dsub = dsrc_f[dsrc_f["data_source_clean"].isin(top_labels)]
        fig_d = px.area(
            dsub,
            x="published_date_il",
            y="news_count",
            color="data_source_clean",
            labels={
                "published_date_il": col_rename(lang).get("published_date_il", "Date"),
                "news_count": col_rename(lang).get("news_count", "News"),
                "data_source_clean": col_rename(lang).get("data_source_clean", "Source"),
            },
        )
        _style_fig(fig_d, height=400)
        st.plotly_chart(
            fig_d,
            use_container_width=True,
            config=_plotly_cfg(),
            key="timeline_data_sources_area",
        )

    # -- Coordinate pipeline ------------------------------------------------
    st.divider()
    csrc = bundle.get("coord_source", pd.DataFrame())
    csrc_f = _filter_days(csrc, date_from, date_to)
    _section("chart_coord_pipeline", "explain_coord_pipeline")
    if csrc_f.empty:
        _empty()
    else:
        fig_cc = px.area(
            csrc_f,
            x="published_date_il",
            y="news_count",
            color="coordinate_source",
            labels={
                "published_date_il": col_rename(lang).get("published_date_il", "Date"),
                "news_count": col_rename(lang).get("news_count", "News"),
                "coordinate_source": col_rename(lang).get("coordinate_source", "Source"),
            },
        )
        _style_fig(fig_cc, height=380)
        st.plotly_chart(
            fig_cc,
            use_container_width=True,
            config=_plotly_cfg(),
            key="timeline_coord_pipeline_area",
        )

    st.divider()
    with st.expander(t("expander_raw_data", lang)):
        st.dataframe(
            _human_df(daily_f, lang), use_container_width=True, height=280, hide_index=True,
        )


# ---------------------------------------------------------------------------
# Tab: Hourly patterns
# ---------------------------------------------------------------------------

def _tab_hourly(bundle: dict[str, pd.DataFrame], date_from, date_to) -> None:
    lang = _lang()

    st.caption(t("intro_hourly", lang))

    hourly = bundle["hourly"]
    hourly_f = _filter_days(hourly, date_from, date_to)

    _section("chart_heatmap", "explain_heatmap")

    if hourly_f.empty:
        _empty()
        return

    n_days = hourly_f["published_date_il"].nunique()
    use_weekly = n_days > HEATMAP_MAX_DAYS
    hf = hourly_f.copy()

    if use_weekly:
        d = pd.to_datetime(hf["published_date_il"])
        hf["week_start"] = (d - pd.to_timedelta(d.dt.dayofweek, unit="d")).dt.date
        pivot = hf.pivot_table(
            index="week_start",
            columns="published_hour_il",
            values="news_count",
            aggfunc="sum",
            fill_value=0,
        ).sort_index()
        st.caption(t("heatmap_weekly_note", lang, n=n_days))
    else:
        pivot = hf.pivot_table(
            index="published_date_il",
            columns="published_hour_il",
            values="news_count",
            aggfunc="sum",
            fill_value=0,
        ).sort_index()

    cr = col_rename(lang)
    fig_h = px.imshow(
        pivot,
        labels=dict(
            x=cr.get("published_hour_il", "Hour"),
            y=cr.get("published_date_il", "Date"),
            color=cr.get("news_count", "News"),
        ),
        aspect="auto",
        color_continuous_scale="Blues",
    )
    h_heat = min(420 + len(pivot.index) * 10, 900)
    _style_fig(fig_h, height=h_heat)
    st.plotly_chart(
        fig_h,
        use_container_width=True,
        config=_plotly_cfg(),
        key="hourly_heatmap",
    )

    # Average bar by hour
    st.divider()
    _section("chart_hourly_avg", "explain_hourly_avg")
    avg_by_hour = (
        hourly_f.groupby("published_hour_il", as_index=False)["news_count"]
        .mean()
        .rename(columns={"news_count": "avg_news"})
    )
    fig_bar = px.bar(
        avg_by_hour,
        x="published_hour_il",
        y="avg_news",
        labels={
            "published_hour_il": cr.get("published_hour_il", "Hour"),
            "avg_news": cr.get("news_count", "News"),
        },
        color="avg_news",
        color_continuous_scale="Blues",
    )
    fig_bar.update_layout(coloraxis_showscale=False)
    _style_fig(fig_bar, height=340)
    st.plotly_chart(
        fig_bar,
        use_container_width=True,
        config=_plotly_cfg(),
        key="hourly_avg_bar",
    )

    with st.expander(t("expander_raw_data", lang)):
        st.dataframe(
            _human_df(hourly_f, lang),
            use_container_width=True,
            height=260,
            hide_index=True,
        )


# ---------------------------------------------------------------------------
# Tab: Geography
# ---------------------------------------------------------------------------

def _tab_geography(bundle: dict[str, pd.DataFrame], top_n_loc: int) -> None:
    lang = _lang()
    st.caption(t("intro_geography", lang))
    _section("chart_top_locations", "explain_map")
    _render_insight_map(
        bundle, top_n_loc, lang, show_table=True, chart_key="geography_map",
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    _inject_css()

    if "lang" not in st.session_state:
        st.session_state["lang"] = "en"

    try:
        bundle = _cached_bundle()
    except Exception as e:
        st.error(t("error_db", _lang()))
        st.code(str(e), language="text")
        st.stop()

    daily = bundle["daily"]
    if daily.empty:
        st.warning(t("empty_run_dbt", _lang()))
        st.stop()

    date_from, date_to, top_n_cat, top_n_loc, top_n_src = _sidebar(daily)
    lang = _lang()
    mode = st.session_state.get("display_mode", "viewer")

    st.title(t("main_title", lang))
    st.markdown(
        f"<p class='product-subtitle'>{t('subtitle', lang)}</p>",
        unsafe_allow_html=True,
    )
    if mode == "analyst":
        st.caption(t("intro_blurb_analyst", lang))

    day_series = pd.to_datetime(daily["published_date_il"]).dt.date
    mask = (day_series >= date_from) & (day_series <= date_to)
    daily_f = daily.loc[mask].copy()

    if mode == "viewer":
        _page_viewer(
            bundle, daily, daily_f, date_from, date_to, top_n_loc, top_n_cat, lang,
        )
        return

    tabs = st.tabs([
        t("tab_overview", lang),
        t("tab_geography", lang),
        t("tab_timeline", lang),
        t("tab_hourly", lang),
        t("tab_summary", lang),
    ])

    with tabs[0]:
        _tab_overview(
            bundle, daily, daily_f, date_from, date_to, top_n_loc, top_n_cat,
        )

    with tabs[1]:
        _tab_geography(bundle, top_n_loc)

    with tabs[2]:
        _tab_timeline(bundle, daily_f, date_from, date_to, top_n_cat, top_n_src)

    with tabs[3]:
        _tab_hourly(bundle, date_from, date_to)

    with tabs[4]:
        _tab_summary(bundle)


if __name__ == "__main__":
    main()
