# 🎓 Data Engineering Learning Notes

**Project**: Weather Data Engineering Pipeline  
**Learner**: First Data Engineering Project  
**Last Updated**: 2026-09-23

---

## 📖 Table of Contents

1. [What is Data Engineering?](#what-is-data-engineering)
2. [The Modern Data Stack](#the-modern-data-stack)
3. [Our Tech Stack Explained](#our-tech-stack-explained)
4. [Key Concepts](#key-concepts)
5. [Learning Resources](#learning-resources)

---

## What is Data Engineering?

### Simple Definition
**Data Engineering** adalah proses membuat "jalan tol" untuk data:
- Mengambil data dari berbagai sumber (API, database, files)
- Membersihkan dan mengubah data menjadi format yang berguna
- Menyimpan data di tempat yang mudah diakses
- Memastikan data berkualitas dan reliable
- Membuat data siap untuk analisis/dashboard

### Real-World Analogy: Restaurant Kitchen

```
Data Engineering Pipeline = Restaurant Kitchen Operations

┌─────────────────────────────────────────────────────────┐
│ RAW INGREDIENTS        → PREPARATION → QUALITY CHECK    │
│ (API Data)             (Transform)    (Validation)      │
│                                                          │
│ Suppliers deliver      Chef cleans    Head chef         │
│ vegetables, meat   →   and cooks   →  tastes food   →   │
│ (API calls)            (dbt)          (GE)              │
│                                                          │
│                        SERVE TO CUSTOMERS                │
│                        (Dashboard/Analytics)             │
└─────────────────────────────────────────────────────────┘
```

**You are the Head Chef (Data Engineer)** who:
- Decides what ingredients to buy (which APIs)
- Designs recipes (data transformations)
- Sets quality standards (data validation)
- Ensures kitchen runs smoothly (orchestration)

---

## The Modern Data Stack

### What is it?
"Modern Data Stack" = Set of tools yang umum dipakai di industri data engineering saat ini.

### Why These Tools?

| Traditional (Old Way) | Modern (Our Way) | Why Changed? |
|----------------------|------------------|--------------|
| Manual cron jobs | **Airflow** | Automated, monitored, visual |
| Stored procedures | **dbt** | Version controlled, testable |
| Manual data checks | **Great Expectations** | Automated, standardized |
| On-premise servers | **Cloud (BigQuery)** | Scalable, cost-effective |
| Manual dashboards | **Streamlit** | Interactive, easy to update |

---

## Our Tech Stack Explained

### 1. Apache Airflow - The Orchestra Conductor 🎼

**What**: Workflow orchestration tool  
**Analogy**: Conductor yang mengatur kapan setiap musisi bermain  
**In Our Project**: Mengatur kapan fetch API, kapan transform, kapan validate

#### Why Airflow?

**Problem Without Airflow**:
```python
# main.py - Imagine running this manually every 6 hours!
def run_pipeline():
    fetch_weather_data()      # What if this fails at 3 AM?
    load_to_bigquery()        # How do you know it succeeded?
    transform_data()          # What if previous step failed?
    validate_quality()        # No visibility!
```

**Solution With Airflow**:
```python
# weather_dag.py - Airflow handles scheduling, retries, monitoring
with DAG('weather_pipeline', schedule='0 */6 * * *'):
    fetch = PythonOperator(task_id='fetch_data', ...)
    load = PythonOperator(task_id='load_bigquery', ...)
    transform = PythonOperator(task_id='transform', ...)
    
    fetch >> load >> transform  # Dependencies clear!
```

**Benefits**:
- ✅ Automatic scheduling (every 6 hours)
- ✅ Retry on failure (3 retries with backoff)
- ✅ Visual monitoring (Web UI at localhost:8080)
- ✅ Email/Slack alerts on failure
- ✅ Dependency management (task B waits for task A)
- ✅ History tracking (see all past runs)

**Key Concepts**:
- **DAG** (Directed Acyclic Graph) = Blueprint of your pipeline
- **Task** = Single unit of work (fetch data, load data, etc.)
- **Operator** = Template for a task (PythonOperator, BashOperator)
- **Schedule** = Cron expression (when to run)

---

### 2. Google BigQuery - The Data Warehouse 🏢

**What**: Cloud-based data warehouse (serverless SQL database)  
**Analogy**: Giant Excel spreadsheet di cloud yang bisa handle milyaran baris  
**In Our Project**: Menyimpan semua weather data kita

#### Why BigQuery?

**Traditional Database Problems**:
- Need to setup/maintain servers
- Slow for large datasets (millions of rows)
- Expensive infrastructure
- Complex scaling

**BigQuery Solution**:
- Serverless (no servers to manage)
- Fast (petabyte-scale queries in seconds)
- Pay-per-query (only pay what you use)
- Free tier (1TB queries/month)
- Integrated with Google Cloud

**Key Features We Use**:

1. **Partitioning** (Performance optimization)
```sql
-- Without partitioning: Scans entire table (expensive!)
SELECT * FROM weather WHERE date = '2026-09-23';  -- Scans 1M rows

-- With partitioning by date: Only scans relevant partition
SELECT * FROM weather WHERE date = '2026-09-23';  -- Scans 120 rows!
```

2. **Clustering** (Further optimization)
```sql
-- Clustered by city_name
-- Queries filtering by city are faster and cheaper
SELECT * FROM weather 
WHERE city_name = 'Jakarta' AND date = '2026-09-23';
-- Only scans Jakarta partition!
```

**Cost Optimization**:
- This project: ~$0/month (stays in free tier)
- 15MB storage (free up to 10GB)
- 100MB queries/month (free up to 1TB)

---

### 3. dbt (Data Build Tool) - The Transformer 🔄

**What**: Transform raw data into analytics-ready models using SQL  
**Analogy**: LEGO instruction manual - defines how to build final model from pieces  
**In Our Project**: Mengubah raw weather JSON menjadi clean tables

#### Why dbt?

**Old Way (Bad)**:
```sql
-- transform.sql - Runs in production, no version control
-- If this breaks, good luck debugging!
DROP TABLE IF EXISTS clean_weather;
CREATE TABLE clean_weather AS
SELECT 
    JSON_EXTRACT(raw_data, '$.temp') as temperature,
    JSON_EXTRACT(raw_data, '$.humidity') as humidity,
    ...
FROM raw_weather;
-- No tests, no documentation, no lineage tracking
```

**dbt Way (Good)**:
```sql
-- models/staging/stg_weather.sql
-- Version controlled, tested, documented
{{ config(
    materialized='view',
    tags=['staging']
) }}

SELECT 
    {{ celsius_to_fahrenheit('temperature') }} as temp_f,
    humidity,
    city_name,
    recorded_at
FROM {{ source('raw', 'openweather') }}
WHERE recorded_at >= current_date() - 7  -- Only last 7 days
```

**Benefits**:
- ✅ **Version control** - Track changes in Git
- ✅ **Testing** - Built-in tests (not null, unique, relationships)
- ✅ **Documentation** - Auto-generate docs with lineage graph
- ✅ **Modularity** - Reuse code with macros/models
- ✅ **Environment management** - Dev/Staging/Prod configs
- ✅ **Dependency resolution** - Builds models in correct order

**Key Concepts**:

1. **Models** = SQL files that create tables/views
2. **Sources** = Raw data from ingestion
3. **Staging** = First cleanup layer (stg_*)
4. **Marts** = Business logic layer (fact_*, dim_*)
5. **Macros** = Reusable SQL functions
6. **Tests** = Data quality assertions

**Our dbt Project Structure**:
```
dbt/models/
├── staging/              # Layer 1: Clean raw data
│   ├── stg_openweather.sql
│   ├── stg_openmeteo.sql
│   └── stg_weather_unified.sql
├── marts/                # Layer 2: Business logic
│   ├── dim_cities.sql          # Dimension: City master data
│   ├── dim_date.sql            # Dimension: Date spine
│   ├── fact_weather.sql        # Fact: Weather observations
│   ├── agg_daily_weather.sql   # Aggregation: Daily stats
│   └── agg_weekly_weather.sql  # Aggregation: Weekly trends
└── schema.yml            # Tests & documentation
```

---

### 4. Great Expectations - The Quality Inspector ✅

**What**: Data quality and validation framework  
**Analogy**: Airport security scanner - checks if data meets standards  
**In Our Project**: Validates weather data is within expected ranges

#### Why Great Expectations?

**Without Validation**:
```python
# Bad data gets into your dashboard silently
{
    "temperature": 999,      # Bug in API?
    "humidity": -50,         # Impossible value
    "city": null            # Missing data
}
# Your dashboard shows wrong insights, nobody notices until CEO asks "Why is Jakarta 999°C?"
```

**With Great Expectations**:
```python
# Validation catches bad data immediately
expect_column_values_to_be_between(
    column="temperature",
    min_value=-50,
    max_value=60
)
# Pipeline fails, alerts sent, no bad data reaches dashboard
```

**Types of Checks We Use**:

1. **Schema Validation**
   - Expected columns exist
   - Correct data types (int, float, string)

2. **Data Range Validation**
   - Temperature: -50°C to 60°C
   - Humidity: 0% to 100%
   - Pressure: 900 to 1100 hPa

3. **Null Checks**
   - Mandatory fields not null (city_name, temperature)
   - Optional fields can be null (weather_description)

4. **Freshness Checks**
   - Data is recent (< 7 hours old)
   - No future dates

5. **Consistency Checks**
   - OpenWeather and Open-Meteo data match (within 5% tolerance)
   - All 5 cities present in every batch

**Key Concepts**:
- **Expectation** = Single validation rule
- **Expectation Suite** = Collection of expectations for a dataset
- **Checkpoint** = Runs suite and generates report
- **Data Docs** = Web UI showing validation results

---

### 5. Streamlit - The Dashboard Builder 📊

**What**: Python library for building interactive web apps  
**Analogy**: PowerPoint + Excel on steroids, but interactive  
**In Our Project**: Show weather trends, pipeline health, data quality

#### Why Streamlit?

**Traditional Dashboard (Hard)**:
```javascript
// React + D3.js + API = Weeks of work
import React from 'react';
import { useEffect, useState } from 'react';
import * as d3 from 'd3';
// 500+ lines of code for one chart...
```

**Streamlit Dashboard (Easy)**:
```python
# app.py - Same result in minutes
import streamlit as st
import pandas as pd

st.title("🌦️ Weather Dashboard")
df = pd.read_gbq("SELECT * FROM weather.fact_weather")
st.line_chart(df, x='date', y='temperature')
# That's it! Interactive chart ready.
```

**Features**:
- ✅ Pure Python (no HTML/CSS/JS needed)
- ✅ Auto-refresh on code change
- ✅ Built-in widgets (sliders, selectors, filters)
- ✅ Caching for performance
- ✅ Easy deployment (Streamlit Cloud free)

**Our Dashboard Pages**:
1. **Overview** - Current weather all cities
2. **Trends** - 7-day, 30-day temperature charts
3. **Comparison** - Compare cities side-by-side
4. **Data Quality** - Validation results, pipeline health
5. **Monitoring** - API performance, last run status

---

### 6. Docker - The Environment Container 🐳

**What**: Platform to run applications in isolated containers  
**Analogy**: Shipping containers - works the same everywhere  
**In Our Project**: Run Airflow without installing dependencies

#### Why Docker?

**Problem (Without Docker)**:
```bash
# On your laptop:
pip install airflow==2.8.1  # Works!
airflow webserver           # Works!

# On your friend's laptop:
pip install airflow==2.8.1  # ERROR: Python version mismatch
# or: "Works on my machine" syndrome
```

**Solution (With Docker)**:
```bash
# On ANY laptop/server:
docker-compose up           # Works! Same environment everywhere
```

**Benefits**:
- ✅ Consistent environment (dev = production)
- ✅ Easy setup (one command: docker-compose up)
- ✅ Isolation (Airflow doesn't mess with your Python)
- ✅ Portability (works on Mac, Windows, Linux)

**Key Concepts**:
- **Image** = Template (like a class in OOP)
- **Container** = Running instance (like an object)
- **Dockerfile** = Recipe to build an image
- **docker-compose.yml** = Define multiple containers

---

## Key Concepts

### 1. ETL vs ELT

**ETL (Old Way)**:
- **E**xtract → **T**ransform → **L**oad
- Transform data before loading (slow)
- Example: Download CSV, clean in Python, upload clean data

**ELT (Modern Way)** ← We use this!
- **E**xtract → **L**oad → **T**ransform
- Load raw data first, transform in warehouse (fast)
- Example: Load raw JSON to BigQuery, transform with dbt

**Why ELT is Better**:
- Faster ingestion (load immediately)
- Keep raw data (can re-transform later)
- Leverage warehouse compute power (BigQuery is fast)
- Easier debugging (raw data available)

### 2. Idempotency

**Definition**: Running the same operation multiple times = same result

**Bad (Not Idempotent)**:
```python
def load_data():
    # Problem: Running twice inserts duplicates!
    df = fetch_weather()
    df.to_gbq('weather.raw_data', if_exists='append')
```

**Good (Idempotent)**:
```python
def load_data():
    # Safe: Always same result, no duplicates
    df = fetch_weather()
    df['load_date'] = today()
    # Delete today's data first, then insert
    client.query("DELETE FROM weather.raw_data WHERE load_date = CURRENT_DATE()")
    df.to_gbq('weather.raw_data', if_exists='append')
```

**Why Important**:
- Airflow retries failed tasks
- You might manually re-run a pipeline
- No duplicates in data = correct analytics

### 3. Data Modeling: Star Schema

**What**: Organize data into Facts (measurements) and Dimensions (context)

**Our Schema**:
```
         ┌─────────────┐
         │  dim_cities │
         │  (5 rows)   │
         └──────┬──────┘
                │
         ┌──────▼──────────────┐         ┌─────────────┐
         │ fact_weather_obs    │─────────│  dim_date   │
         │  (Millions of rows) │         │ (365 rows)  │
         └─────────────────────┘         └─────────────┘

Fact Table: What happened?
- temperature, humidity, pressure
- Foreign keys: city_id, date_id

Dimension Tables: Context
- dim_cities: Jakarta, Surabaya, ...
- dim_date: 2026-09-23, metadata (day_of_week, month, quarter)
```

**Benefits**:
- Easier queries (JOIN dimensions to fact)
- Better performance (small dimension tables)
- Business-friendly (analysts understand)

### 4. Data Quality Layers

```
┌─────────────────────────────────────────────────────┐
│ Layer 1: Schema Validation (Great Expectations)    │
│ - Correct columns? Correct types?                  │
└───────────────────┬─────────────────────────────────┘
                    ▼
┌─────────────────────────────────────────────────────┐
│ Layer 2: Range Validation (Great Expectations)     │
│ - Values within expected ranges?                   │
└───────────────────┬─────────────────────────────────┘
                    ▼
┌─────────────────────────────────────────────────────┐
│ Layer 3: Business Logic Tests (dbt tests)          │
│ - Relationships valid? No duplicates?              │
└───────────────────┬─────────────────────────────────┘
                    ▼
┌─────────────────────────────────────────────────────┐
│ Layer 4: Consistency Checks                        │
│ - Data from multiple sources consistent?           │
└─────────────────────────────────────────────────────┘
```

### 5. Incremental Processing

**Full Refresh (Expensive)**:
```sql
-- Process all data every time (1M rows)
SELECT * FROM raw_weather;  -- Slow, expensive
```

**Incremental (Smart)**:
```sql
-- Only process new data (120 rows)
SELECT * FROM raw_weather 
WHERE load_date = CURRENT_DATE();  -- Fast, cheap
```

**dbt Incremental Strategy**:
```sql
-- models/fact_weather.sql
{{ config(materialized='incremental') }}

SELECT * FROM {{ ref('stg_weather_unified') }}
{% if is_incremental() %}
    WHERE recorded_at > (SELECT MAX(recorded_at) FROM {{ this }})
{% endif %}
```

---

## Learning Resources

### Recommended Learning Path

**Week 1-2: Foundations**
1. ✅ Understand pipeline architecture (this doc)
2. ✅ Learn basic SQL (BigQuery SQL)
3. ✅ Python basics (pandas, requests)
4. ✅ Git basics (commit, push, pull)

**Week 3-4: Orchestration**
5. ⏳ Airflow concepts (DAGs, operators, tasks)
6. ⏳ Docker basics (images, containers)
7. ⏳ Build first pipeline

**Week 5-6: Transformation**
8. ⏳ dbt fundamentals (models, tests, docs)
9. ⏳ Data modeling (star schema)
10. ⏳ SQL optimization

**Week 7-8: Quality & Visualization**
11. ⏳ Great Expectations (expectations, checkpoints)
12. ⏳ Streamlit (dashboards)
13. ⏳ Production best practices

### Free Courses

**Airflow**:
- [Airflow Official Tutorial](https://airflow.apache.org/docs/apache-airflow/stable/tutorial.html)
- [Marc Lamberti's Airflow Course](https://www.youtube.com/watch?v=K9AnJ9_ZAXE) (YouTube)

**dbt**:
- [dbt Fundamentals](https://courses.getdbt.com/courses/fundamentals) (Free, official)
- [dbt Learn SQL](https://docs.getdbt.com/docs/building-a-dbt-project/building-models)

**BigQuery**:
- [BigQuery for Data Analysts](https://cloud.google.com/bigquery/docs/quickstarts)
- [SQL for BigQuery](https://cloud.google.com/bigquery/docs/reference/standard-sql/query-syntax)

**Great Expectations**:
- [Official Tutorial](https://docs.greatexpectations.io/docs/tutorials/getting_started/tutorial_overview)

**Streamlit**:
- [30 Days of Streamlit](https://30days.streamlit.app/)

### Books

1. **Fundamentals of Data Engineering** by Joe Reis & Matt Housley
   - Best comprehensive intro to modern data engineering

2. **The Data Warehouse Toolkit** by Ralph Kimball
   - Star schema modeling (still relevant!)

3. **Designing Data-Intensive Applications** by Martin Kleppmann
   - Advanced concepts (for later)

### YouTube Channels

- **Seattle Data Guy** - Data engineering career advice
- **Data Engineering Simplified** - Hands-on tutorials
- **Andreas Kretz** - DE Academy founder

---

## Common Pitfalls (Avoid These!)

### ❌ Pitfall 1: Over-engineering
**Wrong**: "I need Kafka, Spark, Kubernetes for 5 cities weather data"  
**Right**: "Airflow + BigQuery is enough for my scale"

### ❌ Pitfall 2: No testing
**Wrong**: Deploy to production without tests  
**Right**: Write dbt tests, GE validations, unit tests

### ❌ Pitfall 3: Ignoring costs
**Wrong**: `SELECT *` on 1TB table in BigQuery  
**Right**: Use partitions, clusters, only select needed columns

### ❌ Pitfall 4: No monitoring
**Wrong**: Pipeline fails silently at 3 AM  
**Right**: Airflow alerts on Slack/email

### ❌ Pitfall 5: Not idempotent
**Wrong**: Running twice creates duplicates  
**Right**: Upsert logic, date-based deletes

---

## Interview-Ready Talking Points

When discussing this project in interviews, highlight:

### Technical Skills
✅ "Built end-to-end ELT pipeline with Airflow orchestration"  
✅ "Implemented star schema in BigQuery with partitioning/clustering"  
✅ "Used dbt for modular, tested transformations"  
✅ "Automated data quality validation with Great Expectations"  
✅ "Dockerized infrastructure for reproducibility"

### Best Practices
✅ "Implemented idempotent pipeline (safe retries)"  
✅ "Cost-optimized for GCP free tier ($0/month)"  
✅ "Comprehensive testing (dbt tests, GE validations, pytest)"  
✅ "Full documentation (README, architecture, API docs)"  
✅ "Version controlled with Git"

### Problem Solving
✅ "Handled API rate limits with exponential backoff"  
✅ "Reconciled data from multiple sources (OpenWeather vs Open-Meteo)"  
✅ "Designed incremental loading to reduce costs"  
✅ "Implemented data lineage for debugging"

---

## Next Steps

1. **Finish Sprint 0**: Git setup (manual commands)
2. **Start Sprint 1**: Setup Docker + Airflow
3. **Build Sprint 2**: First data ingestion
4. **Learn by doing**: Follow this doc as reference

**Remember**: It's okay to not understand everything at once. Build incrementally, learn as you go!

---

**Questions?** Add them here as you learn:

- Q: [Your question]
- A: [Answer you discovered]

---

Last Updated: 2026-09-23  
Next Update: After Sprint 1 completion
