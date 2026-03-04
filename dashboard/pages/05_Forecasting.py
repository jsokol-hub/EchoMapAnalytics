import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import roc_auc_score

from dashboard.i18n import t, init_language
from src.frequency_analyzer import build_keyword_timeseries, build_category_timeseries
from src.signal_scorer import build_composite_signal
from config import IRAN_KEYWORDS, ESCALATION_CATEGORIES

st.set_page_config(page_title="Prediction", layout="wide")
init_language()
st.title(t("predict_title"))
st.markdown(t("predict_desc"))

df = st.session_state.get("df_filtered", st.session_state.get("df"))
if df is None:
    st.warning(t("load_data_main_first")); st.stop()

with st.sidebar:
    st.markdown(f"### {t('model_params')}")
    event_date = st.date_input(t("event_date"), value=pd.Timestamp("2026-02-28").date())
    lookback = st.slider(t("observation_window"), 3, 14, 7)
    forecast_horizon = st.slider(t("forecast_horizon"), 1, 14, 7)
    escalation_threshold = st.slider(t("escalation_threshold"), 0.1, 0.9, 0.5, 0.05)

keyword_ts = build_keyword_timeseries(df, IRAN_KEYWORDS, freq="D")
category_ts = build_category_timeseries(df, ESCALATION_CATEGORIES, freq="D")
sentiment_ts = st.session_state.get("sentiment_ts")
signals = build_composite_signal(keyword_ts, category_ts, sentiment_ts)

st.subheader(t("step1"))
st.markdown(t("step1_desc").format(lookback, escalation_threshold, forecast_horizon))


def build_features(sdf, lb):
    feats = pd.DataFrame(index=sdf.index)
    cols = [c for c in sdf.columns if c not in ("composite_escalation_index", "composite_smoothed")]
    for col in cols + ["composite_escalation_index"]:
        s = sdf[col]
        feats[f"{col}_mean_{lb}d"] = s.rolling(lb, min_periods=1).mean()
        feats[f"{col}_max_{lb}d"] = s.rolling(lb, min_periods=1).max()
        feats[f"{col}_std_{lb}d"] = s.rolling(lb, min_periods=1).std().fillna(0)
        feats[f"{col}_trend_{lb}d"] = s.diff(lb)
        feats[f"{col}_accel"] = s.diff().diff()
    feats["day_of_week"] = pd.Series(feats.index).dt.dayofweek.values
    return feats.fillna(0)


features = build_features(signals, lookback)
target = (signals["composite_escalation_index"].shift(-forecast_horizon)
          .rolling(forecast_horizon, min_periods=1).max() >= escalation_threshold).astype(int)

valid = target.notna()
X, y = features[valid], target[valid].astype(int)

c1, c2 = st.columns(2)
with c1: st.metric(t("features"), X.shape[1])
with c2: st.metric(t("training_days"), X.shape[0])

pct = y.mean() * 100
if pct > 0:
    st.info(t("escalation_days_info").format(int(y.sum()), f"{pct:.1f}"))
else:
    st.warning("No escalation periods with current settings."); st.stop()
if len(X) < 30:
    st.warning("Not enough data (need at least 30 days)."); st.stop()

st.subheader(t("step2"))
st.markdown(t("step2_desc"))

n_splits = min(5, max(2, len(X) // 20))
tscv = TimeSeriesSplit(n_splits=n_splits)
fold_scores = []

for _, (train_idx, test_idx) in enumerate(tscv.split(X)):
    Xtr, Xte = X.iloc[train_idx], X.iloc[test_idx]
    ytr, yte = y.iloc[train_idx], y.iloc[test_idx]
    if len(set(ytr)) < 2: continue
    m = GradientBoostingClassifier(n_estimators=100, max_depth=3, learning_rate=0.1, random_state=42)
    m.fit(Xtr, ytr)
    if len(set(yte)) > 1:
        fold_scores.append(roc_auc_score(yte, m.predict_proba(Xte)[:, 1] if len(m.classes_) > 1 else np.zeros(len(Xte))))

if fold_scores:
    avg = np.mean(fold_scores)
    if avg >= 0.8: st.success(t("auc_good").format(avg))
    elif avg >= 0.6: st.info(t("auc_ok").format(avg))
    else: st.warning(t("auc_weak").format(avg))

st.subheader(t("step3"))
st.markdown(t("step3_desc"))

final = GradientBoostingClassifier(n_estimators=100, max_depth=3, learning_rate=0.1, random_state=42)
final.fit(X, y)

imp = pd.Series(final.feature_importances_, index=X.columns).nlargest(15)

fn = {"composite_escalation_index": t("feat_composite"), "keyword_frequency": t("feat_kw_freq"),
      "keyword_acceleration": t("feat_kw_accel"), "sentiment_negativity": t("feat_sentiment"),
      "category_military_action": t("feat_military"), "category_casualties_damage": t("feat_casualties"),
      "category_diplomatic_political": t("feat_diplomatic"), "category_missile_defense": t("feat_missiles"),
      "category_regional_escalation": t("feat_regional")}
sn = {"mean": t("feat_mean"), "max": t("feat_max"), "std": t("feat_std"), "trend": t("feat_trend"), "accel": t("feat_accel")}

def _tr(name):
    for k, v in fn.items():
        if k in name:
            sfx = name.replace(k + "_", "")
            for se, sr in sn.items():
                sfx = sfx.replace(se, sr)
            return f"{v} ({sfx})"
    return name

fig_imp = px.bar(x=imp.values, y=[_tr(f) for f in imp.index], orientation="h",
    color=imp.values, color_continuous_scale="YlOrRd", labels={"x": t("importance"), "y": ""})
fig_imp.update_layout(template="plotly_dark", height=450, yaxis=dict(autorange="reversed"),
    coloraxis_showscale=False, margin=dict(l=0, r=0, t=10, b=0))
st.plotly_chart(fig_imp, use_container_width=True)

st.subheader(t("step4"))
st.markdown(t("step4_desc").format(forecast_horizon))

proba = pd.Series(final.predict_proba(X)[:, 1] if len(final.classes_) > 1 else np.zeros(len(X)), index=X.index)

fig_p = go.Figure()
fig_p.add_trace(go.Scatter(x=proba.index, y=proba.values, mode="lines", name=t("escalation_probability"),
    line=dict(color="#ff4757", width=2), fill="tozeroy", fillcolor="rgba(255,71,87,0.15)"))
fig_p.add_hline(y=0.5, line_dash="dash", line_color="#ffa502", annotation_text="50%")

evt = str(event_date)
fig_p.add_shape(type="line", x0=evt, x1=evt, y0=0, y1=1, line=dict(color="#ff4444", width=2, dash="dash"))
fig_p.add_annotation(x=evt, y=0.95, text=t("event"), showarrow=False, font=dict(color="#ff4444", size=12))

fig_p.update_layout(template="plotly_dark", height=400, yaxis=dict(title=t("escalation_probability"), range=[0, 1], tickformat=".0%"),
    legend=dict(orientation="h", y=1.12), margin=dict(l=0, r=0, t=30, b=0))
st.plotly_chart(fig_p, use_container_width=True)

# Section: when might it end (extrapolation of escalation index trend)
st.subheader(t("war_end_title"))
st.markdown(t("war_end_desc"))

calm_threshold = 0.3
s = signals["composite_smoothed"].dropna()
if len(s) >= 14:
    last_n = min(60, len(s))
    y_vals = s.iloc[-last_n:].values.astype(float)
    x_vals = np.arange(len(y_vals))
    coef = np.polyfit(x_vals, y_vals, 1)
    trend_slope = coef[0]
    max_future = 365
    future_x = np.arange(len(y_vals) + max_future)
    future_y = np.polyval(coef, future_x)
    below = np.where(future_y < calm_threshold)[0]
    if trend_slope < 0 and len(below) > 0:
        idx = int(below[0])
        pred_date = (s.index[-last_n] + pd.Timedelta(days=idx)).strftime("%d.%m.%Y")
        st.info(t("war_end_result").format(calm_threshold, pred_date))
    elif trend_slope >= 0:
        st.warning(t("war_end_trend_rising"))
    else:
        st.warning(t("war_end_no_decrease"))
else:
    st.caption("Not enough data for trend extrapolation.")
st.caption(t("war_end_disclaimer"))

st.subheader(t("conclusions"))
st.markdown(t("conclusions_text").format(lookback, forecast_horizon, escalation_threshold))
