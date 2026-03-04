import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from dashboard.i18n import t, init_language
from src.frequency_analyzer import build_keyword_timeseries, build_category_timeseries
from src.signal_scorer import (
    build_composite_signal, find_signal_peaks, classify_alert_level,
    generate_retrospective_report, estimate_lead_time,
)
from config import IRAN_KEYWORDS, ESCALATION_CATEGORIES

st.set_page_config(page_title="Signals", layout="wide")
init_language()
st.title(t("signals_title"))
st.markdown(t("signals_desc"))

df = st.session_state.get("df_filtered", st.session_state.get("df"))
if df is None:
    st.warning(t("load_data_main_first")); st.stop()

with st.sidebar:
    event_date = st.date_input(t("event_date"), value=pd.Timestamp("2026-02-28").date())
    fm = {"1h": t("hourly"), "3h": t("3h"), "6h": t("6h"), "D": t("daily")}
    freq = st.selectbox(t("time_scale"), list(fm.keys()), format_func=lambda x: fm[x])

keyword_ts = st.session_state.get("keyword_ts")
if keyword_ts is None:
    keyword_ts = build_keyword_timeseries(df, IRAN_KEYWORDS, freq=freq)
category_ts = st.session_state.get("category_ts")
if category_ts is None:
    category_ts = build_category_timeseries(df, ESCALATION_CATEGORIES, freq=freq)
sentiment_ts = st.session_state.get("sentiment_ts")

signals = build_composite_signal(keyword_ts, category_ts, sentiment_ts)

last_val = signals["composite_escalation_index"].iloc[-1] if not signals.empty else 0
alert = classify_alert_level(last_val)

alert_colors = {"CRITICAL": "#ff4444", "HIGH": "#ff8800", "ELEVATED": "#ffcc00", "GUARDED": "#4488ff", "LOW": "#44ff44"}
alert_key = {"CRITICAL": "alert_critical", "HIGH": "alert_high", "ELEVATED": "alert_elevated", "GUARDED": "alert_guarded", "LOW": "alert_low"}

st.markdown(f"""
<div style="text-align:center; padding: 1.5rem; background: linear-gradient(135deg, #1e1e2e, #2d2d44);
            border-radius: 16px; border: 2px solid {alert_colors[alert]}; margin-bottom: 1rem;">
    <p style="font-size: 2.5rem; margin: 0; color: {alert_colors[alert]}; font-weight: bold;">{last_val:.2f}</p>
    <p style="color: {alert_colors[alert]}; margin: 0.3rem 0 0 0;">{t(alert_key[alert])}</p>
</div>
""", unsafe_allow_html=True)

st.subheader(t("index_timeline"))
st.markdown(t("index_timeline_desc"))

fig = go.Figure()
for y0, y1, color in [(0,.2,"rgba(68,255,68,0.05)"),(.2,.4,"rgba(68,136,255,0.05)"),
                       (.4,.6,"rgba(255,204,0,0.08)"),(.6,.8,"rgba(255,136,0,0.1)"),(.8,1,"rgba(255,68,68,0.12)")]:
    fig.add_hrect(y0=y0, y1=y1, fillcolor=color, line_width=0)
fig.add_trace(go.Scatter(x=signals.index, y=signals["composite_escalation_index"], mode="lines", name=t("index_raw"), line=dict(color="#888", width=1)))
fig.add_trace(go.Scatter(x=signals.index, y=signals["composite_smoothed"], mode="lines", name=t("index_smoothed"), line=dict(color="#ff4757", width=3)))

evt = str(event_date)
fig.add_shape(type="line", x0=evt, x1=evt, y0=0, y1=1, line=dict(color="#ff4444", width=2, dash="dash"))
fig.add_annotation(x=evt, y=0.95, text=t("operation_start"), showarrow=False, font=dict(color="#ff4444", size=12))

peaks = find_signal_peaks(signals)
if not peaks.empty:
    fig.add_trace(go.Scatter(x=peaks["date"], y=peaks["score"], mode="markers", name=t("peak_points"),
        marker=dict(color="#ffa502", size=10, symbol="diamond")))

fig.update_layout(template="plotly_dark", height=500, yaxis=dict(title=t("tension_index"), range=[0, 1]),
    legend=dict(orientation="h", y=1.12), margin=dict(l=0, r=0, t=30, b=0))
st.plotly_chart(fig, use_container_width=True)

st.subheader(t("signal_breakdown"))
st.markdown(t("signal_breakdown_desc"))

sig_cols = [c for c in signals.columns if c not in ("composite_escalation_index", "composite_smoothed")]
sig_names = {
    "keyword_frequency": t("sig_keyword_freq"), "keyword_acceleration": t("sig_keyword_accel"),
    "sentiment_negativity": t("sig_sentiment"), "category_military_action": t("sig_military"),
    "category_casualties_damage": t("sig_casualties"), "category_diplomatic_political": t("sig_diplomatic"),
    "category_missile_defense": t("sig_missiles"), "category_regional_escalation": t("sig_regional"),
}

fig_bd = go.Figure()
clrs = px.colors.qualitative.Set2
for i, col in enumerate(sig_cols):
    fig_bd.add_trace(go.Scatter(x=signals.index, y=signals[col].rolling(3, min_periods=1).mean(),
        mode="lines", name=sig_names.get(col, col), line=dict(color=clrs[i % len(clrs)], width=2)))
fig_bd.update_layout(template="plotly_dark", height=400, legend=dict(orientation="h", y=1.2), margin=dict(l=0, r=0, t=30, b=0))
st.plotly_chart(fig_bd, use_container_width=True)

st.subheader(t("retrospective"))
st.markdown(t("retrospective_desc"))

report = generate_retrospective_report(signals, event_date=str(event_date))
if "error" not in report:
    ei = report["escalation_index"]
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric(t("index_day_before"), f"{ei['last_day']:.3f}" if ei['last_day'] else "—")
        st.metric(t("avg_week_before"), f"{ei['last_7d_avg']:.3f}")
    with c2:
        st.metric(t("avg_month_before"), f"{ei['last_30d_avg']:.3f}")
        st.metric(t("peak_month"), f"{ei['max_last_30d']:.3f}")
    with c3:
        tr = {"rising": t("trend_rising"), "falling": t("trend_falling"), "mixed": t("trend_mixed")}
        st.metric(t("trend_week"), tr.get(ei["last_7d_trend"], ei["last_7d_trend"]))

    if report.get("signal_breakdown"):
        st.markdown(f"**{t('strongest_signals')}**")
        cd = pd.DataFrame([
            {t("signal_name"): sig_names.get(k, k), t("contribution"): v["contribution"],
             t("per_week"): v["last_7d_avg"], t("per_month"): v["last_30d_avg"]}
            for k, v in report["signal_breakdown"].items()
        ])
        st.dataframe(cd.style.background_gradient(cmap="YlOrRd", subset=[t("contribution")]), use_container_width=True)

    st.subheader(t("lead_time_title"))
    st.markdown(t("lead_time_desc"))
    for th in [0.3, 0.5, 0.7]:
        lt = estimate_lead_time(signals, event_date=str(event_date), threshold=th)
        if lt["lead_time_days"]:
            sus = t("lead_time_sustained") if lt.get("sustained") else t("lead_time_dropped")
            st.write(f"• {t('lead_time_found').format(th, lt['lead_time_days'], sus)}")
        else:
            st.write(f"• {t('lead_time_not_reached').format(th)}")
else:
    st.warning(report["error"])
