"""
EchoMap / GeoNews — analytics dashboard (Streamlit).

Run from this folder:
  pip install -r requirements.txt
  streamlit run app.py
"""

from __future__ import annotations

import os

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

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


def _style_fig(fig: go.Figure, height: int = 400) -> go.Figure:
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#f7f9fb",
        font=dict(family="system-ui, -apple-system, sans-serif", size=13, color="#1c2330"),
        margin=dict(l=56, r=28, t=36, b=48),
        height=height,
        hoverlabel=dict(bgcolor="white", font_size=13, font_family="system-ui"),
        xaxis=dict(showgrid=True, gridcolor="#e2e8f0", zeroline=False),
        yaxis=dict(showgrid=True, gridcolor="#e2e8f0", zeroline=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig


@st.cache_data(ttl=CACHE_TTL, show_spinner="Loading data…")
def _cached_bundle() -> dict[str, pd.DataFrame]:
    return load_all_marts(location_limit=LOC_LIMIT)


def _inject_css() -> None:
    st.markdown(
        """
        <style>
        .main .block-container { padding-top: 1.5rem; padding-bottom: 2rem; max-width: 1180px; }
        h1 { font-weight: 650; letter-spacing: -0.03em; color: #0f172a; }
        div[data-testid="stMetric"] {
            background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 14px 16px;
        }
        .tooltip-icon {
            display: inline-block;
            width: 18px; height: 18px;
            border-radius: 50%;
            background: #e2e8f0;
            color: #475569;
            font-size: 12px;
            text-align: center;
            line-height: 18px;
            cursor: help;
            margin-left: 4px;
            vertical-align: middle;
        }
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


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

def _sidebar(daily: pd.DataFrame) -> tuple:
    """Render sidebar and return (date_from, date_to, top_n_cat, top_n_loc, top_n_src)."""
    lang = _lang()
    with st.sidebar:
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

def _tab_summary(bundle: dict[str, pd.DataFrame]) -> None:
    lang = _lang()

    st.caption(t("summary_full_period_note", lang))

    war_summary = bundle.get("war_summary")
    top_cat_full = bundle.get("top_categories", pd.DataFrame())

    if war_summary is None or war_summary.empty:
        _empty("empty_run_dbt")
        return

    row = war_summary.iloc[0]

    st.markdown(war_period_narrative(row, top_cat_full, lang=lang))

    k1, k2, k3 = st.columns(3)
    with k1:
        st.metric(t("metric_total_news", lang), fmt_int(row.get("total_news")))
    with k2:
        st.metric(t("metric_calendar_days", lang), fmt_int(row.get("calendar_days_span")))
    with k3:
        st.metric(t("metric_active_days", lang), fmt_int(row.get("distinct_news_days")))

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
            st.plotly_chart(fig_sp, use_container_width=True, config=_plotly_cfg())
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
            st.plotly_chart(fig_cp, use_container_width=True, config=_plotly_cfg())
            st.caption(t("tip_coordinate_source", lang))

    if not top_cat_full.empty:
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
    st.markdown(f"##### {t('chart_daily_volume', lang)}")
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
        _style_fig(fig, height=400)
        st.plotly_chart(fig, use_container_width=True, config=_plotly_cfg())

    # -- Quality mix --------------------------------------------------------
    share_cols = [
        c for c in ("high_signal_share", "multi_source_share", "with_coordinates_share")
        if c in daily_f.columns
    ]
    if share_cols and not daily_f.empty:
        st.markdown(f"##### {t('chart_quality_mix', lang)}")
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
        st.plotly_chart(fig2, use_container_width=True, config=_plotly_cfg())
        st.caption(
            f"{t('tip_high_signal', lang)} · {t('tip_multi_source', lang)} · {t('tip_with_coords', lang)}"
        )

    # -- Categories bar -----------------------------------------------------
    cat = bundle["category"]
    cat_f = _filter_days(cat, date_from, date_to)
    st.markdown(f"##### {t('chart_categories', lang)}")
    if cat_f.empty:
        _empty()
    else:
        totals = (
            cat_f.groupby("category_clean", as_index=False)["news_count"]
            .sum()
            .sort_values("news_count", ascending=False)
        )
        top = totals.head(top_n_cat)
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
        st.plotly_chart(fig_c, use_container_width=True, config=_plotly_cfg())
        st.caption(t("tip_category", lang))

    # -- Sentiment stacked area ---------------------------------------------
    sent = bundle.get("sentiment", pd.DataFrame())
    sent_f = _filter_days(sent, date_from, date_to)
    st.markdown(f"##### {t('chart_sentiment_daily', lang)}")
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
        st.plotly_chart(fig_s, use_container_width=True, config=_plotly_cfg())
        st.caption(t("tip_sentiment", lang))

    # -- Data sources stacked area ------------------------------------------
    dsrc = bundle.get("data_source", pd.DataFrame())
    dsrc_f = _filter_days(dsrc, date_from, date_to)
    st.markdown(f"##### {t('chart_sources_daily', lang)}")
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
        st.plotly_chart(fig_d, use_container_width=True, config=_plotly_cfg())

    # -- Coordinate pipeline ------------------------------------------------
    csrc = bundle.get("coord_source", pd.DataFrame())
    csrc_f = _filter_days(csrc, date_from, date_to)
    st.markdown(f"##### {t('chart_coord_pipeline', lang)}")
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
        st.plotly_chart(fig_cc, use_container_width=True, config=_plotly_cfg())
        st.caption(t("tip_coordinate_source", lang))

    with st.expander(t("expander_raw_data", lang)):
        st.dataframe(
            _human_df(daily_f, lang), use_container_width=True, height=280, hide_index=True,
        )


# ---------------------------------------------------------------------------
# Tab: Hourly patterns
# ---------------------------------------------------------------------------

def _tab_hourly(bundle: dict[str, pd.DataFrame], date_from, date_to) -> None:
    lang = _lang()

    hourly = bundle["hourly"]
    hourly_f = _filter_days(hourly, date_from, date_to)

    st.markdown(f"##### {t('chart_heatmap', lang)}")

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
    st.plotly_chart(fig_h, use_container_width=True, config=_plotly_cfg())

    # Average bar by hour
    st.markdown(f"##### {t('chart_hourly_avg', lang)}")
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
    st.plotly_chart(fig_bar, use_container_width=True, config=_plotly_cfg())

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
    loc = bundle["locations"]

    st.markdown(f"##### {t('chart_top_locations', lang)}")

    if loc.empty:
        _empty("empty_run_dbt")
        return

    loc_top = loc.head(top_n_loc).copy()

    if loc_top["final_lat"].isna().all():
        _empty()
        return

    max_count = loc_top["news_count"].max()
    loc_top["_size"] = (
        loc_top["news_count"] / max_count * 40 + 5
    ) if max_count > 0 else 10

    fig_map = px.scatter_map(
        loc_top,
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
        height=520,
    )
    fig_map.update_layout(
        map_style="open-street-map",
        margin=dict(l=0, r=0, t=0, b=0),
    )
    st.plotly_chart(fig_map, use_container_width=True, config=_plotly_cfg())
    st.caption(t("tip_coordinate_source", lang))

    display_cols = ["geoname", "news_count", "coordinate_source", "final_lat", "final_lon"]
    existing = [c for c in display_cols if c in loc_top.columns]
    st.dataframe(
        _human_df(loc_top[existing], lang),
        use_container_width=True,
        height=min(360, 60 + len(loc_top) * 35),
        hide_index=True,
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

    st.title(t("main_title", lang))
    st.markdown(
        f"<p style='color:#64748b;font-size:1.05rem;margin-top:-0.5rem;"
        f"margin-bottom:0.25rem;'>{t('subtitle', lang)}</p>",
        unsafe_allow_html=True,
    )
    st.markdown(t("intro_blurb", lang))

    day_series = pd.to_datetime(daily["published_date_il"]).dt.date
    mask = (day_series >= date_from) & (day_series <= date_to)
    daily_f = daily.loc[mask].copy()

    tabs = st.tabs([
        t("tab_summary", lang),
        t("tab_timeline", lang),
        t("tab_hourly", lang),
        t("tab_geography", lang),
    ])

    with tabs[0]:
        _tab_summary(bundle)

    with tabs[1]:
        _tab_timeline(bundle, daily_f, date_from, date_to, top_n_cat, top_n_src)

    with tabs[2]:
        _tab_hourly(bundle, date_from, date_to)

    with tabs[3]:
        _tab_geography(bundle, top_n_loc)


if __name__ == "__main__":
    main()
