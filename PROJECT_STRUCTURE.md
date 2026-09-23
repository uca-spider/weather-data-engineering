# Weather Data Engineering Pipeline

Project structure for end-to-end weather data pipeline.

## Rename Directory First

If your folder is still named `data-engineer`, please rename it:

```bash
cd /c/Portofolio
mv data-engineer weather-data-engineering
cd weather-data-engineering
```

## Directory Structure

```
weather-data-engineering/
├── README.md                      # Main documentation
├── SPRINT_PLANNING.md             # Sprint tracker
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment template
├── .gitignore                     # Git exclusions
├── docker-compose.yml             # Infrastructure (Sprint 1)
│
├── docs/                          # Documentation
│   ├── SETUP.md
│   ├── ARCHITECTURE.md
│   ├── COST_ESTIMATE.md
│   └── API_DOCS.md
│
├── airflow/                       # Airflow orchestration
│   ├── dags/                      # DAG definitions (Sprint 2)
│   ├── plugins/                   # Custom operators
│   ├── logs/                      # Airflow logs (gitignored)
│   └── config/                    # Airflow configuration
│
├── dbt/                           # dbt transformations (Sprint 3)
│   ├── models/
│   ├── macros/
│   └── tests/
│
├── great_expectations/            # Data quality (Sprint 4)
│   ├── expectations/
│   └── checkpoints/
│
├── src/                           # Source code
│   ├── ingestion/                 # Data ingestion (Sprint 2)
│   ├── validation/                # Data validation (Sprint 4)
│   ├── dashboard/                 # Streamlit app (Sprint 5)
│   └── utils/                     # Shared utilities
│
├── tests/                         # Test suite (Sprint 6)
│   ├── test_ingestion.py
│   └── test_validation.py
│
└── credentials/                   # GCP credentials (gitignored)
    └── .gitkeep
```

## Sprint Progress

**Current Sprint**: Sprint 0 - Setup & Documentation  
**Status**: Near completion

See [SPRINT_PLANNING.md](SPRINT_PLANNING.md) for detailed task breakdown.
