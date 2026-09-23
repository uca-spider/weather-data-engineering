# 🌦️ Weather Data Engineering Pipeline

**End-to-End Data Engineering Portfolio Project**

Modern data pipeline showcasing real-world data engineering practices with cloud-native architecture, automated orchestration, data quality validation, and analytics dashboard.

## 📊 Project Overview

This project demonstrates a production-ready weather data pipeline that:
- Ingests data from multiple weather APIs
- Processes and validates data quality
- Stores in cloud data warehouse (BigQuery)
- Transforms data using modern analytics engineering (dbt)
- Validates data quality (Great Expectations)
- Visualizes insights through interactive dashboard (Streamlit)
- Orchestrates everything with Apache Airflow

### 🎯 Key Features

- ✅ **Multi-source ingestion** - OpenWeatherMap + Open-Meteo APIs
- ✅ **Cloud data warehouse** - Google BigQuery
- ✅ **Modern transformation** - dbt Core with tests
- ✅ **Data quality** - Great Expectations framework
- ✅ **Orchestration** - Apache Airflow with Docker
- ✅ **Batch processing** - Scheduled every 6 hours
- ✅ **Cost-optimized** - Stays within GCP free tier
- ✅ **Production patterns** - Idempotent, monitored, tested

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     DATA SOURCES                            │
├─────────────────────────────────────────────────────────────┤
│  OpenWeatherMap API  │  Open-Meteo API                      │
└──────────────┬──────────────────┬───────────────────────────┘
               │                  │
               v                  v
┌─────────────────────────────────────────────────────────────┐
│              ORCHESTRATION LAYER                            │
│         Apache Airflow (Docker Compose)                     │
│                                                             │
│  ┌──────────────────────────────────────────────────┐     │
│  │  DAG: weather_ingestion_pipeline                 │     │
│  │  Schedule: Every 6 hours (0 */6 * * *)          │     │
│  │                                                   │     │
│  │  Tasks:                                          │     │
│  │  1. fetch_openweather → validate_raw_data       │     │
│  │  2. fetch_openmeteo → validate_raw_data         │     │
│  │  3. validate_raw_data → load_to_bigquery        │     │
│  │  4. load_to_bigquery → run_dbt_transformations  │     │
│  │  5. run_dbt_transformations → data_quality_check│     │
│  │  6. data_quality_check → notify_completion      │     │
│  └──────────────────────────────────────────────────┘     │
└──────────────┬──────────────────────────────────────────────┘
               │
               v
┌─────────────────────────────────────────────────────────────┐
│                  DATA WAREHOUSE LAYER                       │
│                    Google BigQuery                          │
│                                                             │
│  Dataset: weather_data                                      │
│                                                             │
│  ┌─────────────────────────────────────────────┐          │
│  │  RAW LAYER (Staging)                        │          │
│  │  • raw_openweather (partitioned by date)    │          │
│  │  • raw_openmeteo (partitioned by date)      │          │
│  └─────────────────────────────────────────────┘          │
│                      │                                      │
│                      │ dbt transformations                  │
│                      v                                      │
│  ┌─────────────────────────────────────────────┐          │
│  │  TRANSFORMED LAYER                          │          │
│  │  • stg_weather_unified (standardized)       │          │
│  │  • dim_cities (dimension table)             │          │
│  │  • dim_date (dimension table)               │          │
│  │  • fact_weather_observations (fact table)   │          │
│  │  • agg_daily_weather (aggregations)         │          │
│  │  • agg_weekly_weather (aggregations)        │          │
│  └─────────────────────────────────────────────┘          │
└──────────────┬──────────────────────────────────────────────┘
               │
               v
┌─────────────────────────────────────────────────────────────┐
│                  VISUALIZATION LAYER                        │
│                   Streamlit Dashboard                       │
│                                                             │
│  • Real-time weather metrics                               │
│  • Temperature trends across cities                        │
│  • Weather patterns analysis                               │
│  • Data quality metrics                                    │
│  • Pipeline monitoring stats                               │
└─────────────────────────────────────────────────────────────┘
```

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Orchestration** | Apache Airflow 2.8+ | Workflow scheduling & monitoring |
| **Data Warehouse** | Google BigQuery | Cloud-native data storage |
| **Transformation** | dbt Core 1.7+ | Analytics engineering & testing |
| **Data Quality** | Great Expectations 0.18+ | Data validation framework |
| **Programming** | Python 3.11+ | Pipeline logic |
| **Visualization** | Streamlit 1.30+ | Interactive dashboard |
| **Containerization** | Docker & Docker Compose | Infrastructure as code |
| **Version Control** | Git & GitHub | Code versioning |

## 📍 Coverage

**Indonesian Cities (5):**
- Jakarta (Capital, Java)
- Surabaya (East Java)
- Bandung (West Java)
- Medan (Sumatra)
- Makassar (Sulawesi)

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose installed
- Python 3.11+
- Google Cloud Platform account (free tier)
- API keys (free):
  - OpenWeatherMap API key
  - Open-Meteo (no key required)

### Installation

```bash
# Clone repository
git clone <repository-url>
cd data-engineer

# Setup GCP credentials
# Follow SETUP.md for detailed instructions

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Start infrastructure
docker-compose up -d

# Access Airflow UI
open http://localhost:8080
# Default: airflow / airflow

# Access Streamlit Dashboard
streamlit run src/dashboard/app.py
```

For detailed setup instructions, see [SETUP.md](SETUP.md)

## 📂 Project Structure

```
data-engineer/
├── airflow/                    # Airflow configuration
│   ├── dags/                   # DAG definitions
│   │   ├── weather_pipeline.py
│   │   └── utils/
│   ├── plugins/                # Custom operators
│   └── config/                 # Airflow configs
│
├── dbt/                        # dbt project
│   ├── models/                 # SQL transformations
│   │   ├── staging/            # Staging models
│   │   ├── marts/              # Business logic layer
│   │   └── schema.yml          # Tests & documentation
│   ├── macros/                 # Reusable SQL functions
│   ├── tests/                  # Custom tests
│   └── dbt_project.yml
│
├── great_expectations/         # Data quality
│   ├── expectations/           # Validation rules
│   ├── checkpoints/            # Validation checkpoints
│   └── great_expectations.yml
│
├── src/                        # Source code
│   ├── ingestion/              # Data ingestion logic
│   │   ├── openweather.py
│   │   └── openmeteo.py
│   ├── validation/             # Data validation
│   ├── dashboard/              # Streamlit app
│   └── utils/                  # Shared utilities
│
├── tests/                      # Unit tests
│   ├── test_ingestion.py
│   └── test_transformations.py
│
├── docs/                       # Documentation
│   ├── ARCHITECTURE.md         # Architecture details
│   ├── SETUP.md                # Setup guide
│   ├── COST_ESTIMATE.md        # Cost analysis
│   └── API_DOCS.md             # API documentation
│
├── docker-compose.yml          # Infrastructure definition
├── Dockerfile                  # Custom images
├── requirements.txt            # Python dependencies
├── .env.example                # Environment template
└── README.md                   # This file
```

## 📈 Pipeline Schedule

- **Frequency**: Every 6 hours
- **Schedule**: `0 */6 * * *` (00:00, 06:00, 12:00, 18:00 UTC)
- **Runtime**: ~5-10 minutes per run
- **Data volume**: ~600 records/month

## 💰 Cost Analysis

This project is designed to stay within **GCP free tier**:

| Resource | Monthly Usage | Cost |
|----------|--------------|------|
| BigQuery Storage | ~15MB | $0 (< 10GB free) |
| BigQuery Queries | ~100MB | $0 (< 1TB free) |
| **Total** | | **$0/month** |

See [COST_ESTIMATE.md](docs/COST_ESTIMATE.md) for detailed breakdown.

## 🧪 Data Quality Checks

Great Expectations validations:
- ✅ Schema validation (expected columns, types)
- ✅ Null checks (mandatory fields)
- ✅ Range validation (temperature, humidity ranges)
- ✅ Freshness checks (data recency)
- ✅ Uniqueness constraints
- ✅ Cross-source consistency

## 📊 Dashboard Features

Streamlit dashboard provides:
- Current weather conditions for all cities
- Temperature trends (7-day, 30-day)
- Weather patterns comparison
- Data pipeline health metrics
- Data quality score
- API performance monitoring

## 🔍 Monitoring

- Airflow UI for pipeline monitoring
- BigQuery audit logs
- Great Expectations validation reports
- Streamlit metrics dashboard

## 🧪 Testing

```bash
# Run unit tests
pytest tests/

# Run dbt tests
cd dbt && dbt test

# Run data quality validations
great_expectations checkpoint run weather_checkpoint
```

## 📚 Documentation

- [Architecture Documentation](docs/ARCHITECTURE.md)
- [Setup Guide](docs/SETUP.md)
- [Cost Estimate](docs/COST_ESTIMATE.md)
- [API Documentation](docs/API_DOCS.md)

## 🎓 Learning Outcomes

This project demonstrates:
1. **Data Engineering Fundamentals** - ETL/ELT patterns
2. **Cloud Data Warehousing** - BigQuery best practices
3. **Modern Data Stack** - Airflow + dbt + Great Expectations
4. **Data Quality** - Validation frameworks
5. **Analytics Engineering** - Dimensional modeling
6. **DevOps** - Containerization, IaC
7. **Cost Optimization** - Free tier architecture
8. **Production Patterns** - Idempotency, monitoring, testing

## 🚧 Future Enhancements

- [ ] Add CI/CD pipeline (GitHub Actions)
- [ ] Implement data lineage tracking
- [ ] Add alerting (email/Slack notifications)
- [ ] Create data catalog documentation
- [ ] Add more cities and countries
- [ ] Implement incremental loading strategies
- [ ] Add machine learning predictions
- [ ] Deploy to cloud (Cloud Composer)

## 📝 License

MIT License - See LICENSE file for details

## 👤 Author

Portfolio project for demonstrating data engineering skills.

**Technologies showcased**: Apache Airflow • BigQuery • dbt • Great Expectations • Python • Docker • Streamlit

---

**⭐ If this project helps your learning, please star it!**
