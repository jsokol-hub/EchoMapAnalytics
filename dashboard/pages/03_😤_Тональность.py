import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from dashboard.i18n import t, init_language

st.set_page_config(page_title="Sentiment", layout="wide")
init_language()
st.title(f"😤 {t('sentiment_title')}")
st.markdown(t("sentiment_desc"))

df = st.session_state.get("df_filtered", st.session_state.get("df"))
if df is None:
    st.warning("Load data first."); st.stop()

if "sentiment_label" not in df.columns:
    st.info(t("sentiment_needed"))
    if st.button(f"🚀 {t('run_sentiment')}", type="primary"):
        with st.spinner("..."):
            from src.nlp_analyzer import add_sentiment_to_df
            df = add_sentiment_to_df(df)
            st.session_state["df"] = df
            st.session_state["df_filtered"] = df
        st.rerun()
    else:
        st.stop()

with st.sidebar:
    fm = {"1h": t("hourly"), "3h": t("3h"), "D": t("daily")}
    freq = st.selectbox(t("time_scale"), list(fm.keys()), format_func=lambda x: fm[x])

c1, c2 = st.columns(2)
with c1:
    st.subheader(t("overall_picture"))
    st.markdown(t("overall_desc"))
    counts = df["sentiment_label"].value_counts()
    lr = {"negative": t("negative"), "positive": t("positive"), "neutral": t("neutral")}
    fig_p = px.pie(values=counts.values, names=[lr.get(n, n) for n in counts.index], color=counts.index,
        color_discrete_map={"negative": "#ff4444", "positive": "#44ff44", "neutral": "#4488ff"})
    fig_p.update_layout(template="plotly_dark", height=300, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig_p, use_container_width=True)

with c2:
    if "category" in df.columns:
        st.subheader(t("by_event_type"))
        st.markdown(t("by_event_type_desc"))
        cs = df.groupby(["category", "sentiment_label"]).size().reset_index(name="count")
        fig_b = px.bar(cs, x="category", y="count", color="sentiment_label",
            color_discrete_map={"negative": "#ff4444", "positive": "#44ff44", "neutral": "#4488ff"}, barmode="group",
            labels={"category": t("event_type"), "count": t("count"), "sentiment_label": t("sentiment_label")})
        fig_b.update_layout(template="plotly_dark", height=300, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig_b, use_container_width=True)

st.subheader(f"📉 {t('negativity_timeline')}")
st.markdown(t("negativity_desc"))

if "date" in df.columns:
    from src.nlp_analyzer import build_sentiment_timeseries
    sent_ts = build_sentiment_timeseries(df, freq=freq)
    st.session_state["sentiment_ts"] = sent_ts

    fig_n = go.Figure()
    fig_n.add_trace(go.Scatter(x=sent_ts.index, y=sent_ts["negativity_index"], mode="lines",
        name=t("negativity_index"), line=dict(color="#ff4444", width=2), fill="tozeroy", fillcolor="rgba(255,68,68,0.1)"))
    fig_n.add_trace(go.Scatter(x=sent_ts.index, y=sent_ts["pct_negative"], mode="lines",
        name=t("pct_negative"), line=dict(color="#ff8800", width=1, dash="dot"), yaxis="y2"))
    fig_n.add_hline(y=0, line_dash="dash", line_color="gray")
    fig_n.update_layout(template="plotly_dark", height=400, yaxis=dict(title=t("negativity_higher_worse")),
        yaxis2=dict(title=t("pct_negative"), overlaying="y", side="right", tickformat=".0%"),
        legend=dict(orientation="h", y=1.12), margin=dict(l=0, r=0, t=30, b=0))
    st.plotly_chart(fig_n, use_container_width=True)

st.subheader(f"🔥 {t('most_alarming')}")
st.markdown(t("most_alarming_desc"))
dc = [c for c in ["date", "text_clean", "sentiment_negative", "category", "location"] if c in df.columns]
top_neg = df.nlargest(20, "sentiment_negative")[dc]
st.dataframe(top_neg.style.background_gradient(cmap="Reds", subset=["sentiment_negative"]),
    use_container_width=True, height=500)
