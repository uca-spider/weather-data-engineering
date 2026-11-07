# 💰 Cost Estimate & Analysis

Detailed cost breakdown for the Weather Data Engineering Pipeline on Google Cloud Platform.

## Table of Contents
- [Executive Summary](#executive-summary)
- [GCP Free Tier](#gcp-free-tier)
- [Cost Breakdown](#cost-breakdown)
- [Monthly Projections](#monthly-projections)
- [Cost Optimization](#cost-optimization)
- [Monitoring Costs](#monitoring-costs)
- [Scale Scenarios](#scale-scenarios)

---

## Executive Summary

**Current Configuration: $0/month** ✅

This pipeline is designed to operate **completely within GCP free tier** indefinitely.

| Resource | Monthly Usage | Free Tier Limit | Cost |
|----------|--------------|----------------|------|
| BigQuery Storage | ~15 MB | 10 GB | $0 |
| BigQuery Queries | ~100 MB | 1 TB | $0 |
| BigQuery Inserts | Batch (free) | N/A | $0 |
| **TOTAL** | | | **$0** |

---

## GCP Free Tier

### Always Free Tier (No Expiration)

Google Cloud offers permanent free tier for:

**BigQuery:**
- ✅ **Storage**: First 10 GB free
- ✅ **Queries**: First 1 TB processed free per month
- ✅ **Batch Loading**: FREE (no limits)
- ❌ **Streaming Inserts**: $0.01 per 200 MB (we don't use this)

**Other Services (Not Used):**
- Compute Engine: 1 f1-micro instance/month
- Cloud Storage: 5 GB standard storage
- Cloud Functions: 2M invocations/month

### $300 Credit for New Users

New GCP accounts receive:
- $300 free credits
- Valid for 90 days
- No automatic charges after expiration
- Our pipeline stays free even after credits expire

---

## Cost Breakdown

### 1. BigQuery Storage

**Formula**: `$0.02 per GB per month` (after free 10 GB)

**Our Usage**:
```
Data Collection:
- 5 cities
- 2 API sources per city = 10 records per run
- 4 runs per day (every 6 hours)
- 30 days per month

Records per month: 10 × 4 × 30 = 1,200 records

Size per record:
- Raw JSON: ~2 KB
- Total per month: 1,200 × 2 KB = 2.4 MB
- Total per year: 2.4 MB × 12 = ~29 MB

After transformations (dbt tables):
- fact_weather_observations: ~29 MB/year
- dim_cities: < 1 KB (5 rows)
- dim_date: ~50 KB (730 rows for 2 years)
- agg_daily_weather: ~5 MB/year
- agg_weekly_weather: ~1 MB/year

TOTAL STORAGE (1 year): ~35 MB
```

**Cost**: $0 (well under 10 GB free tier)

### 2. BigQuery Query Processing

**Formula**: `$5 per TB processed` (after free 1 TB)

**Our Usage**:

**Airflow Pipeline Queries**:
```
Per run (every 6 hours):
- Load validation query: ~2 MB scanned
- dbt transformations: ~5 MB scanned
- Data quality checks: ~3 MB scanned

Total per run: ~10 MB
Runs per month: 4 × 30 = 120
Monthly pipeline queries: 10 MB × 120 = 1.2 GB
```

**Streamlit Dashboard Queries**:
```
Typical queries:
- Latest weather: SELECT from agg_daily_weather WHERE date >= DATE_SUB(CURRENT_DATE(), 30)
- Scanned: ~5 MB (partitioned table, only 30 days)

Dashboard refreshes: 
- Cache TTL: 5 minutes
- Active users: 1-2 (portfolio demo)
- Queries per day: ~50
- Monthly: 50 × 30 = 1,500 queries × 5 MB = 7.5 GB
```

**Development Queries**:
```
Ad-hoc analysis: ~10 GB/month
Testing during setup: ~5 GB
```

**Total Monthly Queries**: 1.2 GB + 7.5 GB + 10 GB + 5 GB = **~24 GB/month**

**Cost**: $0 (well under 1 TB free tier)

### 3. BigQuery Operations

| Operation | Cost | Our Usage |
|-----------|------|-----------|
| **Batch Loading** | FREE | ✅ Used (load_table_from_json) |
| **Streaming Inserts** | $0.01/200 MB | ❌ Not used |
| **Storage API** | FREE (batch) | ✅ Used |
| **Exports** | FREE | Rarely used |

**Cost**: $0

### 4. Data Transfer

| Transfer Type | Cost | Our Usage |
|---------------|------|-----------|
| Ingress (API → GCP) | FREE | ✅ Weather API calls |
| Egress (GCP → Internet) | $0.12/GB | Minimal (dashboard queries return small results) |
| BigQuery to Streamlit | ~100 KB/query | ~1,500 queries = 150 MB = $0.02 |

**Cost**: ~$0.02/month (negligible, often rounds to $0)

### 5. Infrastructure (Outside GCP)

**Local Docker Infrastructure**:
- Airflow (local machine)
- PostgreSQL metadata DB (local)
- Streamlit (local)

**Cost**: $0 (runs on your laptop/desktop)

**Compute**:
- Estimated power usage: ~50W for 1 hour/day
- Monthly electricity: ~$2-5 (not GCP cost)

---

## Monthly Projections

### Month 1 (Current)
```
Storage: 2.4 MB → $0
Queries: 24 GB → $0
Operations: Batch only → $0
Total: $0
```

### Month 6
```
Storage: 14.4 MB → $0
Queries: 24 GB/month → $0
Total: $0
```

### Month 12
```
Storage: 29 MB → $0
Queries: 24 GB/month → $0
Total: $0
```

### Year 2
```
Storage: 58 MB → $0
Queries: 24 GB/month → $0
Total: $0
```

**Projection: $0 for at least 5+ years at current scale**

### When Costs Start

Storage exceeds 10 GB: After **~17 years** at current ingestion rate

Queries exceed 1 TB: Would need **41x increase** in dashboard usage

---

## Cost Optimization

### Best Practices Implemented

**1. Partitioning**
```sql
-- Tables partitioned by date
CREATE TABLE weather_data.raw_openweather
PARTITION BY DATE(timestamp)
CLUSTER BY city_name;
```
**Benefit**: Query only relevant partitions (reduces scanned data)

**2. Clustering**
```sql
-- Cluster by commonly filtered column
CLUSTER BY city_name
```
**Benefit**: 50-80% reduction in scanned data for city-specific queries

**3. Materialized Views (via dbt)**
```sql
-- Pre-aggregate common queries
-- agg_daily_weather, agg_weekly_weather
```
**Benefit**: Dashboard queries scan aggregated tables (smaller) instead of raw data

**4. Query Caching**
```python
# Streamlit caching
@st.cache_data(ttl=300)  # 5 minutes
```
**Benefit**: Repeated queries return cached results (no BigQuery query cost)

**5. Batch Loading**
```python
# Use batch load, not streaming inserts
client.load_table_from_json(data, table_ref)
```
**Benefit**: Streaming costs $0.01/200MB, batch is free

**6. Expiration Policies (Optional)**
```sql
-- Set table expiration if historical data not needed
ALTER TABLE weather_data.raw_openweather
SET OPTIONS (
  expiration_timestamp=TIMESTAMP_ADD(CURRENT_TIMESTAMP(), INTERVAL 365 DAY)
);
```
**Benefit**: Automatic cleanup (not needed for this portfolio, but good practice)

### Additional Optimizations

**7. Use Table Decorators for Historical Queries**
```sql
-- Free access to data as it was up to 7 days ago
SELECT * FROM `weather_data.raw_openweather`
FOR SYSTEM_TIME AS OF TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR);
```

**8. Set Maximum Bytes Billed**
```sql
-- Prevent accidental large queries
SET @@dataset.project.maxBytesBilled = 100000000;  -- 100 MB limit
```

**9. Use Views for Simple Logic**
```sql
-- Views don't store data (no storage cost)
-- Only pay when queried
CREATE VIEW weather_data.v_latest_weather AS
SELECT * FROM weather_data.fact_weather_observations
WHERE DATE(timestamp) = CURRENT_DATE();
```

**10. Efficient JOIN Patterns**
```sql
-- Put large table first, filter early
SELECT f.*, c.city_name
FROM weather_data.fact_weather_observations f
JOIN weather_data.dim_cities c ON f.city_id = c.city_id
WHERE DATE(f.timestamp) = CURRENT_DATE()  -- Filter before JOIN
```

---

## Monitoring Costs

### Set Up Billing Alerts

```bash
# Via Console
1. Go to: Billing > Budgets & alerts
2. Click "CREATE BUDGET"
3. Set budget: $1/month
4. Alert threshold: 50%, 90%, 100%
5. Add email notification
```

### Query Cost Estimation

**Before Running Queries**:
```python
from google.cloud import bigquery

client = bigquery.Client()

# Dry run to estimate cost
job_config = bigquery.QueryJobConfig(dry_run=True)
query_job = client.query(query, job_config=job_config)

bytes_processed = query_job.total_bytes_processed
estimated_cost = (bytes_processed / 1_000_000_000_000) * 5  # $5 per TB

print(f"Query will process {bytes_processed / 1_000_000:.2f} MB")
print(f"Estimated cost: ${estimated_cost:.4f}")
```

### Monthly Usage Check

```bash
# View current month usage
bq ls --project_id=weather-data-pipeline --format=prettyjson

# Check table sizes
bq show --format=prettyjson weather_data.raw_openweather
```

### Streamlit Dashboard Monitoring

Add cost tracking to dashboard:
```python
import streamlit as st
from google.cloud import bigquery

def get_query_stats():
    """Show this month's query usage"""
    query = """
    SELECT 
      SUM(total_bytes_processed) / 1000000000 as gb_processed,
      COUNT(*) as query_count
    FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
    WHERE creation_time >= TIMESTAMP_TRUNC(CURRENT_TIMESTAMP(), MONTH)
    """
    return client.query(query).to_dataframe()

# Display in sidebar
st.sidebar.metric("Queries This Month (GB)", f"{stats['gb_processed'][0]:.2f} / 1000")
```

---

## Scale Scenarios

### Scenario 1: Add More Cities (50 cities)

**Impact**:
```
Storage: 29 MB → 290 MB/year (still < 10 GB)
Queries: Minimal increase (same query patterns)
Cost: $0 (still within free tier)
```

### Scenario 2: Increase Frequency (Every 1 hour)

**Impact**:
```
Storage: 29 MB → 174 MB/year (still < 10 GB)
Queries: 1.2 GB → 7.2 GB/month (still < 1 TB)
Cost: $0
```

### Scenario 3: Add Historical Backfill (1 year)

**Impact**:
```
One-time backfill:
- 365 days × 4 runs × 10 records = 14,600 records
- Size: ~29 MB
- Query processing: ~100 GB (one-time)
Cost: $0 (still under 1 TB free tier)
```

### Scenario 4: Add More Metrics (10x data per record)

**Impact**:
```
Storage: 29 MB → 290 MB/year
Queries: 24 GB → 240 GB/month
Cost: $0
```

### Scenario 5: Public Dashboard (100 active users)

**Impact**:
```
Dashboard queries: 7.5 GB → 750 GB/month
Total queries: ~800 GB/month
Cost: $0 (still < 1 TB)
```

### Scenario 6: Real-Time Streaming (Switch to Streaming Inserts)

**Impact**:
```
Streaming inserts: 2.4 MB/month → $0.01 (minimum charge)
Real-time queries: Increase 5x → 120 GB/month
Cost: ~$0.01/month (still negligible)
```

### Breaking Point: When Costs Start

**To exceed free tier**:
- **Storage**: Need 10 GB = **345x current rate** or **~17 years**
- **Queries**: Need 1 TB/month = **42x current usage**

**Realistic cost scenarios**:

| Scale | Cities | Frequency | Users | Monthly Cost |
|-------|--------|-----------|-------|--------------|
| **Current** | 5 | 6h | 1-2 | **$0** |
| Small | 20 | 3h | 5 | $0 |
| Medium | 50 | 1h | 20 | $0 |
| Large | 100 | 1h | 50 | $0-2 |
| Enterprise | 500 | 15min | 200 | $5-20 |
| Production | 1000+ | Real-time | 1000+ | $50-500 |

---

## Cost Comparison with Alternatives

| Solution | Monthly Cost | Pros | Cons |
|----------|--------------|------|------|
| **BigQuery (Current)** | **$0** | Serverless, scalable, free tier | Vendor lock-in |
| AWS Redshift | ~$160 | Powerful | Expensive, always-on |
| Snowflake | ~$40 | Great performance | No free tier |
| PostgreSQL (Cloud) | ~$15 | Open source | Manual scaling |
| PostgreSQL (Local) | $0 | Full control | Limited resources |

---

## Best Practices Checklist

- [x] Use batch loading instead of streaming
- [x] Partition large tables by date
- [x] Cluster tables by commonly filtered columns
- [x] Cache dashboard queries
- [x] Use materialized aggregations
- [x] Set billing alerts
- [x] Monitor query costs regularly
- [x] Use dry-run for expensive queries
- [x] Implement table expiration (optional)
- [x] Use views for simple transformations

---

## Conclusion

**This pipeline is designed for zero cost operation.**

Key takeaways:
- ✅ **Current**: $0/month indefinitely
- ✅ **Scalable**: Can 10x scale and stay free
- ✅ **Safe**: Billing alerts prevent surprises
- ✅ **Optimized**: Follows BigQuery best practices
- ✅ **Monitored**: Built-in cost tracking

**For portfolio purposes, this demonstrates:**
1. Cost-conscious engineering
2. Cloud optimization skills
3. Scalable architecture
4. Production-ready patterns

---

**Questions?** See [SETUP.md](SETUP.md) for monitoring setup or [ARCHITECTURE.md](ARCHITECTURE.md) for technical details.
