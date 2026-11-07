# Weather Data Pipeline: OpenWeatherMap to BigQuery

A batch ELT pipeline that collects current weather for five Indonesian cities every 6 hours, loads it into **BigQuery**, models it with **dbt**, and checks its health with an automated **data quality audit**. **Apache Airflow** (Docker Compose) orchestrates everything, and a **Streamlit** dashboard reads the results.

**Status:** runs end to end locally with Docker Compose. It has been running on a 6-hour schedule since 2 November 2026. It is a portfolio project, not a hosted production service.

## Results so far

> Fill in the numbers from your own BigQuery and Airflow after checking them. Delete any line you cannot verify.

| Metric | Value |
|--------|-------|
| Cities covered | 5 (Jakarta, Surabaya, Bandung, Medan, Makassar) |
| Schedule | every 6 hours (`0 */6 * * *`) |
| Rows in `raw_weather_data` | `[FILL: SELECT COUNT(*) ...]` |
| Successful DAG runs / total | `[FILL: from Airflow UI]` |
| dbt tests | 24 passing (last run 7 Nov 2026) |
| Latest data quality score | `[FILL: from data_quality_audit_log]` |

![Airflow DAG graph](docs/images/airflow-dag.png)
![dbt lineage](docs/images/dbt-lineage.png)
![Dashboard](docs/images/dashboard.png)

## Architecture

```
OpenWeatherMap API
        |
        v
Airflow DAG (every 6 hours, 2 retries, 5-minute delay)
  fetch_weather
    -> validate_data            (warns only; does not stop the run)
    -> load_to_bigquery         (append to raw table, partitioned by day)
    -> run_dbt_transformations  (dbt run, then dbt test)
    -> run_data_quality_checks  (audit; critical failure stops the DAG)
    -> log_summary
        |
        v
BigQuery
  weather_data           raw_weather_data
  weather_data_staging   stg_weather_cleaned (view)
  weather_data_marts     dim_cities, dim_dates, fact_weather_observations,
                         agg_daily_weather, data_quality_audit_log
        |
        v
Streamlit dashboard (current conditions, daily trends, quality log)
```

## Tech stack

- Apache Airflow 2.8.1 (LocalExecutor), PostgreSQL 14 for Airflow metadata
- Google BigQuery (region `asia-southeast2`)
- dbt Core with `dbt-bigquery` 1.7.4
- Python, `requests`, `google-cloud-bigquery`
- Streamlit and Plotly for the dashboard
- Docker and Docker Compose

## Data model

| Layer | Model | Notes |
|-------|-------|-------|
| Raw | `raw_weather_data` | Appended on every run; table partitioned by day on `timestamp` |
| Staging | `stg_weather_cleaned` | Casts types, filters null cities and timestamps, builds `observation_id` (MD5 of city and timestamp), and removes duplicates with `QUALIFY ROW_NUMBER()` |
| Marts | `dim_cities`, `dim_dates` | Dimensions with MD5 surrogate keys |
| Marts | `fact_weather_observations` | Partitioned by `observation_date`, clustered by `city_id` and `weather_main` |
| Marts | `agg_daily_weather` | Daily average, min and max temperature, humidity, pressure, wind speed, and dominant weather per city |

dbt tests cover `not_null`, `unique`, and `relationships` on the staging and mart models (24 tests).

## Data quality

Quality is checked in three places:

1. **In the DAG (`validate_data`)**: required fields and plausible ranges for each record. It only logs warnings.
2. **In dbt**: `not_null`, `unique`, and `relationships` tests run after every `dbt run`. A failing test fails the task.
3. **Audit (`WeatherQualityChecker`)**: runs after dbt and writes every result to `weather_data_marts.data_quality_audit_log`.
   - **Freshness**: the latest observation must be within the 7-hour SLA
   - **Completeness**: all five expected cities must be present
   - **Climate range**: temperature 15-45 °C, humidity 20-100%, pressure 900-1100 hPa
   - Each check scores PASS (100), WARN (50) or FAIL (0), and the overall score is the average. A critical failure raises an error and stops the DAG.

## Getting started

### Prerequisites

- Docker and Docker Compose
- An [OpenWeatherMap](https://openweathermap.org/api) API key
- A Google Cloud project with BigQuery enabled and a service account key (JSON)

### Setup

```bash
git clone https://github.com/uca-spider/weather-data-engineering.git
cd weather-data-engineering

cp .env.example .env
# Edit .env: GCP_PROJECT_ID, OPENWEATHER_API_KEY, and the Airflow login

# Put your service account key here (this folder is git-ignored)
mkdir -p credentials
cp /path/to/your-key.json credentials/gcp-credentials.json
```

Create the dbt datasets once, then start Airflow:

```bash
python src/setup_dbt_datasets.py       # creates the staging and marts datasets
docker compose up airflow-init
docker compose up -d
```

Open Airflow at <http://localhost:8080>, log in with the user you set in `.env`, unpause `weather_ingestion_pipeline`, and trigger a run.

### Dashboard

```bash
pip install -r requirements-dashboard.txt
streamlit run src/dashboard/app.py
```

The dashboard has three tabs: current weather by city, daily aggregation trends, and the data quality audit log.

> Never commit `.env` or anything in `credentials/`. Both are listed in `.gitignore`.

## Project structure

```
weather-data-engineering/
├── airflow/dags/
│   └── weather_ingestion_pipeline.py   # Production DAG
├── dbt/weather_dbt/
│   ├── models/staging/                 # stg_weather_cleaned + sources and tests
│   └── models/marts/                   # dim, fact and aggregate models + tests
├── src/
│   ├── ingestion/                      # API fetcher and BigQuery loader
│   ├── validation/                     # WeatherQualityChecker
│   └── dashboard/                      # Streamlit app
├── docs/                               # Architecture, setup, and notes
├── docker-compose.yml
├── Dockerfile                          # Airflow image with dbt installed
├── .env.example
└── requirements.txt
```

## Design decisions and trade-offs

- **Append to raw, deduplicate in dbt.** The loader uses `insert_rows_json` (streaming inserts) and never updates rows. Duplicates are removed in the staging layer. The raw table is a full history, but the loader itself is not idempotent. Re-running a failed task can add duplicate raw rows, which dbt then removes.
- **Partitioning and clustering.** The raw table is partitioned by day, and the fact table is partitioned by date and clustered by city and weather type, to limit the data scanned by dashboard queries.
- **Quality gate after dbt.** The audit reads the marts, so it checks what the dashboard actually shows, and a stale or incomplete load stops the pipeline.
- **6-hour schedule.** Weather changes slowly, and 6 hours keeps API calls and BigQuery usage small.

## Limitations

- Runs locally; there is no cloud deployment or alerting yet
- Single data source (OpenWeatherMap) and five cities
- The loader uses streaming inserts and is not idempotent (see above)
- `validate_data` only warns; the real stopping gate is the audit
- No unit tests for the Python code yet (the dbt tests are the automated checks)
- Great Expectations is not used; quality checks are custom

## Roadmap

- [ ] Unit tests for the fetcher, loader and quality checker (pytest), run in GitHub Actions
- [ ] Make the load idempotent (load jobs or `MERGE` on `observation_id`)
- [ ] Add alerts on audit failure (email or chat webhook)
- [ ] Add a second data source (for example Open-Meteo) and cross-source checks
- [ ] Deploy the dashboard

## Acknowledgements

Weather data from [OpenWeatherMap](https://openweathermap.org/).
