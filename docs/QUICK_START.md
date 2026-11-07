# 🚀 Quick Start Guide - Sprint 1

**Goal**: Get Airflow running locally in 30 minutes

---

## Prerequisites Check

Before starting, make sure you have:

```bash
# Check Docker is installed
docker --version
# Should show: Docker version 20.x or higher

# Check Docker Compose is installed
docker-compose --version
# Should show: Docker Compose version 2.x or higher

# Check Python is installed
python --version
# Should show: Python 3.11 or higher
```

**Don't have Docker?**
- Windows: [Install Docker Desktop](https://docs.docker.com/desktop/install/windows-install/)
- Mac: [Install Docker Desktop](https://docs.docker.com/desktop/install/mac-install/)
- Linux: [Install Docker Engine](https://docs.docker.com/engine/install/)

---

## Step 1: Setup Environment Variables (5 min)

### 1.1 Copy template
```bash
cp .env.example .env
```

### 1.2 Edit `.env` file

For now, just change these (we'll add GCP later):
```bash
# Required for Airflow to start
AIRFLOW_UID=50000

# Optional: Get free API key
OPENWEATHER_API_KEY=your_key_here
```

**How to get OpenWeather API Key** (Free, 2 minutes):
1. Go to: https://home.openweathermap.org/users/sign_up
2. Sign up (free account)
3. Go to: https://home.openweathermap.org/api_keys
4. Copy your API key
5. Paste in `.env` file

**Can I skip the API key for now?**
- Yes! We'll add dummy data first. You can get the key later.

---

## Step 2: Start Airflow (10 min)

### 2.1 Initialize Airflow (First time only)

```bash
# This creates database, admin user, installs dependencies
docker-compose up airflow-init
```

**What's happening?**
- Creating PostgreSQL database for Airflow
- Installing Python packages from requirements.txt
- Creating admin user (username: airflow, password: airflow)

**Expected output**:
```
airflow-init_1  | Airflow initialization complete!
airflow-init_1  | Access UI at: http://localhost:8080
airflow-init_1  | Username: airflow
airflow-init_1  | Password: airflow
airflow-init_1 exited with code 0
```

### 2.2 Start all services

```bash
# -d = detached mode (runs in background)
docker-compose up -d
```

**What's starting?**
- PostgreSQL (database)
- Airflow Webserver (UI)
- Airflow Scheduler (runs DAGs)

### 2.3 Check services are running

```bash
docker-compose ps
```

**Expected output**:
```
NAME                        STATUS
weather_postgres            Up (healthy)
weather_airflow_webserver   Up (healthy)
weather_airflow_scheduler   Up
```

All should show "Up" or "Up (healthy)"

---

## Step 3: Access Airflow UI (2 min)

### 3.1 Open browser

Go to: http://localhost:8080

### 3.2 Login

- **Username**: `airflow`
- **Password**: `airflow`

### 3.3 Verify

You should see:
- Empty DAGs list (no pipelines yet - that's correct!)
- Green status indicators
- No errors in UI

**Screenshot this!** You'll add it to your portfolio later.

---

## Step 4: Verify Installation (5 min)

### 4.1 Check logs (make sure no errors)

```bash
# View all logs
docker-compose logs

# View only webserver logs
docker-compose logs airflow-webserver

# View only scheduler logs
docker-compose logs airflow-scheduler

# Follow logs in real-time
docker-compose logs -f
```

**What to look for**:
- ✅ No ERROR lines
- ✅ "Airflow webserver is ready" message
- ✅ "Scheduler is starting" message

### 4.2 Check directories were created

```bash
ls -la airflow/
```

**Expected**:
```
airflow/
├── dags/          ← Your DAG files go here
├── logs/          ← Task logs appear here
├── plugins/       ← Custom operators (if needed)
└── config/        ← Airflow configs
```

---

## Step 5: Create Your First DAG (10 min)

Let's create a simple "Hello World" DAG to test everything works.

### 5.1 Create DAG file

Create `airflow/dags/test_dag.py`:

```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

def say_hello():
    print("🎉 Hello from Airflow!")
    print("✅ Your Airflow setup is working!")
    return "Success!"

# DAG definition
with DAG(
    dag_id='test_hello_world',
    description='Test DAG to verify Airflow setup',
    schedule=None,  # Manual trigger only
    start_date=datetime(2026, 9, 23),
    catchup=False,
    tags=['test', 'sprint1'],
) as dag:
    
    hello_task = PythonOperator(
        task_id='say_hello',
        python_callable=say_hello,
    )
```

### 5.2 Wait for DAG to appear (30 seconds)

Airflow scans `dags/` folder every 30 seconds.

Refresh Airflow UI: http://localhost:8080

You should see: `test_hello_world` DAG

### 5.3 Run the DAG

1. Click on DAG name: `test_hello_world`
2. Click ▶️ (Play button) → "Trigger DAG"
3. Click on the running task
4. Click "Logs"
5. You should see: `🎉 Hello from Airflow!`

**🎉 Congratulations!** If you see the log message, Airflow is working!

---

## Common Issues & Solutions

### Issue 1: Port 8080 already in use

**Error**: `Bind for 0.0.0.0:8080 failed: port is already allocated`

**Solution**:
```bash
# Stop whatever is using port 8080
# Then try again
docker-compose down
docker-compose up -d
```

Or change port in docker-compose.yml:
```yaml
ports:
  - "8081:8080"  # Use 8081 instead
```

### Issue 2: Permission denied on airflow/logs

**Error**: `Permission denied: '/opt/airflow/logs'`

**Solution**:
```bash
# Linux/Mac
chmod -R 777 airflow/logs

# Windows (in Git Bash or WSL)
# Usually not an issue on Windows
```

### Issue 3: Containers keep restarting

**Check logs**:
```bash
docker-compose logs
```

**Common causes**:
- PostgreSQL not ready → Wait 1 minute, should auto-recover
- Out of memory → Close other Docker containers
- Syntax error in .env → Check .env file has no typos

### Issue 4: DAG not appearing in UI

**Solutions**:
1. Wait 30 seconds (scan interval)
2. Check file is in `airflow/dags/` folder
3. Check for Python syntax errors:
   ```bash
   python airflow/dags/test_dag.py
   ```
4. Check scheduler logs:
   ```bash
   docker-compose logs airflow-scheduler | tail -50
   ```

---

## Useful Commands

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart a specific service
docker-compose restart airflow-scheduler

# View logs
docker-compose logs -f

# Access Airflow container shell
docker exec -it weather_airflow_webserver bash

# Fresh start (deletes database!)
docker-compose down -v
docker-compose up airflow-init
docker-compose up -d

# Check resource usage
docker stats
```

---

## What You Just Learned 🎓

Congratulations! You now understand:

✅ **Docker Compose** - Multi-container orchestration
✅ **Airflow Architecture** - Webserver, Scheduler, Metadata DB
✅ **DAG** - Directed Acyclic Graph (pipeline blueprint)
✅ **Operator** - Task template (PythonOperator, BashOperator)
✅ **Task** - Single unit of work

---

## Next Steps

### Immediate (Sprint 1 continuation):
- [ ] Setup GCP project
- [ ] Create BigQuery dataset
- [ ] Get GCP service account key
- [ ] Test BigQuery connection

### Sprint 2 (Data Ingestion):
- [ ] Build weather API clients
- [ ] Create real weather DAG
- [ ] Load data to BigQuery

---

## Sprint 1 Checklist

- [ ] Docker Desktop installed
- [ ] docker-compose.yml created
- [ ] .env file configured
- [ ] Airflow initialized (airflow-init)
- [ ] All containers running (docker-compose ps)
- [ ] Airflow UI accessible (localhost:8080)
- [ ] Test DAG created and runs successfully
- [ ] Logs show no errors

**Status**: ⬜ Not started | 🟡 In progress | ✅ Complete

---

## Resources

- [Airflow Docs](https://airflow.apache.org/docs/)
- [Docker Compose Docs](https://docs.docker.com/compose/)
- [Our Learning Notes](LEARNING_NOTES.md)

---

**Need help?** Check logs first, then Google the error message!

Last Updated: 2026-09-23
