"""
Weather Data Quality & Observability Suite
===========================================
Modul audit mutu data untuk memvalidasi Freshness, Completeness,
dan Deteksi Anomali Iklim Tropis pada data mart BigQuery.
Hasil audit disimpan ke tabel `weather_data_marts.data_quality_audit_log`.
"""

import os
import sys
from datetime import datetime, timezone
from typing import Dict, List, Tuple
from google.cloud import bigquery


class WeatherQualityChecker:
    def __init__(self):
        self.project_id = os.getenv("GCP_PROJECT_ID", "weather-513509")
        self.marts_dataset = "weather_data_marts"
        self.audit_table_id = f"{self.project_id}.{self.marts_dataset}.data_quality_audit_log"
        self.fact_table_id = f"{self.project_id}.{self.marts_dataset}.fact_weather_observations"
        
        self.client = bigquery.Client(project=self.project_id)
        self.expected_cities = {"Jakarta", "Surabaya", "Bandung", "Medan", "Makassar"}
        
        # Inisialisasi tabel log jika belum ada
        self._ensure_audit_table_exists()

    def _ensure_audit_table_exists(self):
        """Membuat tabel data_quality_audit_log jika belum tersedia di BigQuery."""
        schema = [
            bigquery.SchemaField("check_timestamp", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("check_name", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("check_category", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("status", "STRING", mode="REQUIRED"),  # PASS, WARN, FAIL
            bigquery.SchemaField("metric_value", "FLOAT64", mode="NULLABLE"),
            bigquery.SchemaField("threshold", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("message", "STRING", mode="REQUIRED"),
        ]
        
        table = bigquery.Table(self.audit_table_id, schema=schema)
        table.time_partitioning = bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY,
            field="check_timestamp"
        )
        self.client.create_table(table, exists_ok=True)

    def check_freshness(self) -> Dict:
        """Pilar 1: Freshness SLA - Data terbaru tidak boleh lebih tua dari 7 jam."""
        query = f"""
            SELECT 
                TIMESTAMP_DIFF(CURRENT_TIMESTAMP(), MAX(observation_timestamp), MINUTE) AS minutes_since_last
            FROM `{self.fact_table_id}`
        """
        result = list(self.client.query(query).result())[0]
        minutes_ago = result["minutes_since_last"] or 9999
        hours_ago = round(minutes_ago / 60.0, 2)
        
        sla_hours = 7.0
        if hours_ago <= sla_hours:
            status = "PASS"
            msg = f"Data fresh. Observasi terakhir {hours_ago} jam lalu (SLA < {sla_hours}h)."
        elif hours_ago <= 12.0:
            status = "WARN"
            msg = f"Data tertunda: Observasi terakhir {hours_ago} jam lalu."
        else:
            status = "FAIL"
            msg = f"CRITICAL FRESHNESS BREACH: Data sudah {hours_ago} jam tidak terupdate!"

        return {
            "check_name": "freshness_sla",
            "check_category": "freshness",
            "status": status,
            "metric_value": float(hours_ago),
            "threshold": f"<= {sla_hours} hours",
            "message": msg
        }

    def check_completeness(self) -> Dict:
        """Pilar 2: Completeness Rate - Memastikan semua 5 kota ada pada batch data terakhir."""
        query = f"""
            WITH latest_date AS (
                SELECT MAX(observation_date) AS max_date 
                FROM `{self.fact_table_id}`
            )
            SELECT DISTINCT c.city_name
            FROM `{self.fact_table_id}` f
            JOIN `{self.project_id}.{self.marts_dataset}.dim_cities` c ON f.city_id = c.city_id
            WHERE f.observation_date = (SELECT max_date FROM latest_date)
        """
        rows = self.client.query(query).result()
        found_cities = {row["city_name"] for row in rows}
        missing_cities = self.expected_cities - found_cities
        completeness_pct = round((len(found_cities) / len(self.expected_cities)) * 100.0, 2)

        if len(missing_cities) == 0:
            status = "PASS"
            msg = f"Kelengkapan kota 100% ({len(found_cities)}/{len(self.expected_cities)} kota tercakup)."
        elif len(found_cities) >= 3:
            status = "WARN"
            msg = f"Sebagian kota hilang ({completeness_pct}%). Kota tidak ditemukan: {list(missing_cities)}"
        else:
            status = "FAIL"
            msg = f"CRITICAL DATA LOSS: Hanya {len(found_cities)} kota yang ada. Hilang: {list(missing_cities)}"

        return {
            "check_name": "city_completeness_rate",
            "check_category": "completeness",
            "status": status,
            "metric_value": completeness_pct,
            "threshold": "100.0%",
            "message": msg
        }

    def check_climate_anomalies(self) -> Dict:
        """Pilar 3: Anomaly Detection - Cek anomali batas wajar iklim tropis Indonesia."""
        query = f"""
            SELECT 
                COUNTIF(temperature < 15.0 OR temperature > 45.0) AS temp_anomalies,
                COUNTIF(humidity < 20 OR humidity > 100) AS humidity_anomalies,
                COUNTIF(pressure < 900 OR pressure > 1100) AS pressure_anomalies,
                COUNT(*) AS total_rows
            FROM `{self.fact_table_id}`
        """
        row = list(self.client.query(query).result())[0]
        total_anomalies = row["temp_anomalies"] + row["humidity_anomalies"] + row["pressure_anomalies"]
        total_rows = row["total_rows"] or 1
        anomaly_rate = round((total_anomalies / total_rows) * 100.0, 2)

        if total_anomalies == 0:
            status = "PASS"
            msg = "Semua metrik (suhu, kelembapan, tekanan) berada dalam rentang wajar iklim tropis."
        else:
            status = "WARN" if total_anomalies <= 2 else "FAIL"
            msg = (f"Terdeteksi {total_anomalies} anomali (Suhu ekstrem: {row['temp_anomalies']}, "
                   f"Kelembapan ekstrem: {row['humidity_anomalies']}, Tekanan ekstrem: {row['pressure_anomalies']}).")

        return {
            "check_name": "tropical_climate_range",
            "check_category": "anomaly_detection",
            "status": status,
            "metric_value": float(total_anomalies),
            "threshold": "0 anomalies (Temp: 15-45C, Hum: 20-100%, Press: 900-1100hPa)",
            "message": msg
        }

    def run_all_checks(self) -> Tuple[float, List[Dict]]:
        """Menjalankan seluruh rangkaian tes dan menghitung skor mutu data kumulatif."""
        print("=" * 60)
        print("🔍 RUNNING DATA QUALITY & OBSERVABILITY SUITE")
        print("=" * 60)

        checks = [
            self.check_freshness(),
            self.check_completeness(),
            self.check_climate_anomalies(),
        ]

        # Hitung skor mutu data (PASS = 1.0, WARN = 0.5, FAIL = 0.0)
        score_map = {"PASS": 100.0, "WARN": 50.0, "FAIL": 0.0}
        total_score = sum(score_map[c["status"]] for c in checks) / len(checks)
        overall_score = round(total_score, 1)

        now = datetime.now(timezone.utc)
        records_to_insert = []
        has_failure = False

        for c in checks:
            icon = "✅" if c["status"] == "PASS" else ("⚠️" if c["status"] == "WARN" else "❌")
            print(f"{icon} [{c['status']}] {c['check_name']}: {c['message']}")
            
            records_to_insert.append({
                "check_timestamp": now.isoformat(),
                "check_name": c["check_name"],
                "check_category": c["check_category"],
                "status": c["status"],
                "metric_value": c["metric_value"],
                "threshold": c["threshold"],
                "message": c["message"],
            })
            if c["status"] == "FAIL":
                has_failure = True

        print("-" * 60)
        print(f"📊 OVERALL DATA QUALITY SCORE: {overall_score}/100")
        print("=" * 60)

        # Simpan hasil audit ke BigQuery
        errors = self.client.insert_rows_json(self.audit_table_id, records_to_insert)
        if errors:
            print(f"⚠️ Warning: Gagal menyimpan log audit ke BigQuery: {errors}")
        else:
            print("💾 Hasil audit mutu data berhasil disimpan ke BigQuery.")

        return overall_score, checks, has_failure


def main():
    checker = WeatherQualityChecker()
    score, checks, has_failure = checker.run_all_checks()

    # Gagalkan eksekusi jika ada tes fatal (FAIL)
    if has_failure:
        print("\n❌ CRITICAL: Data quality check failed! Pipeline dihentikan.")
        sys.exit(1)
    else:
        print("\n🎉 Data quality check passed successfully!")
        sys.exit(0)


if __name__ == "__main__":
    main()
