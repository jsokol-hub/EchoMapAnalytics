"""EchoMap Analytics — main dashboard."""

import sys
import threading
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import logging

logging.basicConfig(level=logging.INFO)

st.set_page_config(page_title="EchoMap Analytics", page_icon="🌍", layout="wide", initial_sidebar_state="expanded")

st.markdown("""<style>
    .block-container { padding-top: 1rem; }
    div[data-testid="stSidebar"] { background: linear-gradient(180deg, #0e1117 0%, #1a1a2e 100%); }
</style>""", unsafe_allow_html=True)

from dashboard.i18n import t, init_language


# PRODUCTION: background-loaded df so first HTTP response is fast (avoids proxy/healthcheck killing the container)
_background_df = None
_background_load_started = False


def _background_load():
    global _background_df
    try:
        df = load_and_preprocess(source="auto", csv_path=None)
        _background_df = df.copy()
    except Exception:
        _background_df = None


@st.cache_data(ttl=600)
def load_and_preprocess(source="auto", csv_path=None):
    from src.data_loader import load_data, load_from_cache
    from src.preprocessor import preprocess_dataframe
    from src.geo_analyzer import add_region_column
    from config import CACHE_PATH

    if csv_path:
        df = load_data(source="csv", path=csv_path)
        df = preprocess_dataframe(df)
        df = add_region_column(df)
        return df

    if source == "auto" and Path(CACHE_PATH).exists():
        return load_from_cache()

    df = load_data(source=source)
    df = preprocess_dataframe(df)
    df = add_region_column(df)
    return df


def main():
    init_language()

    st.title(f"🌍 {t('app_title')}")
    st.markdown(t("app_subtitle"))

    from config import PRODUCTION

    # PRODUCTION: fast first response — show "Loading..." and load data in background so proxy/healthcheck gets 200 quickly
    if PRODUCTION and "df" not in st.session_state:
        global _background_df, _background_load_started
        if _background_df is not None:
            st.session_state["df"] = _background_df
            _background_df = None
            # fall through to render with session_state["df"] below
        else:
            if not _background_load_started:
                _background_load_started = True
                th = threading.Thread(target=_background_load, daemon=True)
                th.start()
            st.info(t("loading_data_background"))
            @st.fragment(run_every=2)
            def poll_loaded():
                global _background_df
                if _background_df is not None:
                    st.session_state["df"] = _background_df
                    _background_df = None
                    st.rerun()
            poll_loaded()
            return

    # Duplicate import removed; PRODUCTION already imported above

    with st.sidebar:
        data_source = "auto"
        csv_path = None
        if not PRODUCTION:
            st.header("⚙️")
            from config import SSH_CONFIG
            default_source = "postgres" if SSH_CONFIG["enabled"] else "auto"
            data_source = st.radio("Source", ["postgres", "csv", "auto"],
                                   index=["postgres", "csv", "auto"].index(default_source), horizontal=True)
            if data_source == "csv":
                uploaded = st.file_uploader("CSV", type=["csv"])
                if uploaded:
                    import tempfile
                    tmp = Path(tempfile.mkdtemp()) / "uploaded.csv"
                    tmp.write_bytes(uploaded.read())
                    csv_path = str(tmp)

    try:
        if "df" in st.session_state:
            df = st.session_state["df"]
        else:
            with st.spinner(t("loading_data")):
                df = load_and_preprocess(source=data_source, csv_path=csv_path)
            st.session_state["df"] = df

        with st.sidebar:
            st.divider()
            st.header(f"🔍 {t('filters')}")

            if "date" in df.columns:
                date_range = st.date_input(t("date_range"),
                    value=(df["date"].min().date(), df["date"].max().date()),
                    min_value=df["date"].min().date(), max_value=df["date"].max().date())
                if len(date_range) == 2:
                    mask = (df["date"].dt.date >= date_range[0]) & (df["date"].dt.date <= date_range[1])
                    df = df[mask]

            if "category" in df.columns:
                cats = df["category"].unique().tolist()
                selected_cats = st.multiselect(t("event_types"), cats, default=cats)
                df = df[df["category"].isin(selected_cats)]

            if "channel" in df.columns:
                channels = df["channel"].value_counts().head(20).index.tolist()
                selected_ch = st.multiselect(t("channels"), channels, default=channels)
                df = df[df["channel"].isin(selected_ch)]

            if "region" in df.columns:
                regions = df["region"].unique().tolist()
                selected_regions = st.multiselect(t("regions"), regions, default=regions)
                df = df[df["region"].isin(selected_regions)]

        st.session_state["df_filtered"] = df
        _show_overview(df)

    except FileNotFoundError:
        st.warning("No data found. Configure .env or upload CSV.")
    except Exception as e:
        st.error(f"Error: {e}")
        st.exception(e)


def _show_overview(df):
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: st.metric(f"📨 {t('messages_count')}", f"{len(df):,}")
    with c2:
        if "date" in df.columns:
            days = max((df["date"].max() - df["date"].min()).days, 1)
            st.metric(f"📅 {t('days_in_sample')}", days)
    with c3:
        if "channel" in df.columns: st.metric(f"📡 {t('channels_count')}", df["channel"].nunique())
    with c4:
        if "location" in df.columns: st.metric(f"📍 {t('locations_count')}", df["location"].nunique())
    with c5:
        if "category" in df.columns: st.metric(f"🏷️ {t('categories_count')}", df["category"].nunique())

    st.divider()
    tab1, tab2, tab3 = st.tabs([f"📈 {t('tab_dynamics')}", f"🗺️ {t('tab_map')}", f"📋 {t('tab_data')}"])

    with tab1:
        st.markdown(t("dynamics_desc"))
        if "date" in df.columns:
            freq_map = {"1h": t("hourly"), "3h": t("3h"), "6h": t("6h"), "D": t("daily")}
            freq = st.radio(t("time_scale"), list(freq_map.keys()), index=0, horizontal=True,
                            format_func=lambda x: freq_map[x])

            daily = df.set_index("date").resample(freq).size().reset_index(name="count")
            fig = px.area(daily, x="date", y="count", labels={"date": "", "count": t("messages")})
            fig.update_layout(template="plotly_dark", height=300, margin=dict(l=0, r=0, t=10, b=0))
            st.plotly_chart(fig, use_container_width=True)

            if "category" in df.columns:
                st.markdown(f"**{t('by_category')}** — {t('by_category_desc')}")
                from config import CATEGORY_LABELS
                cat_ts = (df.set_index("date").groupby([pd.Grouper(freq=freq), "category"])
                          .size().unstack(fill_value=0).reset_index()
                          .melt(id_vars="date", var_name="category", value_name="count"))
                color_map = {k: v["color"] for k, v in CATEGORY_LABELS.items()}
                fig_cat = px.area(cat_ts, x="date", y="count", color="category", color_discrete_map=color_map,
                                  labels={"date": "", "count": t("messages"), "category": t("event_type")})
                fig_cat.update_layout(template="plotly_dark", height=300, margin=dict(l=0, r=0, t=10, b=0))
                st.plotly_chart(fig_cat, use_container_width=True)

    with tab2:
        st.markdown(t("map_desc"))
        if "lat" in df.columns and "long" in df.columns:
            from src.geo_analyzer import get_map_data
            from config import CATEGORY_LABELS
            map_df = get_map_data(df)
            if not map_df.empty:
                color_map = {k: v["color"] for k, v in CATEGORY_LABELS.items()}
                fig_map = px.scatter_map(map_df, lat="lat", lon="long", color="category",
                    color_discrete_map=color_map, hover_name="location",
                    hover_data={"text_clean": True, "date": True, "lat": False, "long": False},
                    zoom=3, height=600)
                fig_map.update_layout(map_style="carto-darkmatter", margin=dict(l=0, r=0, t=0, b=0))
                st.plotly_chart(fig_map, use_container_width=True)

    with tab3:
        st.markdown(t("table_desc"))
        display_cols = [c for c in ["date", "text_clean", "location", "category", "channel"] if c in df.columns]
        st.dataframe(df[display_cols].tail(50), use_container_width=True, height=500)

    st.divider()
    st.markdown(f"👈 {t('go_to_pages')}")


if __name__ == "__main__":
    main()
