"""
BharatVerse - New Resource Analyzer & Training Pipeline
1. Validates and profiles newly entered campus resources (rooms, labs, halls).
2. Computes capability match, capacity category, and anomaly thresholds.
3. Ingests or generates baseline telemetry for the new resource into BharatVerse_Data_Fusion_Dataset.
4. Updates the dataset and triggers model retraining.
5. Produces an instant 24-hour demand forecast for the new resource.
"""

import os
import sys
import json
import random
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ml.training.train_models import train_pipeline
from backend.app.database.connection import SessionLocal
from backend.app.database.db_models import ResourceModel
from backend.app.services.prediction_service import prediction_service

FUSION_DATA_PATH = os.path.join(PROJECT_ROOT, "BharatVerse_Data_Fusion_Dataset", "processed", "fused_ml_room_occupancy.csv")
SYNTHETIC_DATA_PATH = os.path.join(PROJECT_ROOT, "data", "synthetic", "historical_occupancy.csv")

def get_target_data_path():
    if os.path.exists(FUSION_DATA_PATH):
        return FUSION_DATA_PATH
    return SYNTHETIC_DATA_PATH

def analyze_and_ingest_resource(resource_dict: dict, days_of_history: int = 30, retrain_now: bool = True):
    """
    Analyzes a newly entered resource, ingests it into dataset & DB, and retrains the models.
    """
    target_data_path = get_target_data_path()
    print("==================================================================")
    print("  BHARATVERSE RESOURCE INGESTION & ANALYSIS PIPELINE")
    print("==================================================================")
    print(f"Target Dataset: {target_data_path}")

    # 1. Validation
    res_id = resource_dict.get("resource_id")
    name = resource_dict.get("name", res_id)
    capacity = int(resource_dict.get("capacity", 50))
    capabilities = resource_dict.get("capabilities", ["projector"])
    cost_per_hour = float(resource_dict.get("cost_per_hour", 60.0))
    res_type = resource_dict.get("type", "room")
    building_id = resource_dict.get("building_id", "BLD_A")
    location = resource_dict.get("location", "Academic Block")

    if not res_id:
        raise ValueError("resource_id is required")
    if capacity <= 0:
        raise ValueError(f"Invalid capacity: {capacity}. Must be positive.")

    # 2. Resource Intelligence Profiling
    print(f"\n[Step 1/4] Analyzing Profile for: {name} ({res_id})")
    
    if capacity < 50:
        cap_category = "Small Discussion Room / Specialized Lab"
    elif capacity < 100:
        cap_category = "Standard Lecture Classroom"
    elif capacity < 200:
        cap_category = "Large Tiered Lecture Hall"
    else:
        cap_category = "Campus Auditorium / Mega Space"

    common_demands = ["projector", "computer", "audio", "gpu_cluster", "smartboard", "sensors"]
    matched_demands = [c for c in capabilities if c in common_demands]
    versatility_score = round((len(matched_demands) / len(common_demands)) * 100, 1)

    safe_max_occupancy = int(capacity * 1.0)
    overcrowding_threshold = int(capacity * 1.15)
    off_hours_alert_threshold = max(5, int(capacity * 0.15))

    analysis_report = {
        "resource_id": res_id,
        "name": name,
        "type": res_type,
        "capacity": capacity,
        "capacity_category": cap_category,
        "capabilities": capabilities,
        "versatility_score": f"{versatility_score}%",
        "hourly_cost": f"₹{cost_per_hour}",
        "operational_thresholds": {
            "normal_safe_max": safe_max_occupancy,
            "overcrowding_alert_level": overcrowding_threshold,
            "off_hours_threshold": off_hours_alert_threshold
        }
    }

    print(f"  • Category:          {cap_category}")
    print(f"  • Versatility Score: {versatility_score}% (Capabilities: {', '.join(capabilities)})")
    print(f"  • Cost per Hour:     ₹{cost_per_hour}")
    print(f"  • Anomaly Limit:     > {overcrowding_threshold} occupants triggers High Severity Alert")

    # 3. Ingest into Database
    print(f"\n[Step 2/4] Registering resource into Database...")
    db = SessionLocal()
    try:
        existing = db.query(ResourceModel).filter(ResourceModel.resource_id == res_id).first()
        if existing:
            print(f"  Updating existing record for {res_id}")
            existing.name = name
            existing.capacity = capacity
            existing.capabilities = capabilities
            existing.cost_per_hour = cost_per_hour
            existing.location = location
            existing.type = res_type
            existing.building_id = building_id
        else:
            print(f"  Inserting new resource {res_id}")
            new_r = ResourceModel(
                resource_id=res_id,
                name=name,
                type=res_type,
                capacity=capacity,
                building_id=building_id,
                location=location,
                capabilities=capabilities,
                cost_per_hour=cost_per_hour,
                status="available",
                current_occupancy=0
            )
            db.add(new_r)
        db.commit()
    finally:
        db.close()

    # 4. Generate & Ingest Telemetry History into CSV
    print(f"\n[Step 3/4] Generating {days_of_history} days of baseline telemetry for training...")
    df_existing = pd.read_csv(target_data_path) if os.path.exists(target_data_path) else pd.DataFrame()

    # Remove previous records for this room if updating
    if not df_existing.empty and "room_id" in df_existing.columns:
        df_existing = df_existing[df_existing["room_id"] != res_id]

    base_date = datetime.now() - timedelta(days=days_of_history)
    new_records = []
    is_fusion = "power_kw" in df_existing.columns

    for day in range(days_of_history):
        current_date = base_date + timedelta(days=day)
        day_of_week = current_date.weekday()
        is_weekend = 1 if day_of_week >= 5 else 0

        for hour in range(24):
            if is_weekend:
                expected_occ = int(capacity * random.uniform(0.0, 0.10))
            elif 9 <= hour <= 17:
                expected_occ = int(capacity * random.uniform(0.50, 0.90))
            elif 18 <= hour <= 21:
                expected_occ = int(capacity * random.uniform(0.15, 0.35))
            else:
                expected_occ = 0

            utilization = round((expected_occ / capacity) * 100.0, 2)
            timestamp_str = (current_date + timedelta(hours=hour)).strftime("%Y-%m-%d %H:%M:%S")

            if is_fusion:
                pwr = round(0.6 + 2.8 * (expected_occ / max(1, capacity)) + random.uniform(-0.1, 0.1), 2)
                temp = round(23.0 + 2.0 * (expected_occ / max(1, capacity)) + random.uniform(-0.3, 0.3), 2)
                new_records.append({
                    "sensor_id": f"SENS_{res_id}",
                    "timestamp": timestamp_str,
                    "room_id": res_id,
                    "occupancy_count": expected_occ,
                    "power_kw": pwr,
                    "temperature_c": temp,
                    "source_system": "IoT+ERP",
                    "day_of_week": day_of_week,
                    "hour": hour,
                    "is_weekend": is_weekend,
                    "lag_1h": expected_occ,
                    "lag_24h": expected_occ,
                    "rolling_3h": expected_occ,
                    "capacity": capacity,
                    "cost_per_hour": cost_per_hour,
                    "utilization": round(expected_occ / max(1, capacity), 3),
                    "expected_occupancy": float(expected_occ),
                    "anomaly_label": 0,
                    "data_source": "IoT+ERP",
                    "fusion_key": f"ROOM:{res_id}|{current_date.strftime('%Y%m%d')}{hour:02d}",
                    "record_quality": 1.0
                })
            else:
                new_records.append({
                    "timestamp": timestamp_str,
                    "room_id": res_id,
                    "day_of_week": day_of_week,
                    "hour": hour,
                    "is_weekend": is_weekend,
                    "exam_period": 0,
                    "room_capacity": capacity,
                    "equipment_count": len(capabilities),
                    "cost_per_hour": cost_per_hour,
                    "actual_occupancy": expected_occ,
                    "utilization_ratio": utilization,
                    "is_anomaly": 0
                })

    df_new = pd.DataFrame(new_records)
    df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    df_combined.to_csv(target_data_path, index=False)
    print(f"  Added {len(new_records)} sensor readings to {target_data_path} (Total: {len(df_combined):,} records).")

    # 5. Retrain Models
    training_metrics = {}
    if retrain_now:
        print("\n[Step 4/4] Retraining XGBoost & Isolation Forest on updated campus dataset...")
        training_metrics = train_pipeline()
    else:
        print("\n[Step 4/4] Model retraining skipped (retrain_now=False).")

    # 6. Generate 24-Hour Forecast for the new resource
    prediction_service.load_model()
    forecast_preview = prediction_service.get_24h_forecast(room_capacity=capacity, day_of_week=0)

    result = {
        "analysis": analysis_report,
        "new_samples_added": len(new_records),
        "total_dataset_samples": len(df_combined),
        "retrained": retrain_now,
        "model_metrics": training_metrics.get("metrics", {}),
        "forecast_sample_24h": forecast_preview[:6]
    }

    print("\n✅ New Resource Analysis and Model Retraining Completed Successfully!")
    return result

if __name__ == "__main__":
    sample_new_resource = {
        "resource_id": "ROOM_QUANTUM_COMP",
        "name": "Quantum Computing & Supercomputing Cluster",
        "type": "laboratory",
        "capacity": 65,
        "building_id": "B03",
        "location": "Science & Labs - Level 4",
        "capabilities": ["gpu_cluster", "computer", "smartboard", "high_speed_net"],
        "cost_per_hour": 160.0
    }
    res = analyze_and_ingest_resource(sample_new_resource, days_of_history=25, retrain_now=True)
    print("\nResult Summary:")
    print(json.dumps(res, indent=2))
