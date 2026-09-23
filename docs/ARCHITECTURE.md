# 🏗️ Architecture Documentation

Technical deep-dive into the Weather Data Engineering Pipeline architecture.

## Table of Contents
- [System Overview](#system-overview)
- [Data Flow](#data-flow)
- [Component Details](#component-details)
- [Data Models](#data-models)
- [Infrastructure](#infrastructure)
- [Design Decisions](#design-decisions)
- [Scalability Considerations](#scalability-considerations)

---

## System Overview

### Architecture Pattern

This pipeline implements a **modern ELT (Extract, Load, Transform)** pattern with cloud-native data warehouse:

```
Extract → Load → Transform → Serve
  ↓        ↓        ↓         ↓
 APIs   BigQuery   dbt     Streamlit
```

**Why ELT over ETL?**
- Leverage BigQuery's computational power
- Keep raw data for reprocessing
- Faster initial load
- SQL-based transformations (dbt)
- Better auditability

### High-Level Components

```
┌──────────────────────────────────────────────────────┐
│                  Presentation Layer                   │
│                  (Streamlit Dashboard)                │
└──────────────┬───────────────────────────────────────┘
               │ Reads from
               ↓
┌──────────────────────────────────────────────────────┐
│              Analytics Layer (dbt)                    │
│  Dimensional Models + Aggregations                    │
└──────────────┬───────────────────────────────────────┘
               │ Transforms
               ↓
┌──────────────────────────────────────────────────────┐
│         Storage Layer (BigQuery)                      │
│  Raw Data + Staging + Data Warehouse                  │
└──────────────┬───────────────────────────────────────┘
               │ Receives from
               ↓
┌──────────────────────────────────────────────────────┐
│       Orchestration Layer (Airflow)                   │
│  Scheduling + Monitoring + Error Handling             │
└──────────────┬───────────────────────────────────────┘
               │ Orchestrates
               ↓
┌──────────────────────────────────────────────────────┐
│          Ingestion Layer (Python)                     │
│  API Clients + Validation + Error Handling            │
└──────────────┬───────────────────────────────────────┘
               │ Fetches from
               ↓
┌──────────────────────────────────────────────────────┐
│              Data Sources                             │
│  OpenWeatherMap API | Open-Meteo API                 │
└──────────────────────────────────────────────────────┘
```

---

## Data Flow

### Detailed Pipeline Flow

```
┌─────────────────────────────────────────────────────────┐
│ STEP 1: Data Ingestion (Every 6 hours)                 │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Airflow DAG Triggered (0 */6 * * *)                  │
│         ↓                                               │
│  Task: fetch_openweather_data                          │
│    • Call OpenWeatherMap API for 5 cities             │
│    • Parse JSON response                               │
│    • Extract: temp, humidity, pressure, wind, weather  │
│    • Add metadata: source, timestamp, city_id          │
│    • Store in memory (XCom)                            │
│         ↓                                               │
│  Task: fetch_openmeteo_data                            │
│    • Call Open-Meteo API for same 5 cities            │
│    • Parse JSON response                               │
│    • Extract same metrics                              │
│    • Standardize format to match OpenWeather           │
│    • Store in memory (XCom)                            │
│         ↓                                               │
│  Task: validate_raw_data                               │
│    • Schema validation (expected fields present)       │
│    • Type validation (numeric, string, datetime)       │
│    • Range checks (temp: -50 to 60°C, etc.)           │
│    • Null checks (mandatory fields)                    │
│    • If validation fails → Raise alert, stop pipeline  │
│    • If valid → Continue                               │
│                                                         │
└─────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 2: Load to BigQuery (Raw Layer)                   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Task: load_to_bigquery                                │
│    • Batch load JSON data                              │
│    • Insert into:                                      │
│      - weather_data.raw_openweather                    │
│      - weather_data.raw_openmeteo                      │
│    • Partitioned by DATE(timestamp)                    │
│    • Clustered by city_name                            │
│    • Mode: APPEND (never overwrite)                    │
│    • Idempotent: Check timestamp to avoid duplicates   │
│                                                         │
│  BigQuery Tables Created:                              │
│  ┌─────────────────────────────────────┐              │
│  │ raw_openweather                     │              │
│  │ - ingestion_id (STRING)             │              │
│  │ - timestamp (TIMESTAMP)             │              │
│  │ - city_name (STRING)                │              │
│  │ - temperature (FLOAT64)             │              │
│  │ - feels_like (FLOAT64)              │              │
│  │ - humidity (INT64)                  │              │
│  │ - pressure (INT64)                  │              │
│  │ - wind_speed (FLOAT64)              │              │
│  │ - weather_condition (STRING)        │              │
│  │ - source (STRING)                   │              │
│  │ - loaded_at (TIMESTAMP)             │              │
│  └─────────────────────────────────────┘              │
│                                                         │
└─────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 3: Transform with dbt (Analytics Layer)           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Task: run_dbt_transformations                         │
│    • Execute: dbt run --models +all                    │
│                                                         │
│  Transformation Flow:                                   │
│                                                         │
│  1. Staging Layer (stg_*)                              │
│     • stg_weather_unified                              │
│       - Union OpenWeather + OpenMeteo                  │
│       - Standardize column names                       │
│       - Convert units (Kelvin → Celsius)               │
│       - Add quality flags                              │
│                                                         │
│  2. Dimension Tables (dim_*)                           │
│     • dim_cities                                       │
│       - city_id (PK)                                   │
│       - city_name, country, latitude, longitude        │
│       - SCD Type 1 (current values only)               │
│     • dim_date                                         │
│       - date_id (PK)                                   │
│       - full_date, year, month, day, quarter           │
│       - is_weekend, day_name                           │
│       - Pre-generated for 2 years                      │
│                                                         │
│  3. Fact Table (fact_*)                                │
│     • fact_weather_observations                        │
│       - observation_id (PK)                            │
│       - city_id (FK → dim_cities)                      │
│       - date_id (FK → dim_date)                        │
│       - timestamp                                      │
│       - temperature, humidity, pressure, wind          │
│       - weather_condition                              │
│       - source                                         │
│       - data_quality_score                             │
│                                                         │
│  4. Aggregation Tables (agg_*)                         │
│     • agg_daily_weather                                │
│       - date, city                                     │
│       - avg/min/max temperature                        │
│       - avg humidity, pressure                         │
│       - dominant weather condition                     │
│     • agg_weekly_weather                               │
│       - Similar to daily but weekly aggregates         │
│                                                         │
│  dbt Tests Run Automatically:                          │
│    • Unique key constraints                            │
│    • Not null checks                                   │
│    • Referential integrity (FK checks)                 │
│    • Accepted values (weather conditions)              │
│    • Custom tests (temperature ranges)                 │
│                                                         │
└─────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 4: Data Quality Validation (Great Expectations)   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Task: run_data_quality_checks                         │
│    • Run checkpoint: weather_checkpoint                │
│                                                         │
│  Expectations Validated:                                │
│    1. Row count expectations                           │
│       - Should have 5 cities × 2 sources = 10 rows     │
│    2. Column value expectations                        │
│       - Temperature: -50 to 60°C                       │
│       - Humidity: 0 to 100%                            │
│       - Pressure: 900 to 1100 hPa                      │
│    3. Freshness expectations                           │
│       - Latest timestamp < 7 hours old                 │
│    4. Completeness expectations                        │
│       - No nulls in mandatory fields                   │
│    5. Consistency expectations                         │
│       - Cross-source variance < 5°C for same city      │
│                                                         │
│  Validation Report Generated:                           │
│    • HTML report with pass/fail status                 │
│    • Stored in: great_expectations/uncommitted/        │
│    • Metrics logged to Airflow                         │
│                                                         │
│  If validation fails:                                   │
│    • Alert sent (email/Slack)                          │
│    • Pipeline marked as FAILED                         │
│    • Data still in BigQuery (manual review needed)     │
│                                                         │
└─────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 5: Notification & Monitoring                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Task: notify_completion                               │
│    • Log success to Airflow                            │
│    • Update pipeline metrics:                          │
│      - Records processed                               │
│      - Runtime duration                                │
│      - Data quality score                              │
│    • (Optional) Send Slack notification                │
│                                                         │
│  Airflow Metrics Tracked:                              │
│    • DAG run duration                                  │
│    • Task success/failure rates                        │
│    • Data volume processed                             │
│    • API response times                                │
│                                                         │
└─────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 6: Consumption (Streamlit Dashboard)              │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Streamlit App queries BigQuery:                       │
│    • Reads from: agg_daily_weather, agg_weekly_weather │
│    • Displays:                                         │
│      - Current weather for all cities                  │
│      - Temperature trend charts (7d, 30d)              │
│      - Weather comparison matrix                       │
│      - Pipeline health dashboard                       │
│      - Data quality metrics                            │
│    • Refresh: Every 5 minutes (cached)                 │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. Airflow (Orchestration)

**Version**: 2.8+  
**Executor**: LocalExecutor (single machine)  
**Database**: PostgreSQL (metadata)

**DAG Configuration**:
```python
dag = DAG(
    'weather_ingestion_pipeline',
    schedule_interval='0 */6 * * *',  # Every 6 hours
    start_date=datetime(2026, 1, 1),
    catchup=False,  # Don't backfill
    max_active_runs=1,  # One at a time
    default_args={
        'owner': 'data-engineer',
        'retries': 3,
        'retry_delay': timedelta(minutes=5),
        'email_on_failure': False,
        'depends_on_past': False,
    }
)
```

**Task Dependencies**:
```
fetch_openweather ───┐
                     ├──> validate_raw_data ──> load_to_bigquery ──> 
fetch_openmeteo  ────┘                           run_dbt ──> 
                                                  data_quality_check ──> 
                                                  notify_completion
```

### 2. BigQuery (Data Warehouse)

**Project**: weather-data-pipeline  
**Dataset**: weather_data  
**Region**: us-central1

**Table Optimization**:
- **Partitioning**: By DATE(timestamp) - reduces scan cost
- **Clustering**: By city_name - faster city-specific queries
- **Compression**: Automatic (columnar storage)

**Cost Controls**:
```sql
-- Set maximum bytes billed
SET @@dataset.maxBytesBilled = 100000000;  -- 100MB limit

-- Use table decorators for snapshot access (free)
SELECT * FROM `weather_data.raw_openweather` 
FOR SYSTEM_TIME AS OF TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR);
```

### 3. dbt (Transformation)

**Version**: dbt-bigquery 1.7+  
**Materialization Strategy**:

| Model | Materialization | Why |
|-------|----------------|-----|
| `stg_*` | View | Lightweight, always fresh |
| `dim_*` | Table | Small, infrequently changes |
| `fact_*` | Incremental | Large, append-only |
| `agg_*` | Table | Medium, updated fully |

**Incremental Strategy**:
```sql
-- fact_weather_observations
{{
  config(
    materialized='incremental',
    unique_key='observation_id',
    on_schema_change='append_new_columns',
    partition_by={
      'field': 'timestamp',
      'data_type': 'timestamp',
      'granularity': 'day'
    }
  )
}}

SELECT * FROM {{ ref('stg_weather_unified') }}
{% if is_incremental() %}
  WHERE timestamp > (SELECT MAX(timestamp) FROM {{ this }})
{% endif %}
```

### 4. Great Expectations (Data Quality)

**Expectations Suite**:
```yaml
# weather_expectations.json
expectations:
  - expectation_type: expect_table_row_count_to_be_between
    kwargs: { min_value: 8, max_value: 12 }
  
  - expectation_type: expect_column_values_to_be_in_set
    kwargs:
      column: city_name
      value_set: [Jakarta, Surabaya, Bandung, Medan, Makassar]
  
  - expectation_type: expect_column_values_to_be_between
    kwargs:
      column: temperature
      min_value: -50
      max_value: 60
```

### 5. Streamlit (Visualization)

**Query Pattern**:
```python
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_weather_data():
    query = """
    SELECT * FROM `weather_data.agg_daily_weather`
    WHERE date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
    ORDER BY date DESC
    """
    return client.query(query).to_dataframe()
```

---

## Data Models

### Dimensional Model (Star Schema)

```
           ┌─────────────────┐
           │   dim_cities    │
           │─────────────────│
           │ city_id (PK)    │
           │ city_name       │
           │ country         │
           │ latitude        │
           │ longitude       │
           └────────┬────────┘
                    │
                    │
        ┌───────────┴──────────────┐
        │                          │
┌───────▼─────────┐       ┌────────▼────────┐
│   dim_date      │       │ fact_weather_   │
│─────────────────│       │ observations    │
│ date_id (PK)    │       │─────────────────│
│ full_date       │◄──────│ observation_id  │
│ year            │       │ city_id (FK)    │
│ month           │       │ date_id (FK)    │
│ day             │       │ timestamp       │
│ quarter         │       │ temperature     │
│ is_weekend      │       │ humidity        │
└─────────────────┘       │ pressure        │
                          │ wind_speed      │
                          │ condition       │
                          │ source          │
                          │ quality_score   │
                          └─────────────────┘
```

### Data Lineage

```
raw_openweather ──┐
                  ├──> stg_weather_unified ──> fact_weather_observations ──> agg_daily_weather
raw_openmeteo ────┘                                     │
                                                        │
dim_cities ─────────────────────────────────────────────┤
                                                        │
dim_date ───────────────────────────────────────────────┘
```

---

## Infrastructure

### Docker Compose Architecture

```yaml
services:
  postgres:          # Airflow metadata DB
    - Port: 5432
    - Volume: postgres-db-volume
  
  airflow-webserver: # Airflow UI
    - Port: 8080
    - Depends on: postgres
  
  airflow-scheduler: # DAG scheduler
    - Depends on: postgres
  
  airflow-init:      # One-time setup
    - Creates admin user
```

### Resource Allocation

| Service | CPU | Memory | Disk |
|---------|-----|--------|------|
| airflow-webserver | 1 core | 2GB | - |
| airflow-scheduler | 1 core | 2GB | - |
| postgres | 0.5 core | 1GB | 5GB |

---

## Design Decisions

### Why BigQuery?

✅ **Pros**:
- Serverless (no infrastructure management)
- Scales automatically
- Columnar storage (cost-efficient)
- SQL interface (familiar)
- Integrates with dbt

❌ **Cons**:
- Vendor lock-in
- Query costs (mitigated by partitioning)

**Alternative considered**: PostgreSQL locally (free but limited scalability)

### Why Batch over Streaming?

**Batch (Chosen)**:
- ✅ Simpler architecture
- ✅ Lower cost
- ✅ Weather data changes slowly (6h is sufficient)
- ✅ Easier to debug

**Streaming**:
- ❌ Requires Pub/Sub + Dataflow ($$$)
- ❌ Overkill for weather data
- ❌ Harder to maintain

### Why dbt?

- Industry standard for analytics engineering
- Version-controlled transformations
- Built-in testing framework
- SQL-based (accessible)
- Great documentation generation

### Why Great Expectations?

- Comprehensive validation framework
- Integrates with Airflow
- Generates validation reports
- Catches data quality issues early

---

## Scalability Considerations

### Current Limitations
- Single Airflow instance (LocalExecutor)
- Limited to 5 cities
- No distributed processing

### Scale-Up Path

**To 100+ cities**:
1. Use CeleryExecutor (distributed workers)
2. Implement task parallelization
3. Use partitioned BigQuery loads

**To real-time**:
1. Add Pub/Sub for event streaming
2. Use Dataflow for stream processing
3. Switch to BigQuery streaming inserts

**To multi-region**:
1. Deploy Airflow to Cloud Composer
2. Use multi-region BigQuery
3. Add CDN for dashboard

### Cost at Scale

| Scale | Monthly Cost (Estimated) |
|-------|------------------------|
| 5 cities, 6h batch | $0 (free tier) |
| 50 cities, 1h batch | ~$5 |
| 100 cities, real-time | ~$50-100 |

---

## Security

- Service account with least privilege (BigQuery only)
- API keys in environment variables (not code)
- Credentials volume-mounted (not in image)
- No public exposure of Airflow UI (localhost only)

---

**Next**: See [COST_ESTIMATE.md](COST_ESTIMATE.md) for detailed cost analysis.
