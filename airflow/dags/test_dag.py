"""
Test DAG - Hello World
======================
Purpose: Verify Airflow setup is working correctly
Sprint: Sprint 1 - Infrastructure Setup

This is a simple DAG to test that:
1. Airflow can read DAG files
2. Scheduler is running
3. Tasks can execute
4. Logs are accessible

Usage:
1. Wait 30 seconds after creating this file
2. Go to Airflow UI: http://localhost:8080
3. Find 'test_hello_world' DAG
4. Click Play button → Trigger DAG
5. Check logs to see success message
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator


def say_hello():
    """Simple Python function to test PythonOperator"""
    print("=" * 50)
    print("🎉 Hello from Airflow!")
    print("✅ Your Airflow setup is working!")
    print("=" * 50)
    print("\n📊 Environment Info:")
    print(f"   - DAG: test_hello_world")
    print(f"   - Task: say_hello")
    print(f"   - Execution Time: {datetime.now()}")
    print("\n🚀 Next Steps:")
    print("   1. Setup GCP BigQuery")
    print("   2. Build weather ingestion DAG")
    print("   3. Transform data with dbt")
    print("=" * 50)
    return "Success!"


def check_environment():
    """Check if environment variables are loaded"""
    import os

    print("\n🔍 Checking Environment Variables...")
    print("=" * 50)

    # Check key environment variables
    env_vars = {
        'AIRFLOW_UID': os.getenv('AIRFLOW_UID', 'NOT SET'),
        'ENVIRONMENT': os.getenv('ENVIRONMENT', 'NOT SET'),
        'GCP_PROJECT_ID': os.getenv('GCP_PROJECT_ID', 'NOT SET'),
        'OPENWEATHER_API_KEY': '***' if os.getenv('OPENWEATHER_API_KEY') else 'NOT SET',
        'LOG_LEVEL': os.getenv('LOG_LEVEL', 'NOT SET'),
    }

    for key, value in env_vars.items():
        status = "✅" if value != "NOT SET" else "⚠️"
        print(f"{status} {key}: {value}")

    print("=" * 50)
    return env_vars

def check_time():
    """Check current time in Jakarta timezone"""
    from datetime import datetime
    import pytz
    
    print("\n" + "=" * 50)
    print("⏰ TIME CHECK")
    print("=" * 50)
    
    # UTC time
    utc_time = datetime.now(pytz.UTC)
    print(f"UTC Time: {utc_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    
    # Jakarta time
    jakarta_tz = pytz.timezone('Asia/Jakarta')
    jakarta_time = datetime.now(jakarta_tz)
    print(f"Jakarta Time: {jakarta_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    
    print("=" * 50)
    
    return jakarta_time.strftime('%Y-%m-%d %H:%M:%S')


# Default arguments for all tasks in this DAG
default_args = {
    'owner': 'data-engineer',  # Your name
    'depends_on_past': False,  # Task doesn't depend on previous runs
    'email_on_failure': False,  # Disable email alerts (for now)
    'email_on_retry': False,
    'retries': 1,  # Retry once if fails
    'retry_delay': timedelta(minutes=1),  # Wait 1 min before retry
}

# DAG definition
with DAG(
    dag_id='test_hello_world',
    description='Test DAG to verify Airflow setup',
    default_args=default_args,
    schedule=None,  # Manual trigger only (no automatic schedule)
    start_date=datetime(2026, 9, 23),  # When this DAG becomes active
    catchup=False,  # Don't run for past dates
    tags=['test', 'sprint1', 'learning'],  # Tags for filtering in UI
) as dag:

    # Task 1: Bash command (simplest operator)
    bash_task = BashOperator(
        task_id='print_date',
        bash_command='date && echo "Bash operator is working!"',
    )

    # Task 2: Python function
    hello_task = PythonOperator(
        task_id='say_hello',
        python_callable=say_hello,
    )

    # Task 3: Check environment
    env_task = PythonOperator(
        task_id='check_environment',
        python_callable=check_environment,
    )

    # Task 4: Check time
    time_task = PythonOperator(
        task_id='check_time',
        python_callable=check_time,
    )

    # Define task dependencies (execution order)
    # bash_task runs first, then hello_task and env_task run in parallel
    bash_task >> time_task >> [hello_task, env_task]

    # Alternative syntax (same result):
    # bash_task.set_downstream([hello_task, env_task])

# DAG structure visualization:
#
#     bash_task
#        ↓
#     time_task (NEW!)
#        /  \
#       /    \
# hello_task  env_task

#
# All 3 tasks will execute when you trigger this DAG

"""
Learning Notes:
===============

1. DAG (Directed Acyclic Graph):
   - Blueprint of your pipeline
   - Defines: what tasks, in what order, when to run

2. Operators:
   - BashOperator: Run bash commands
   - PythonOperator: Run Python functions
   - Many more: BranchOperator, EmailOperator, etc.

3. Task Dependencies:
   - >> operator: task_a >> task_b (a before b)
   - << operator: task_b << task_a (same as above)
   - [a, b] >> c: both a and b before c

4. Schedule:
   - None: Manual trigger only
   - '@daily': Once per day
   - '0 */6 * * *': Cron expression (every 6 hours)

5. Catchup:
   - False: Only run for current date
   - True: Run for all past dates (backfill)
"""
