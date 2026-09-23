# 🚀 Setup Guide

Complete step-by-step instructions to set up the Weather Data Engineering Pipeline.

## Table of Contents
- [Prerequisites](#prerequisites)
- [GCP Setup](#gcp-setup)
- [API Keys](#api-keys)
- [Local Environment](#local-environment)
- [Docker Setup](#docker-setup)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software
- **Docker Desktop** (4.0+)
  - Windows: [Download](https://www.docker.com/products/docker-desktop)
  - Mac: [Download](https://www.docker.com/products/docker-desktop)
  - Linux: `sudo apt install docker.io docker-compose`
- **Python 3.11+**
  - Check: `python --version`
  - Download: [python.org](https://www.python.org/downloads/)
- **Git**
  - Check: `git --version`
  - Download: [git-scm.com](https://git-scm.com/)

### Accounts Needed
- Google Cloud Platform (Free tier)
- OpenWeatherMap (Free API key)

---

## GCP Setup

### 1. Create GCP Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Sign up (you'll get $300 free credits for 90 days)
3. Complete billing setup (required but won't be charged within free tier)

### 2. Create New Project

```bash
# Via Console UI
1. Go to: https://console.cloud.google.com/projectcreate
2. Project Name: "weather-data-engineering"
3. Click "Create"
4. Note your PROJECT_ID (will be used later)

# Or via gcloud CLI (after installing gcloud)
gcloud projects create weather-data-engineering
gcloud config set project weather-data-engineering
```

### 3. Enable Required APIs

```bash
# Via Console UI
Go to: APIs & Services > Enable APIs and Services
Search and enable:
- BigQuery API
- BigQuery Data Transfer API

# Or via gcloud CLI
gcloud services enable bigquery.googleapis.com
gcloud services enable bigquerydatatransfer.googleapis.com
```

### 4. Create BigQuery Dataset

```bash
# Via Console UI
1. Go to BigQuery: https://console.cloud.google.com/bigquery
2. Click your project name
3. Click "CREATE DATASET"
   - Dataset ID: weather_data
   - Location: us-central1 (or closest to you)
   - Default table expiration: Never
4. Click "CREATE DATASET"

# Or via bq CLI
bq --location=us-central1 mk --dataset weather_data
```

### 5. Create Service Account

```bash
# Via Console UI
1. Go to: IAM & Admin > Service Accounts
2. Click "CREATE SERVICE ACCOUNT"
3. Service account details:
   - Name: weather-pipeline-sa
   - ID: weather-pipeline-sa
   - Description: Service account for weather data pipeline
4. Click "CREATE AND CONTINUE"
5. Grant roles:
   - BigQuery Data Editor
   - BigQuery Job User
6. Click "DONE"

# Or via gcloud CLI
gcloud iam service-accounts create weather-pipeline-sa \
    --display-name="Weather Pipeline Service Account"

gcloud projects add-iam-policy-binding weather-data-engineering \
    --member="serviceAccount:weather-pipeline-sa@weather-data-engineering.iam.gserviceaccount.com" \
    --role="roles/bigquery.dataEditor"

gcloud projects add-iam-policy-binding weather-data-engineering \
    --member="serviceAccount:weather-pipeline-sa@weather-data-engineering.iam.gserviceaccount.com" \
    --role="roles/bigquery.jobUser"
```

### 6. Create and Download Service Account Key

```bash
# Via Console UI
1. Go to: IAM & Admin > Service Accounts
2. Click on "weather-pipeline-sa@..."
3. Go to "KEYS" tab
4. Click "ADD KEY" > "Create new key"
5. Select "JSON"
6. Click "CREATE"
7. Save file as: gcp-credentials.json
8. IMPORTANT: Keep this file secure, never commit to git!

# Or via gcloud CLI
gcloud iam service-accounts keys create gcp-credentials.json \
    --iam-account=weather-pipeline-sa@weather-data-engineering.iam.gserviceaccount.com
```

### 7. Move Credentials to Project

```bash
# Create credentials directory
mkdir -p credentials

# Move the downloaded JSON file
mv ~/Downloads/gcp-credentials.json credentials/

# Secure the file
chmod 600 credentials/gcp-credentials.json
```

---

## API Keys

### OpenWeatherMap API

1. Go to [OpenWeatherMap](https://openweathermap.org/api)
2. Sign up for free account
3. Go to [API Keys](https://home.openweathermap.org/api_keys)
4. Copy your API key
5. Free tier: 1,000 calls/day (sufficient for this project)

### Open-Meteo API

- **No API key required!** ✅
- Open source weather API
- Free unlimited access

---

## Local Environment

### 1. Clone Repository

```bash
git clone <your-repo-url>
cd data-engineer
```

### 2. Create Virtual Environment

```bash
# Create venv
python -m venv venv

# Activate
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

# Verify
which python  # Should point to venv
```

### 3. Install Python Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Verify installations
python -c "import airflow; print(airflow.__version__)"
python -c "import google.cloud.bigquery; print('BigQuery client OK')"
```

### 4. Configure Environment Variables

```bash
# Copy template
cp .env.example .env

# Edit .env file
nano .env  # or use your preferred editor
```

**.env file contents:**
```bash
# GCP Configuration
GCP_PROJECT_ID=weather-data-engineering
GCP_DATASET_ID=weather_data
GOOGLE_APPLICATION_CREDENTIALS=/opt/airflow/credentials/gcp-credentials.json

# API Keys
OPENWEATHER_API_KEY=your_openweathermap_api_key_here

# Cities (comma-separated)
CITIES=Jakarta,Surabaya,Bandung,Medan,Makassar

# Airflow Configuration
AIRFLOW_UID=50000
AIRFLOW__CORE__EXECUTOR=LocalExecutor
AIRFLOW__CORE__LOAD_EXAMPLES=False
AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION=True

# Database (for Airflow metadata)
POSTGRES_USER=airflow
POSTGRES_PASSWORD=airflow
POSTGRES_DB=airflow
```

---

## Docker Setup

### 1. Initialize Airflow

```bash
# Create necessary directories
mkdir -p ./airflow/dags ./airflow/logs ./airflow/plugins ./airflow/config
mkdir -p ./credentials

# Set permissions
chmod -R 777 ./airflow/logs

# Initialize Airflow database
docker-compose up airflow-init
```

### 2. Start Services

```bash
# Start all services
docker-compose up -d

# Verify services are running
docker-compose ps

# Expected output:
# NAME                     STATUS
# airflow-webserver        Up (healthy)
# airflow-scheduler        Up (healthy)
# postgres                 Up (healthy)
```

### 3. Access Airflow UI

```bash
# Open browser
http://localhost:8080

# Default credentials
Username: airflow
Password: airflow
```

---

## Verification

### 1. Check Airflow Connection

```bash
# List DAGs
docker-compose exec airflow-webserver airflow dags list

# Should see: weather_ingestion_pipeline
```

### 2. Test BigQuery Connection

```bash
# Test from Python
python << EOF
from google.cloud import bigquery
import os

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'credentials/gcp-credentials.json'
client = bigquery.Client(project='weather-data-engineering')

# List datasets
datasets = list(client.list_datasets())
print(f"Found {len(datasets)} datasets")
for dataset in datasets:
    print(f"  - {dataset.dataset_id}")
EOF
```

### 3. Test API Keys

```bash
# Test OpenWeatherMap
python << EOF
import requests
import os

api_key = os.getenv('OPENWEATHER_API_KEY')
url = f"https://api.openweathermap.org/data/2.5/weather?q=Jakarta&appid={api_key}"
response = requests.get(url)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
EOF

# Test Open-Meteo
curl "https://api.open-meteo.com/v1/forecast?latitude=-6.2088&longitude=106.8456&current_weather=true"
```

### 4. Run Test DAG

```bash
# Trigger test run
docker-compose exec airflow-webserver airflow dags trigger weather_ingestion_pipeline

# Watch logs
docker-compose logs -f airflow-scheduler
```

---

## Troubleshooting

### Issue: Docker containers won't start

```bash
# Check Docker is running
docker ps

# Check logs
docker-compose logs

# Restart
docker-compose down
docker-compose up -d
```

### Issue: Permission denied on credentials

```bash
# Fix permissions
chmod 600 credentials/gcp-credentials.json

# Ensure correct path in .env
echo $GOOGLE_APPLICATION_CREDENTIALS
```

### Issue: BigQuery authentication failed

```bash
# Verify service account has correct roles
gcloud projects get-iam-policy weather-data-engineering \
    --flatten="bindings[].members" \
    --filter="bindings.members:weather-pipeline-sa@*"

# Should show:
# - roles/bigquery.dataEditor
# - roles/bigquery.jobUser
```

### Issue: Airflow DAG not showing

```bash
# Check DAG for syntax errors
docker-compose exec airflow-webserver python /opt/airflow/dags/weather_pipeline.py

# Refresh DAGs
docker-compose exec airflow-webserver airflow dags reserialize
```

### Issue: OpenWeatherMap API rate limit

```bash
# Check remaining calls
# Response header: X-RateLimit-Remaining

# Reduce frequency in DAG if needed
# Change schedule from */6 to */12 hours
```

### Issue: Port 8080 already in use

```bash
# Find process using port
# Windows
netstat -ano | findstr :8080
# Mac/Linux
lsof -i :8080

# Kill process or change Airflow port in docker-compose.yml
# ports:
#   - "8081:8080"
```

---

## Next Steps

After successful setup:

1. ✅ Review DAG in Airflow UI
2. ✅ Enable the DAG (toggle switch)
3. ✅ Trigger manual run to test
4. ✅ Check BigQuery tables are created
5. ✅ Run dbt transformations
6. ✅ Launch Streamlit dashboard

See [README.md](../README.md) for usage instructions.

---

## Useful Commands

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v

# View logs
docker-compose logs -f [service-name]

# Restart specific service
docker-compose restart airflow-scheduler

# Execute command in container
docker-compose exec airflow-webserver bash

# Check Airflow version
docker-compose exec airflow-webserver airflow version
```

---

## Security Checklist

- [ ] Service account key secured (not in git)
- [ ] .env file in .gitignore
- [ ] Minimum IAM permissions granted
- [ ] API keys kept secret
- [ ] Docker containers regularly updated
- [ ] Logs don't expose sensitive data

---

**Need help?** Check [Troubleshooting](#troubleshooting) or review error logs.
