"""
Data Loader Module for Streamlit Dashboard
============================================
Mengambil data analitik dari BigQuery Data Marts dengan caching cerdas (@st.cache_data).
"""

import os
from pathlib import Path
import streamlit as st
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account


def get_bigquery_client() -> bigquery.Client:
    """Menginisialisasi BigQuery Client dengan fallback credentials yang aman."""
    project_id = os.getenv("GCP_PROJECT_ID", "weather-513509")
    
    # 1. Cek dari Streamlit Secrets (untuk deployment di Streamlit Cloud)
    try:
        if "gcp_service_account" in st.secrets:
            credentials = service_account.Credentials.from_service_account_info(
                dict(st.secrets["gcp_service_account"])
            )
            return bigquery.Client(credentials=credentials, project=project_id)
    except Exception:
        # Secrets file belum ada (wajar di local environment)
        pass
    
    # 2. Cek file credentials lokal di Windows/Linux
    possible_cred_paths = [
        Path("credentials/gcp-credentials.json"),
        Path("../credentials/gcp-credentials.json"),
        Path(os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")),
    ]
    
    for path in possible_cred_paths:
        if path.is_file():
            credentials = service_account.Credentials.from_service_account_file(str(path))
            return bigquery.Client(credentials=credentials, project=project_id)
            
    # 3. Default fallback
    return bigquery.Client(project=project_id)


@st.cache_data(ttl=300, show_spinner=False)
def load_latest_city_weather() -> pd.DataFrame:
    """Mengambil kondisi cuaca terkini per kota beserta koordinat geospasialnya."""
    client = get_bigquery_client()
    query = """
        WITH latest_obs AS (
            SELECT 
                f.city_id,
                c.city_name,
                c.latitude,
                c.longitude,
                f.observation_timestamp,
                f.temperature,
                f.feels_like,
                f.humidity,
                f.pressure,
                f.wind_speed,
                f.weather_main,
                f.weather_description,
                f.cloudiness,
                ROW_NUMBER() OVER (PARTITION BY f.city_id ORDER BY f.observation_timestamp DESC) as rank
            FROM `weather-513509.weather_data_marts.fact_weather_observations` f
            JOIN `weather-513509.weather_data_marts.dim_cities` c ON f.city_id = c.city_id
        )
        SELECT * EXCEPT(rank)
        FROM latest_obs
        WHERE rank = 1
        ORDER BY city_name ASC
    """
    return client.query(query).to_dataframe()


@st.cache_data(ttl=300, show_spinner=False)
def load_daily_trends() -> pd.DataFrame:
    """Mengambil riwayat ringkasan harian dari tabel agg_daily_weather."""
    client = get_bigquery_client()
    query = """
        SELECT 
            city_name,
            observation_date,
            total_observations,
            avg_temperature,
            min_temperature,
            max_temperature,
            avg_humidity,
            avg_wind_speed,
            dominant_weather
        FROM `weather-513509.weather_data_marts.agg_daily_weather`
        ORDER BY observation_date ASC, city_name ASC
    """
    df = client.query(query).to_dataframe()
    df["observation_date"] = pd.to_datetime(df["observation_date"]).dt.date
    return df


@st.cache_data(ttl=300, show_spinner=False)
def load_data_quality_logs(limit: int = 10) -> pd.DataFrame:
    """Mengambil riwayat log audit mutu data dari tabel data_quality_audit_log."""
    client = get_bigquery_client()
    query = f"""
        SELECT 
            check_timestamp,
            check_name,
            check_category,
            status,
            metric_value,
            threshold,
            message
        FROM `weather-513509.weather_data_marts.data_quality_audit_log`
        ORDER BY check_timestamp DESC
        LIMIT {limit}
    """
    df = client.query(query).to_dataframe()
    if not df.empty:
        df["check_timestamp"] = pd.to_datetime(df["check_timestamp"])
    return df


@st.cache_data(ttl=300, show_spinner=False)
def load_overall_kpis() -> dict:
    """Menghitung metrik ringkasan eksekutif untuk kartu KPI."""
    df_current = load_latest_city_weather()
    df_logs = load_data_quality_logs(limit=3)
    
    if df_current.empty:
        return {
            "avg_temp": 0.0,
            "max_temp": 0.0,
            "hottest_city": "N/A",
            "avg_humidity": 0.0,
            "total_cities": 0,
            "quality_score": "N/A",
            "last_updated": "N/A"
        }
        
    hottest_row = df_current.loc[df_current["temperature"].idxmax()]
    
    # Hitung status mutu data terbaru
    if not df_logs.empty:
        fail_count = (df_logs["status"] == "FAIL").sum()
        warn_count = (df_logs["status"] == "WARN").sum()
        if fail_count > 0:
            quality_status = "CRITICAL FAIL"
        elif warn_count > 0:
            quality_status = "WARNING"
        else:
            quality_status = "100% HEALTHY"
    else:
        quality_status = "HEALTHY"

    return {
        "avg_temp": round(df_current["temperature"].mean(), 1),
        "max_temp": round(hottest_row["temperature"], 1),
        "hottest_city": hottest_row["city_name"],
        "avg_humidity": round(df_current["humidity"].mean(), 0),
        "total_cities": len(df_current),
        "quality_status": quality_status,
        "last_updated": df_current["observation_timestamp"].max().strftime("%d %b %Y, %H:%M UTC")
    }
