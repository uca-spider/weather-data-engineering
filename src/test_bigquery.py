"""
BigQuery Connection Test Script
Purpose: Test service account credentials and BigQuery access
"""

import os
from google.cloud import bigquery
from google.oauth2 import service_account
from datetime import datetime


def test_bigquery_connection():
    """Test BigQuery connection with service account"""
    
    print("=" * 60)
    print("☁️  BigQuery Connection Test")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Get credentials path
    credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    project_id = os.getenv('GCP_PROJECT_ID')
    dataset_id = os.getenv('GCP_DATASET_ID', 'weather_data')
    
    print(f"Project ID: {project_id}")
    print(f"Dataset ID: {dataset_id}")
    print(f"Credentials: {credentials_path}")
    print()
    
    # Check if credentials file exists
    if not credentials_path or not os.path.exists(credentials_path):
        print("❌ ERROR: Credentials file not found!")
        print(f"Expected at: {credentials_path}")
        return False
    
    print("✅ Credentials file found")
    print()
    
    try:
        # Load credentials
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=["https://www.googleapis.com/auth/bigquery"]
        )
        
        # Create BigQuery client
        client = bigquery.Client(
            credentials=credentials,
            project=project_id
        )
        
        print("Testing BigQuery access...")
        print()
        
        # Test 1: List datasets
        print("Test 1: List datasets")
        datasets = list(client.list_datasets())
        
        if datasets:
            print(f"✅ Found {len(datasets)} dataset(s):")
            for dataset in datasets:
                print(f"   - {dataset.dataset_id}")
        else:
            print("⚠️  No datasets found (create 'weather_data' dataset)")
        print()
        
        # Test 2: Access specific dataset
        print("Test 2: Access weather_data dataset")
        dataset_ref = f"{project_id}.{dataset_id}"
        
        try:
            dataset = client.get_dataset(dataset_ref)
            print(f"✅ Dataset '{dataset_id}' accessible")
            print(f"   Location: {dataset.location}")
            print(f"   Created: {dataset.created}")
            print()
            
            # Test 3: List tables
            print("Test 3: List tables in dataset")
            tables = list(client.list_tables(dataset))
            
            if tables:
                print(f"✅ Found {len(tables)} table(s):")
                for table in tables:
                    print(f"   - {table.table_id}")
            else:
                print("ℹ️  No tables yet (will be created by pipeline)")
            print()
            
        except Exception as e:
            print(f"❌ Cannot access dataset '{dataset_id}'")
            print(f"Error: {str(e)}")
            print()
            print("Make sure you created the dataset in BigQuery Console!")
            return False
        
        # Test 4: Test query (simple)
        print("Test 4: Test query execution")
        query = "SELECT 1 as test_value"
        
        query_job = client.query(query)
        results = query_job.result()
        
        for row in results:
            print(f"✅ Query successful! Result: {row.test_value}")
        print()
        
        print("=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("BigQuery connection is working correctly!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print("=" * 60)
        print(f"❌ ERROR: {type(e).__name__}")
        print(f"Message: {str(e)}")
        print("=" * 60)
        return False


if __name__ == "__main__":
    success = test_bigquery_connection()
    exit(0 if success else 1)
