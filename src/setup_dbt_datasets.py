"""
Setup BigQuery Datasets for dbt
================================
Membuat dataset staging dan marts di region yang sama dengan raw dataset.
"""

import os
import sys
from google.cloud import bigquery
from google.cloud.exceptions import Conflict


def create_datasets():
    project_id = os.getenv("GCP_PROJECT_ID", "weather-513509")
    region = os.getenv("GCP_REGION", "asia-southeast2")

    print("=" * 60)
    print("🚀 Initializing BigQuery Datasets for dbt")
    print(f"Project ID : {project_id}")
    print(f"Region     : {region}")
    print("=" * 60)

    client = bigquery.Client(project=project_id)

    target_datasets = [
        {
            "id": "weather_data_staging",
            "description": "dbt Staging layer: cleaned, typed, and deduplicated raw weather data",
        },
        {
            "id": "weather_data_marts",
            "description": "dbt Marts layer: star schema dimensions, facts, and daily aggregations",
        },
    ]

    for item in target_datasets:
        dataset_ref = f"{project_id}.{item['id']}"
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = region
        dataset.description = item["description"]

        try:
            client.create_dataset(dataset, exists_ok=True)
            print(f"✅ Dataset ready: {dataset_ref} (location: {region})")
        except Conflict:
            print(f"ℹ️  Dataset already exists: {dataset_ref}")
        except Exception as e:
            print(f"❌ Failed to create {dataset_ref}: {e}")
            sys.exit(1)

    print("\n🎉 All required BigQuery datasets are ready!")


if __name__ == "__main__":
    create_datasets()
