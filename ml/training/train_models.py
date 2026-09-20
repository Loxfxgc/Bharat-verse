"""
BharatVerse - Machine Learning Model Training Pipeline
Trains:
1. XGBoost Regressor for Resource Demand & Room Occupancy Prediction
2. Isolation Forest for Anomaly Detection in Resource Utilization
Trained on: BharatVerse_Data_Fusion_Dataset/processed/fused_ml_room_occupancy.csv
"""

import os
import json
import joblib
from datetime import datetime
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))

# Primary dataset: BharatVerse_Data_Fusion_Dataset
FUSION_DATA_PATH = os.path.join(PROJECT_ROOT, "BharatVerse_Data_Fusion_Dataset", "processed", "fused_ml_room_occupancy.csv")
SYNTHETIC_DATA_PATH = os.path.join(PROJECT_ROOT, "data", "synthetic", "historical_occupancy.csv")
MODELS_DIR = os.path.join(PROJECT_ROOT, "ml", "models")

def get_active_dataset_path():
    if os.path.exists(FUSION_DATA_PATH):
        return FUSION_DATA_PATH, "BharatVerse_Data_Fusion_Dataset"
    elif os.path.exists(SYNTHETIC_DATA_PATH):
        return SYNTHETIC_DATA_PATH, "Synthetic_Campus_Dataset"
    else:
        raise FileNotFoundError(f"Neither {FUSION_DATA_PATH} nor {SYNTHETIC_DATA_PATH} found!")

def train_pipeline():
    os.makedirs(MODELS_DIR, exist_ok=True)
    data_path, dataset_name = get_active_dataset_path()

    print("==================================================================")
    print("  BHARATVERSE ML TRAINING PIPELINE (Phase 4 Implementation)")
    print("==================================================================")
    print(f"Dataset Source: [{dataset_name}]")
    print(f"File Path:      {data_path}")

    df = pd.read_csv(data_path)
    print(f"Total Records:  {len(df):,} rows | {len(df.columns)} columns")

    # Determine schema (Fusion Dataset vs Synthetic Fallback)
    is_fusion = "occupancy_count" in df.columns

    if is_fusion:
        print("\n[Step 1/5] Engineering features from Fused Telemetry Dataset...")
        # Handle lag features
        df_clean = df.copy()
        df_clean["lag_1h"] = df_clean["lag_1h"].bfill().fillna(df_clean["occupancy_count"])
        df_clean["lag_24h"] = df_clean["lag_24h"].fillna(df_clean["expected_occupancy"])
        df_clean["rolling_3h"] = df_clean["rolling_3h"].fillna(df_clean["occupancy_count"])

        feature_cols = [
            "day_of_week",
            "hour",
            "is_weekend",
            "capacity",
            "cost_per_hour",
            "power_kw",
            "temperature_c",
            "lag_1h",
            "lag_24h",
            "rolling_3h",
            "expected_occupancy"
        ]

        target_col = "occupancy_count"
        X = df_clean[feature_cols].copy()
        y = df_clean[target_col].copy()

        # Features for Isolation Forest
        anomaly_feature_cols = [
            "occupancy_count",
            "power_kw",
            "temperature_c",
            "hour",
            "is_weekend",
            "capacity",
            "utilization"
        ]
        X_anomaly = df_clean[anomaly_feature_cols].values
        known_anomalies = int((df_clean["anomaly_label"] == 1).sum()) if "anomaly_label" in df_clean else 0

    else:
        # Fallback schema
        print("\n[Step 1/5] Engineering features from baseline dataset...")
        room_hour_avg = df.groupby(["room_id", "hour"])["actual_occupancy"].mean().rename("hist_avg_occupancy")
        df = df.join(room_hour_avg, on=["room_id", "hour"])

        feature_cols = [
            "day_of_week",
            "hour",
            "is_weekend",
            "exam_period",
            "room_capacity",
            "equipment_count",
            "cost_per_hour",
            "hist_avg_occupancy"
        ]
        target_col = "actual_occupancy"
        X = df[feature_cols].copy()
        y = df[target_col].copy()

        df["occupancy_ratio"] = df["actual_occupancy"] / df["room_capacity"]
        anomaly_feature_cols = ["occupancy_ratio", "hour", "is_weekend", "cost_per_hour"]
        X_anomaly = df[anomaly_feature_cols].values
        known_anomalies = int(df["is_anomaly"].sum()) if "is_anomaly" in df else 0

    # 2. Train / Val / Test Split
    print("\n[Step 2/5] Splitting data (80% Train, 10% Val, 10% Test)...")
    X_train_val, X_test, y_train_val, y_test = train_test_split(X, y, test_size=0.10, random_state=42)
    X_train, X_val, y_train, y_val = train_test_split(X_train_val, y_train_val, test_size=0.1111, random_state=42)

    print(f"  Train: {len(X_train):,} | Validation: {len(X_val):,} | Test: {len(X_test):,}")

    # 3. Train XGBoost Demand Regressor
    print("\n[Step 3/5] Training XGBoost Demand Regressor...")
    model_xgb = xgb.XGBRegressor(
        n_estimators=220,
        max_depth=6,
        learning_rate=0.06,
        subsample=0.85,
        colsample_bytree=0.85,
        random_state=42,
        objective="reg:squarederror"
    )

    model_xgb.fit(
        X_train,
        y_train,
        eval_set=[(X_val, y_val)],
        verbose=False
    )

    # Evaluate on Test Set
    y_pred = model_xgb.predict(X_test)
    y_pred = np.clip(y_pred, 0, None)

    mae = float(mean_absolute_error(y_test, y_pred))
    rmse = float(root_mean_squared_error(y_test, y_pred))
    r2 = float(r2_score(y_test, y_pred))

    print(f"\n--- XGBoost Demand Model Test Set Results ---")
    print(f"  R² Score:                       {r2:.4f} ({r2*100:.2f}% Accuracy)")
    print(f"  Mean Absolute Error (MAE):     {mae:.3f} occupants")
    print(f"  Root Mean Squared Error (RMSE): {rmse:.3f} occupants")

    importances = model_xgb.feature_importances_
    feat_imp = {col: float(imp) for col, imp in sorted(zip(feature_cols, importances), key=lambda x: x[1], reverse=True)}
    print("\nFeature Importances:")
    for col, imp in feat_imp.items():
        print(f"  - {col:<22}: {imp*100:.2f}%")

    # 4. Train Isolation Forest for Anomaly Detection
    print("\n[Step 4/5] Training Isolation Forest on Operational Telemetry...")
    contamination_rate = 0.01 if is_fusion else 0.03
    iso_forest = IsolationForest(
        n_estimators=150,
        contamination=contamination_rate,
        random_state=42
    )
    iso_forest.fit(X_anomaly)
    anom_preds = iso_forest.predict(X_anomaly)
    anomalies_flagged = int((anom_preds == -1).sum())
    print(f"  Flagged {anomalies_flagged} anomalies across {len(X_anomaly):,} operational samples.")
    if known_anomalies > 0:
        print(f"  Known Injected Anomalies in Dataset: {known_anomalies}")

    # 5. Export Models and Metadata
    print("\n[Step 5/5] Exporting model artifacts to ml/models/...")
    xgb_path = os.path.join(MODELS_DIR, "xgboost_demand_model.json")
    iso_path = os.path.join(MODELS_DIR, "isolation_forest_anomaly.joblib")
    meta_path = os.path.join(MODELS_DIR, "metadata.json")

    model_xgb.save_model(xgb_path)
    joblib.dump(iso_forest, iso_path)

    metadata = {
        "model_name": "BharatVerse Campus Resource Intelligence ML",
        "dataset_source": dataset_name,
        "dataset_file": data_path,
        "trained_at": datetime.now().isoformat(),
        "frameworks": {
            "xgboost": xgb.__version__,
            "scikit_learn": "1.9.1"
        },
        "target": target_col,
        "metrics": {
            "mae": round(mae, 3),
            "rmse": round(rmse, 3),
            "r2_score": round(r2, 4),
            "accuracy_pct": round(r2 * 100, 2)
        },
        "feature_cols": feature_cols,
        "feature_importances": feat_imp,
        "anomaly_features": anomaly_feature_cols,
        "anomaly_contamination": contamination_rate,
        "anomalies_flagged": anomalies_flagged,
        "training_samples": len(df)
    }

    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"  Saved XGBoost model:    {xgb_path}")
    print(f"  Saved Isolation Forest: {iso_path}")
    print(f"  Saved Metadata:         {meta_path}")
    print(f"\n✅ Training on {dataset_name} completed with {r2*100:.2f}% accuracy!")
    return metadata

if __name__ == "__main__":
    train_pipeline()
