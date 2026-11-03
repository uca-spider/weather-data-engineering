"""
BigQuery Loader
Load weather data to BigQuery with automatic table creation
"""

import os
from typing import List, Dict
from datetime import datetime
from google.cloud import bigquery
from google.oauth2 import service_account
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BigQueryLoader:
    """Load weather data to BigQuery"""
    
    def __init__(self):
        """Initialize BigQuery client"""
        credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        project_id = os.getenv('GCP_PROJECT_ID')
        dataset_id = os.getenv('GCP_DATASET_ID', 'weather_data')
        
        if not credentials_path or not project_id:
            raise ValueError("GCP credentials not configured")
        
        # Load credentials
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=["https://www.googleapis.com/auth/bigquery"]
        )
        
        self.client = bigquery.Client(
            credentials=credentials,
            project=project_id
        )
        
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.table_id = 'raw_weather_data'
        self.full_table_id = f"{project_id}.{dataset_id}.{self.table_id}"
        
        logger.info(f"BigQuery client initialized: {self.full_table_id}")
    
    def create_table_if_not_exists(self):
        """Create raw weather data table if it doesn't exist"""
        
        schema = [
            bigquery.SchemaField("city", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("country", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("latitude", "FLOAT", mode="REQUIRED"),
            bigquery.SchemaField("longitude", "FLOAT", mode="REQUIRED"),
            bigquery.SchemaField("temperature", "FLOAT", mode="REQUIRED"),
            bigquery.SchemaField("feels_like", "FLOAT", mode="NULLABLE"),
            bigquery.SchemaField("temp_min", "FLOAT", mode="NULLABLE"),
            bigquery.SchemaField("temp_max", "FLOAT", mode="NULLABLE"),
            bigquery.SchemaField("pressure", "INTEGER", mode="NULLABLE"),
            bigquery.SchemaField("humidity", "INTEGER", mode="NULLABLE"),
            bigquery.SchemaField("weather_main", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("weather_description", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("wind_speed", "FLOAT", mode="NULLABLE"),
            bigquery.SchemaField("wind_direction", "FLOAT", mode="NULLABLE"),
            bigquery.SchemaField("cloudiness", "INTEGER", mode="NULLABLE"),
            bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("data_source", "STRING", mode="REQUIRED"),
        ]
        
        table = bigquery.Table(self.full_table_id, schema=schema)
        
        # Partition by date (timestamp field)
        table.time_partitioning = bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY,
            field="timestamp"
        )
        
        try:
            # Try to get table
            self.client.get_table(self.full_table_id)
            logger.info(f"✅ Table already exists: {self.table_id}")
            
        except Exception:
            # Table doesn't exist, create it
            table = self.client.create_table(table)
            logger.info(f"✅ Created table: {self.table_id}")
    
    def load_data(self, data: List[Dict]) -> int:
        """
        Load weather data to BigQuery
        
        Args:
            data: List of weather data dictionaries
            
        Returns:
            Number of rows inserted
        """
        if not data:
            logger.warning("No data to load")
            return 0
        
        # Ensure table exists
        self.create_table_if_not_exists()
        
        # Convert timestamp strings to datetime objects
        for record in data:
            if isinstance(record['timestamp'], datetime):
                record['timestamp'] = record['timestamp'].isoformat()
        
        logger.info(f"Inserting {len(data)} records...")
        
        # Insert data
        errors = self.client.insert_rows_json(self.full_table_id, data)
        
        if errors:
            logger.error(f"❌ Errors inserting rows: {errors}")
            return 0
        else:
            logger.info(f"✅ Successfully inserted {len(data)} records")
            return len(data)
    
    def get_latest_records(self, limit: int = 10) -> List[Dict]:
        """
        Query latest records from BigQuery
        
        Args:
            limit: Number of records to return
            
        Returns:
            List of records
        """
        query = f"""
            SELECT 
                city,
                temperature,
                weather_description,
                timestamp
            FROM `{self.full_table_id}`
            ORDER BY timestamp DESC
            LIMIT {limit}
        """
        
        query_job = self.client.query(query)
        results = query_job.result()
        
        records = []
        for row in results:
            records.append(dict(row))
        
        return records


def load_to_bigquery(weather_data: List[Dict]) -> int:
    """
    Main function to load weather data to BigQuery
    
    Args:
        weather_data: List of weather data dictionaries
        
    Returns:
        Number of rows inserted
    """
    loader = BigQueryLoader()
    return loader.load_data(weather_data)


if __name__ == "__main__":
    # Test the module
    from weather_fetcher import fetch_weather_data
    
    print("Testing BigQuery Loader...")
    print("\n1. Fetching weather data...")
    data = fetch_weather_data()
    
    print(f"\n2. Loading {len(data)} records to BigQuery...")
    rows_inserted = load_to_bigquery(data)
    
    print(f"\n3. Verifying data in BigQuery...")
    loader = BigQueryLoader()
    latest = loader.get_latest_records(5)
    
    print(f"\nLatest {len(latest)} records:")
    for record in latest:
        print(f"  - {record['city']}: {record['temperature']}°C at {record['timestamp']}")
