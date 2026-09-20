"""
BharatVerse - Machine Learning Model Training Pipeline
Trains:
1. XGBoost Regressor for Resource Demand & Room Occupancy Prediction
2. Isolation Forest for Anomaly Detection in Resource Utilization
Saves trained models, feature definitions, and evaluation metrics.
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
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "synthetic", "historical_occupancy.csv")
MODELS_DIR = os.path.join(PROJECT_ROOT, "ml", "models")

def train_pipeline():
    os.makedirs(MODELS_DIR, exist_ok=True)
    print("==================================================================")
    print("  BHARATVERSE ML TRAINING PIPELINE (Phase 4 Implementation)")
    print("==================================================================")
    print(f"Loading historical data from: {DATA_PATH}")

    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Dataset not found at {DATA_PATH}. Run generate_synthetic_data.py first!")

    df = pd.read_csv(DATA_PATH)
    print(f"Dataset shape: {df.shape[0]} rows, {df.shape[1]} columns")

    # 1. Feature Engineering
    print("\n[Step 1/5] Engineering features...")
    # Compute historical average occupancy grouped by room_id and hour
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

    X = df[feature_cols].copy()
    y = df["actual_occupancy"].copy()

    # 2. Train / Val / Test Split
    print("\n[Step 2/5] Splitting data (80% Train, 10% Val, 10% Test)...")
    X_train_val, X_test, y_train_val, y_test = train_test_split(X, y, test_size=0.10, random_state=42)
    X_train, X_val, y_train, y_val = train_test_split(X_train_val, y_train_val, test_size=0.1111, random_state=42)

    print(f"Train size: {len(X_train)} | Val size: {len(X_val)} | Test size: {len(X_test)}")

    # 3. Train XGBoost Regressor
    print("\n[Step 3/5] Training XGBoost Demand Regressor...")
    model_xgb = xgb.XGBRegressor(
        n_estimators=180,
        max_depth=6,
        learning_rate=0.07,
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
    y_pred = np.clip(y_pred, 0, None) # Occupancy cannot be negative

    mae = float(mean_absolute_error(y_test, y_pred))
    rmse = float(root_mean_squared_error(y_test, y_pred))
    r2 = float(r2_score(y_test, y_pred))

    print(f"\n--- XGBoost Demand Model Evaluation on Test Set ---")
    print(f"  Mean Absolute Error (MAE):     {mae:.3f} occupants")
    print(f"  Root Mean Squared Error (RMSE): {rmse:.3f} occupants")
    print(f"  R² Score:                       {r2:.4f} (Accuracy ~ {r2*100:.2f}%)")

    # Feature importances
    importances = model_xgb.feature_importances_
    feat_imp = {col: float(imp) for col, imp in sorted(zip(feature_cols, importances), key=lambda x: x[1], reverse=True)}
    print("\nFeature Importances:")
    for col, imp in feat_imp.items():
        print(f"  - {col:<22}: {imp*100:.2f}%")

    # 4. Train Isolation Forest for Anomaly Detection
    print("\n[Step 4/5] Training Isolation Forest for Anomaly Detection...")
    df["occupancy_ratio"] = df["actual_occupancy"] / df["room_capacity"]
    anomaly_features = ["occupancy_ratio", "hour", "is_weekend", "cost_per_hour"]
    X_anomaly = df[anomaly_features].values

    iso_forest = IsolationForest(
        n_estimators=120,
        contamination=0.03,
        random_state=42
    )
    iso_forest.fit(X_anomaly)

    # 5. Export Models and Metadata
    print("\n[Step 5/5] Exporting model artifacts to ml/models/...")
    xgb_path = os.path.join(MODELS_DIR, "xgboost_demand_model.json")
    iso_path = os.path.join(MODELS_DIR, "isolation_forest_anomaly.joblib")
    meta_path = os.path.join(MODELS_DIR, "metadata.json")

    model_xgb.save_model(xgb_path)
    joblib.dump(iso_forest, iso_path)

    metadata = {
        "model_name": "BharatVerse Campus Resource Intelligence ML",
        "trained_at": datetime.now().isoformat(),
        "frameworks": {
            "xgboost": xgb.__version__,
            "scikit_learn": "1.9.1"
        },
        "target": "actual_occupancy",
        "metrics": {
            "mae": round(mae, 3),
            "rmse": round(rmse, 3),
            "r2_score": round(r2, 4),
            "accuracy_pct": round(r2 * 100, 2)
        },
        "feature_cols": feature_cols,
        "feature_importances": feat_imp,
        "anomaly_features": anomaly_features,
        "anomaly_contamination": 0.03,
        "training_samples": len(df)
    }

    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"Saved XGBoost model to:       {xgb_path}")
    print(f"Saved Isolation Forest to:    {iso_path}")
    print(f"Saved Model Metadata to:      {meta_path}")
    print("\nTraining completed successfully! BharatVerse ML engine is ready.")
    return metadata

if __name__ == "__main__":
    train_pipeline()
