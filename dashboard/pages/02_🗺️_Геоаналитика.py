import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from dashboard.i18n import t, init_language
from src.geo_analyzer import get_location_stats, build_geo_timeseries, get_map_data
from config import CATEGORY_LABELS

st.set_page_config(page_title="Geo", layout="wide")
init_language()
st.title(f"🗺️ {t('geo_title')}")
st.markdown(t("geo_desc"))

df = st.session_state.get("df_filtered", st.session_state.get("df"))
if df is None:
    st.warning("Load data first."); st.stop()

st.subheader(t("interactive_map"))
st.markdown(t("map_hint"))

map_df = get_map_data(df)
if not map_df.empty:
    with st.sidebar:
        styles = {"carto-darkmatter": t("dark"), "open-street-map": t("normal"), "carto-positron": t("light")}
        map_style = st.selectbox(t("map_style"), list(styles.keys()), format_func=lambda x: styles[x])
        dot_size = st.slider(t("dot_size"), 3, 15, 7)

    color_map = {k: v["color"] for k, v in CATEGORY_LABELS.items()}
    fig = px.scatter_map(map_df, lat="lat", lon="long", color="category", color_discrete_map=color_map,
        hover_name="location", hover_data={"text_clean": True, "date": True, "lat": False, "long": False},
        zoom=4, height=600, center={"lat": 31.5, "lon": 45.0})
    fig.update_traces(marker=dict(size=dot_size))
    fig.update_layout(map_style=map_style, margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig, use_container_width=True)

st.subheader(f"📍 {t('top_locations')}")
st.markdown(t("top_locations_desc"))

loc_stats = get_location_stats(df, top_n=20)
if not loc_stats.empty:
    c1, c2 = st.columns(2)
    with c1:
        color_map = {k: v["color"] for k, v in CATEGORY_LABELS.items()}
        fig_l = px.bar(loc_stats, x="count", y="location", orientation="h",
            color="dominant_category" if "dominant_category" in loc_stats.columns else None,
            color_discrete_map=color_map, labels={"count": t("mentions"), "location": "", "dominant_category": t("main_topic")})
        fig_l.update_layout(template="plotly_dark", height=500, yaxis=dict(autorange="reversed"), margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig_l, use_container_width=True)
    with c2:
        st.dataframe(loc_stats, use_container_width=True, height=500)

st.subheader(f"📈 {t('regional_activity')}")
st.markdown(t("regional_activity_desc"))

if "region" in df.columns:
    geo_ts = build_geo_timeseries(df, freq="1h")
    if not geo_ts.empty:
        fig_r = go.Figure()
        rc = {"Israel": "#4ecdc4", "Iran": "#ff6b6b", "Gulf States": "#ffa502", "Lebanon": "#a29bfe", "Other": "#888"}
        for col in geo_ts.columns:
            fig_r.add_trace(go.Scatter(x=geo_ts.index, y=geo_ts[col], mode="lines", name=col,
                line=dict(color=rc.get(col, "#888"), width=2), stackgroup="one"))
        fig_r.update_layout(template="plotly_dark", height=400, yaxis_title=t("messages"),
            legend=dict(orientation="h", y=1.12), margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig_r, use_container_width=True)

if "location" in df.columns and "category" in df.columns:
    st.subheader(f"🏷️ {t('location_categories')}")
    st.markdown(t("location_categories_desc"))
    top = df["location"].value_counts().head(10).index.tolist()
    lc = df[df["location"].isin(top)].groupby(["location", "category"]).size().reset_index(name="count")
    color_map = {k: v["color"] for k, v in CATEGORY_LABELS.items()}
    fig_lc = px.bar(lc, x="location", y="count", color="category", color_discrete_map=color_map, barmode="stack",
        labels={"location": "", "count": t("messages"), "category": t("event_type")})
    fig_lc.update_layout(template="plotly_dark", height=400, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig_lc, use_container_width=True)
