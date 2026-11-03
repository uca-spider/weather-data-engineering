"""
Weather Ingestion Pipeline DAG
================================
Production DAG to fetch weather data and load to BigQuery

Schedule: Every 6 hours (00:00, 06:00, 12:00, 18:00 UTC)
Cities: Jakarta, Surabaya, Bandung, Medan, Makassar

Author: Weather Data Engineering Project
Sprint: Sprint 2
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
import sys
import os

# Add src to Python path
sys.path.insert(0, '/opt/airflow/src')

from ingestion.weather_fetcher import fetch_weather_data, INDONESIAN_CITIES
from ingestion.bigquery_loader import load_to_bigquery


def fetch_weather(**context):
    """Task 1: Fetch weather data from API"""
    print("=" * 60)
    print("🌦️  TASK 1: Fetching Weather Data")
    print("=" * 60)
    
    # Fetch data
    weather_data = fetch_weather_data(INDONESIAN_CITIES)
    
    if not weather_data:
        raise ValueError("No weather data fetched!")
    
    print(f"\n✅ Fetched {len(weather_data)} cities")
    for record in weather_data:
        print(f"   - {record['city']}: {record['temperature']}°C, {record['weather_description']}")
    
    # Push to XCom for next task
    context['task_instance'].xcom_push(key='weather_data', value=weather_data)
    
    return len(weather_data)


def validate_weather_data(**context):
    """Task 2: Validate weather data quality"""
    print("=" * 60)
    print("🔍 TASK 2: Validating Data Quality")
    print("=" * 60)
    
    # Pull data from previous task
    weather_data = context['task_instance'].xcom_pull(
        task_ids='fetch_weather',
        key='weather_data'
    )
    
    if not weather_data:
        raise ValueError("No data received from fetch_weather task")
    
    errors = []
    
    # Validation checks
    for record in weather_data:
        city = record.get('city', 'Unknown')
        
        # Check required fields
        required_fields = ['city', 'temperature', 'humidity', 'timestamp']
        for field in required_fields:
            if field not in record or record[field] is None:
                errors.append(f"{city}: Missing {field}")
        
        # Check temperature range (-50°C to 60°C)
        temp = record.get('temperature')
        if temp and (temp < -50 or temp > 60):
            errors.append(f"{city}: Temperature out of range ({temp}°C)")
        
        # Check humidity range (0-100%)
        humidity = record.get('humidity')
        if humidity and (humidity < 0 or humidity > 100):
            errors.append(f"{city}: Humidity out of range ({humidity}%)")
    
    if errors:
        print("\n⚠️  Validation warnings:")
        for error in errors:
            print(f"   - {error}")
        
        # For now, warnings only (don't fail)
        # In production, you might want to fail on critical errors
    
    print(f"\n✅ Validation complete: {len(weather_data)} records OK")
    
    # Push validated data to XCom
    context['task_instance'].xcom_push(key='validated_data', value=weather_data)
    
    return len(weather_data)


def load_to_bq(**context):
    """Task 3: Load data to BigQuery"""
    print("=" * 60)
    print("☁️  TASK 3: Loading to BigQuery")
    print("=" * 60)
    
    # Pull validated data
    weather_data = context['task_instance'].xcom_pull(
        task_ids='validate_data',
        key='validated_data'
    )
    
    if not weather_data:
        raise ValueError("No validated data received")
    
    # Load to BigQuery
    rows_inserted = load_to_bigquery(weather_data)
    
    if rows_inserted == 0:
        raise ValueError("Failed to insert data to BigQuery")
    
    print(f"\n✅ Successfully loaded {rows_inserted} records to BigQuery")
    
    return rows_inserted


def log_pipeline_summary(**context):
    """Task 4: Log pipeline execution summary"""
    print("=" * 60)
    print("📊 TASK 4: Pipeline Summary")
    print("=" * 60)
    
    # Get results from previous tasks
    cities_fetched = context['task_instance'].xcom_pull(task_ids='fetch_weather')
    cities_validated = context['task_instance'].xcom_pull(task_ids='validate_data')
    rows_loaded = context['task_instance'].xcom_pull(task_ids='load_to_bigquery')
    
    execution_date = context['execution_date']
    
    print(f"\n📅 Execution Date: {execution_date}")
    print(f"✅ Cities Fetched: {cities_fetched}")
    print(f"✅ Cities Validated: {cities_validated}")
    print(f"✅ Rows Loaded: {rows_loaded}")
    print(f"\n🎉 Pipeline executed successfully!")
    print("=" * 60)
    
    return "success"


# Default arguments
default_args = {
    'owner': 'data-engineer',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2026, 11, 2),
}

# DAG definition
with DAG(
    dag_id='weather_ingestion_pipeline',
    description='Fetch weather data from OpenWeatherMap and load to BigQuery',
    default_args=default_args,
    schedule_interval='0 */6 * * *',  # Every 6 hours
    catchup=False,
    tags=['production', 'weather', 'bigquery', 'sprint2'],
) as dag:
    
    # Task 1: Fetch weather data
    fetch_task = PythonOperator(
        task_id='fetch_weather',
        python_callable=fetch_weather,
        provide_context=True,
    )
    
    # Task 2: Validate data
    validate_task = PythonOperator(
        task_id='validate_data',
        python_callable=validate_weather_data,
        provide_context=True,
    )
    
    # Task 3: Load to BigQuery
    load_task = PythonOperator(
        task_id='load_to_bigquery',
        python_callable=load_to_bq,
        provide_context=True,
    )
    
    # Task 4: Log summary
    summary_task = PythonOperator(
        task_id='log_summary',
        python_callable=log_pipeline_summary,
        provide_context=True,
    )
    
    # Define task dependencies
    fetch_task >> validate_task >> load_task >> summary_task


# DAG Flow:
#
# fetch_weather → validate_data → load_to_bigquery → log_summary
#
# All tasks run sequentially with data passed via XCom
