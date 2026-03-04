import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from dashboard.i18n import t, init_language
from src.frequency_analyzer import (
    build_keyword_timeseries, build_category_timeseries,
    detect_anomalies, find_crescendo_patterns,
)
from config import IRAN_KEYWORDS, ESCALATION_CATEGORIES

st.set_page_config(page_title="Frequency", layout="wide")
init_language()
st.title(t("freq_title"))
st.markdown(t("freq_desc"))

df = st.session_state.get("df_filtered", st.session_state.get("df"))
if df is None:
    st.warning(t("load_data_main_first"))
    st.stop()

with st.sidebar:
    freq_map = {"1h": t("hourly"), "3h": t("3h"), "6h": t("6h"), "D": t("daily")}
    freq = st.selectbox(t("time_scale"), list(freq_map.keys()), format_func=lambda x: freq_map[x])
    anomaly_sigma = st.slider(t("sensitivity"), 1.5, 4.0, 2.5, 0.5)
    anomaly_window = st.slider(t("comparison_period"), 5, 30, 14)

st.subheader(t("keyword_mentions"))
st.markdown(t("keyword_chart_desc"))

keyword_ts = build_keyword_timeseries(df, IRAN_KEYWORDS, freq=freq)
st.session_state["keyword_ts"] = keyword_ts

fig = go.Figure()
fig.add_trace(go.Scatter(x=keyword_ts.index, y=keyword_ts["keyword_hits"], mode="lines",
    name=t("keyword_matches"), line=dict(color="#ff6b6b", width=2), fill="tozeroy", fillcolor="rgba(255,107,107,0.1)"))
fig.add_trace(go.Scatter(x=keyword_ts.index, y=keyword_ts["total_messages"], mode="lines",
    name=t("total_messages"), line=dict(color="#4ecdc4", width=1, dash="dot"), yaxis="y2"))
fig.update_layout(template="plotly_dark", height=400, yaxis=dict(title=t("keyword_matches")),
    yaxis2=dict(title=t("total_messages"), overlaying="y", side="right"),
    legend=dict(orientation="h", y=1.12), margin=dict(l=0, r=0, t=30, b=0))
st.plotly_chart(fig, use_container_width=True)

c1, c2 = st.columns([2, 1])
with c1: st.metric(t("total_matches_found"), f"{int(keyword_ts['keyword_hits'].sum()):,}")
with c2: st.metric(t("relevant_share"), f"{keyword_ts['keyword_ratio'].mean():.1%}")

if len(keyword_ts) > anomaly_window:
    st.subheader(t("unusual_spikes"))
    st.markdown(t("spikes_desc"))
    anomalies = detect_anomalies(keyword_ts["keyword_hits"], window=anomaly_window, threshold_sigma=anomaly_sigma)

    fig_a = go.Figure()
    fig_a.add_trace(go.Scatter(x=anomalies.index, y=anomalies["value"], mode="lines", name=t("actual_value"), line=dict(color="#888", width=1)))
    fig_a.add_trace(go.Scatter(x=anomalies.index, y=anomalies["rolling_mean"], mode="lines", name=t("normal_level"), line=dict(color="#4ecdc4", width=2)))
    upper = anomalies["rolling_mean"] + anomaly_sigma * anomalies["rolling_std"]
    fig_a.add_trace(go.Scatter(x=anomalies.index, y=upper, mode="lines", name=t("threshold"), line=dict(color="#ff8800", width=1, dash="dash")))
    anom = anomalies[anomalies["is_anomaly"]]
    if not anom.empty:
        fig_a.add_trace(go.Scatter(x=anom.index, y=anom["value"], mode="markers", name=t("spikes"), marker=dict(color="#ff4444", size=10, symbol="triangle-up")))
    fig_a.update_layout(template="plotly_dark", height=350, legend=dict(orientation="h", y=1.12), margin=dict(l=0, r=0, t=30, b=0))
    st.plotly_chart(fig_a, use_container_width=True)

    n = anom["is_anomaly"].sum()
    if n > 0: st.success(t("spikes_found").format(n))
    else: st.info(t("no_spikes"))

st.subheader(t("escalation_topics"))
st.markdown(t("escalation_topics_desc"))

category_ts = build_category_timeseries(df, ESCALATION_CATEGORIES, freq=freq)
st.session_state["category_ts"] = category_ts

cat_names = {"military_action": t("cat_military"), "casualties_damage": t("cat_casualties"),
    "diplomatic_political": t("cat_diplomatic"), "missile_defense": t("cat_missiles"), "regional_escalation": t("cat_regional")}
colors = ["#ff6b6b", "#ffa502", "#7bed9f", "#70a1ff", "#a29bfe"]

fig_c = go.Figure()
for i, col in enumerate(category_ts.columns):
    fig_c.add_trace(go.Scatter(x=category_ts.index, y=category_ts[col].rolling(3, min_periods=1).mean(),
        mode="lines", name=cat_names.get(col, col), line=dict(color=colors[i % len(colors)], width=2)))
fig_c.update_layout(template="plotly_dark", height=400, yaxis_title=t("messages"), legend=dict(orientation="h", y=1.15), margin=dict(l=0, r=0, t=30, b=0))
st.plotly_chart(fig_c, use_container_width=True)

if "category" in df.columns:
    st.subheader(t("event_stats"))
    st.markdown(t("event_stats_desc"))
    from config import CATEGORY_LABELS
    cc = df["category"].value_counts()
    color_map = {k: v["color"] for k, v in CATEGORY_LABELS.items()}
    fig_n = px.bar(x=cc.index, y=cc.values, color=cc.index, color_discrete_map=color_map,
        labels={"x": t("event_type"), "y": t("count")})
    fig_n.update_layout(template="plotly_dark", height=300, showlegend=False, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig_n, use_container_width=True)

if len(category_ts) > 5:
    st.subheader(t("crescendo"))
    st.markdown(t("crescendo_desc"))
    crescendo = find_crescendo_patterns(category_ts)
    fig_cr = go.Figure()
    fig_cr.add_trace(go.Scatter(x=crescendo.index, y=crescendo["crescendo_score"], mode="lines",
        name=t("crescendo_strength"), line=dict(color="#ff4757", width=3), fill="tozeroy", fillcolor="rgba(255,71,87,0.15)"))
    fig_cr.add_trace(go.Scatter(x=crescendo.index, y=crescendo["n_accelerating_categories"], mode="lines",
        name=t("topics_growing"), line=dict(color="#ffa502", width=2, dash="dot"), yaxis="y2"))
    fig_cr.update_layout(template="plotly_dark", height=350, yaxis=dict(title=t("crescendo_strength")),
        yaxis2=dict(title=t("topics_growing"), overlaying="y", side="right"), legend=dict(orientation="h", y=1.12), margin=dict(l=0, r=0, t=30, b=0))
    st.plotly_chart(fig_cr, use_container_width=True)
