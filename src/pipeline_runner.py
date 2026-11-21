"""
Standalone Cloud Pipeline Runner (GitHub Actions / Scheduled Runner)
===================================================================
Menjalankan seluruh tahapan ELT end-to-end tanpa memerlukan kontainer Airflow:
1. Ingestion: OpenWeather API -> BigQuery Raw
2. Transformation: dbt run & dbt test
3. Observability: Weather Quality Checker Audit
"""

import os
import sys
import subprocess
from pathlib import Path

# Pastikan path modul src terbaca
sys.path.insert(0, str(Path(__file__).parent))

from ingestion.weather_fetcher import fetch_weather_data, INDONESIAN_CITIES
from ingestion.bigquery_loader import load_to_bigquery
from validation.weather_quality_checker import WeatherQualityChecker


def run_ingestion():
    print("=" * 60)
    print("🌦️  STEP 1: Ingesting Weather Data")
    print("=" * 60)
    data = fetch_weather_data(INDONESIAN_CITIES)
    if not data:
        raise RuntimeError("No data fetched from OpenWeatherMap API!")
    
    rows = load_to_bigquery(data)
    print(f"✅ Successfully loaded {rows} records to BigQuery raw layer.")


def run_dbt():
    print("=" * 60)
    print("⚙️  STEP 2: Running dbt Transformations & Tests")
    print("=" * 60)
    dbt_dir = Path(__file__).parent.parent / "dbt" / "weather_dbt"
    
    # Jalankan dbt run
    cmd_run = ["dbt", "run", "--profiles-dir", str(dbt_dir)]
    res_run = subprocess.run(cmd_run, cwd=str(dbt_dir))
    if res_run.returncode != 0:
        raise RuntimeError("dbt run failed!")
        
    # Jalankan dbt test
    cmd_test = ["dbt", "test", "--profiles-dir", str(dbt_dir)]
    res_test = subprocess.run(cmd_test, cwd=str(dbt_dir))
    if res_test.returncode != 0:
        raise RuntimeError("dbt tests failed!")
        
    print("✅ dbt transformations & 24 tests passed successfully.")


def run_quality_audit():
    print("=" * 60)
    print("🛡️  STEP 3: Running Data Quality & Observability Audit")
    print("=" * 60)
    checker = WeatherQualityChecker()
    score, checks, has_failure = checker.run_all_checks()
    
    print(f"📊 Quality Score: {score}/100")
    if has_failure:
        raise RuntimeError(f"Critical Data Quality Failure! Score: {score}/100")
    print("✅ Quality audit completed and logged to BigQuery.")


def main():
    try:
        run_ingestion()
        run_dbt()
        run_quality_audit()
        print("\n🎉 ALL PIPELINE STAGES COMPLETED SUCCESSFULLY!")
    except Exception as e:
        print(f"\n❌ Pipeline failed: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
