"""
Indonesia Weather Analytics & Observability Dashboard
======================================================
Enterprise End-to-End Data Engineering Showcase
Stack: OpenWeatherMap API -> Apache Airflow -> Google BigQuery -> dbt -> Streamlit
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pydeck as pdk
from datetime import datetime

# Import data loader module
from data_loader import (
    load_latest_city_weather,
    load_daily_trends,
    load_data_quality_logs,
    load_overall_kpis,
)

# -----------------------------------------------------------------------------
# 1. Page Configuration & Theme
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Nusantara Weather Intelligence",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown("""
<style>
    .metric-card {
        background: #ffffff;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08), 0 2px 8px rgba(0,0,0,0.04);
        border: 1px solid #e8eaed;
    }
    .metric-label {
        font-size: 0.75rem;
        color: #5f6368;
        font-weight: 500;
        letter-spacing: 0.025em;
        margin-bottom: 8px;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 600;
        color: #202124;
        line-height: 1.2;
    }
    .metric-sub {
        font-size: 0.875rem;
        color: #5f6368;
        margin-top: 8px;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        border-bottom: 1px solid #e8eaed;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 12px 20px;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)



# -----------------------------------------------------------------------------
# 2. Sidebar Navigation & Controls
# -----------------------------------------------------------------------------
with st.sidebar:
    st.title("Weather Data Platform")
    st.caption("ELT pipeline with automated quality checks")
    st.markdown("---")
    
    st.subheader("Controls")
    if st.button("Refresh data", use_container_width=True, help="Clear cache and fetch latest data from BigQuery"):
        st.cache_data.clear()
        st.success("Cache cleared")
        st.rerun()

    st.markdown("---")
    st.subheader("Pipeline Architecture")
    st.markdown("""
    **Ingestion:** Python & Airflow  
    **Warehouse:** Google Cloud BigQuery  
    **Transform:** dbt (Star Schema)  
    **Quality:** Automated audit suite  
    **Serving:** Streamlit & PyDeck
    """)
    st.markdown("---")
    st.caption("Data refreshes every 6 hours")



# -----------------------------------------------------------------------------
# 3. Header & Executive KPI Summary
# -----------------------------------------------------------------------------
st.title("Nusantara Weather Intelligence")
st.markdown("Weather monitoring and analytics for Indonesia's major cities, refreshed every 6 hours, powered by BigQuery and dbt.")



try:
    kpis = load_overall_kpis()
    df_current = load_latest_city_weather()
    df_trends = load_daily_trends()
    df_logs = load_data_quality_logs(limit=15)
except Exception as e:
    st.error(f"Gagal memuat data dari BigQuery: {str(e)}")
    st.stop()

# Baris Metrik KPI Utama
kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5 = st.columns(5)

with kpi_col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">AVERAGE TEMPERATURE</div>
        <div class="metric-value">{kpis['avg_temp']}°C</div>
        <div class="metric-sub">Across 5 cities</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">HOTTEST CITY</div>
        <div class="metric-value">{kpis['max_temp']}°C</div>
        <div class="metric-sub">{kpis['hottest_city']}</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">AVERAGE HUMIDITY</div>
        <div class="metric-value">{int(kpis['avg_humidity'])}%</div>
        <div class="metric-sub">Tropical climate</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col4:
    status_color = "#137333" if "HEALTHY" in kpis['quality_status'] else "#C5221F"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">DATA QUALITY</div>
        <div class="metric-value" style="font-size: 1.4rem; color: {status_color};">{kpis['quality_status']}</div>
        <div class="metric-sub">Freshness & completeness</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col5:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">LAST OBSERVATION</div>
        <div class="metric-value" style="font-size: 1.1rem;">{kpis['last_updated']}</div>
        <div class="metric-sub">Pipeline sync</div>
    </div>
    """, unsafe_allow_html=True)


st.markdown("<br>", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 4. Tab Navigation
# -----------------------------------------------------------------------------
tab_map, tab_trends, tab_quality = st.tabs([
    "Current Conditions",
    "Historical Trends",
    "Data Quality"
])



# =============================================================================
# TAB 1: Peta Geospasial & Cuaca Terkini
# =============================================================================
with tab_map:
    st.subheader("Current weather by city")
    
    col_map, col_details = st.columns([1.6, 1.0])
    
    with col_map:
        st.markdown("**Temperature distribution across Indonesia**")

        if not df_current.empty:
            # Hitung radius dan warna berdasarkan temperatur
            df_map = df_current.copy()

            # Skala warna: Kuning hangat ke Oranye-Merah tropis
            def get_color(temp):
                if temp < 27:
                    return [33, 150, 243, 200]   # Biru sejuk
                elif temp < 30:
                    return [255, 193, 7, 200]   # Kuning hangat
                elif temp < 32:
                    return [255, 152, 0, 220]   # Oranye
                else:
                    return [244, 67, 54, 230]   # Merah panas

            df_map["color"] = df_map["temperature"].apply(get_color)

            layer = pdk.Layer(
                "ScatterplotLayer",
                data=df_map,
                get_position=["longitude", "latitude"],
                get_color="color",
                get_radius=50000,  # 50 km radius
                pickable=True,
                auto_highlight=True,
            )

            view_state = pdk.ViewState(
                latitude=-2.5,
                longitude=118.0,
                zoom=4.2,
                pitch=20,
            )

            r = pdk.Deck(
                layers=[layer],
                initial_view_state=view_state,
                tooltip={
                    "html": "<b>{city_name}</b><br/>"
                            "🌡️ Suhu: {temperature}°C (Terasa: {feels_like}°C)<br/>"
                            "💧 Kelembaban: {humidity}%<br/>"
                            "☁️ Cuaca: {weather_description}<br/>"
                            "💨 Angin: {wind_speed} m/s",
                    "style": {"backgroundColor": "#263238", "color": "white", "fontSize": "13px"}
                },
                map_style="light",
            )
            st.pydeck_chart(r)
        else:
            st.warning("Belum ada data observasi terkini.")

    with col_details:
        st.markdown("**City details**")
        if not df_current.empty:
            selected_city = st.selectbox("Select city:", df_current["city_name"].tolist())
            city_row = df_current[df_current["city_name"] == selected_city].iloc[0]
            
            st.markdown(f"""
            ### {city_row['city_name']}
            **Temperature:** {city_row['temperature']}°C (feels like {city_row['feels_like']}°C)  
            **Humidity:** {city_row['humidity']}%  
            **Pressure:** {city_row['pressure']} hPa  
            **Wind:** {city_row['wind_speed']} m/s  
            **Cloud cover:** {city_row['cloudiness']}%  
            **Condition:** {city_row['weather_description'].title()}
            """)
            st.caption(f"Observed at {city_row['observation_timestamp']}")

    st.markdown("---")
    st.markdown("**All cities**")
    display_cols = ["city_name", "temperature", "feels_like", "humidity", "pressure", "wind_speed", "weather_main", "weather_description"]
    st.dataframe(
        df_current[display_cols].rename(columns={
            "city_name": "City",
            "temperature": "Temp (°C)",
            "feels_like": "Feels like (°C)",
            "humidity": "Humidity (%)",
            "pressure": "Pressure (hPa)",
            "wind_speed": "Wind (m/s)",
            "weather_main": "Weather",
            "weather_description": "Description"
        }),
        use_container_width=True,
        hide_index=True
    )



# =============================================================================
# TAB 2: Tren Analitik Historis (dbt Marts)
# =============================================================================
with tab_trends:
    st.subheader("Daily aggregation trends")
    st.markdown("Historical data transformed through dbt staging and marts models.")


    if not df_trends.empty:
        # Filter kota
        all_cities = df_trends["city_name"].unique().tolist()
        filter_cities = st.multiselect("Filter cities:", all_cities, default=all_cities)


        filtered_trends = df_trends[df_trends["city_name"].isin(filter_cities)]

        # Chart 1: Garis Tren Suhu Rata-rata per Kota
        fig_temp = px.line(
            filtered_trends,
            x="observation_date",
            y="avg_temperature",
            color="city_name",
            markers=True,
            title="Tren Suhu Rata-rata Harian per Kota (°C)",
            labels={"observation_date": "Tanggal", "avg_temperature": "Suhu Rata-rata (°C)", "city_name": "Kota"},
            template="plotly_white",
        )
        fig_temp.update_layout(hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_temp, use_container_width=True)

        col_chart_a, col_chart_b = st.columns(2)

        with col_chart_a:
            # Chart 2: Perbandingan Suhu Min vs Max
            fig_range = px.bar(
                filtered_trends,
                x="city_name",
                y=["min_temperature", "max_temperature"],
                barmode="group",
                title="Rentang Fluktuasi Suhu (Min vs Max) per Kota",
                labels={"value": "Suhu (°C)", "city_name": "Kota", "variable": "Metrik"},
                template="plotly_white",
                color_discrete_sequence=["#0288D1", "#E65100"]
            )
            st.plotly_chart(fig_range, use_container_width=True)

        with col_chart_b:
            # Chart 3: Distribusi Cuaca Dominan (Dominant Weather)
            fig_weather = px.histogram(
                filtered_trends,
                x="dominant_weather",
                color="city_name",
                title="Distribusi Cuaca Dominan",
                labels={"dominant_weather": "Kondisi Cuaca", "count": "Jumlah Hari", "city_name": "Kota"},
                template="plotly_white"
            )
            st.plotly_chart(fig_weather, use_container_width=True)

    else:
        st.info("No historical data available yet.")



# =============================================================================
# TAB 3: Observabilitas Data & Audit Mutu (Data Quality Suite)
# =============================================================================
with tab_quality:
    st.subheader("Data quality audit log")
    st.markdown("Automated checks from the pipeline quality task evaluating freshness, completeness, and anomaly detection.")
    
    col_pipe_info, col_pipe_stat = st.columns([1, 1])
    
    with col_pipe_info:
        st.markdown("""
        #### Quality checks
        **Freshness SLA:** Data must arrive within 7 hours of API observation  
        **Completeness:** All 5 cities must be present  
        **Climate range:** Temperature within tropical bounds (15°C – 45°C)
        """)
        
    with col_pipe_stat:
        st.markdown(f"""
        #### Current status
        **Pipeline health:** {kpis['quality_status']}  
        **Audit table:** `weather_data_marts.data_quality_audit_log`  
        **Failure behavior:** Critical failures halt the Airflow DAG
        """)

    st.markdown("---")
    st.markdown("**Recent audit log entries**")


    if not df_logs.empty:
        # Format styling tabel audit
        def highlight_status(val):
            if val == "PASS":
                return "color: #2E7D32; font-weight: bold;"
            elif val == "WARN":
                return "color: #F57C00; font-weight: bold;"
            else:
                return "color: #C62828; font-weight: bold;"

        styled_logs = df_logs.style.map(highlight_status, subset=["status"])
        st.dataframe(styled_logs, use_container_width=True, hide_index=True)
    else:
        st.info("No audit log entries yet.")

