"""
BharatVerse - Anomaly Service
Loads trained Isolation Forest model and evaluates campus sensor events
Adapted for BharatVerse_Data_Fusion_Dataset features.
"""

import os
import json
import joblib
import numpy as np

MODELS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "ml", "models")
)
ISO_MODEL_PATH = os.path.join(MODELS_DIR, "isolation_forest_anomaly.joblib")
META_PATH = os.path.join(MODELS_DIR, "metadata.json")

class AnomalyService:
    def __init__(self):
        self.model = None
        self.metadata = {}
        self.load_model()

    def load_model(self):
        if os.path.exists(ISO_MODEL_PATH):
            self.model = joblib.load(ISO_MODEL_PATH)
        if os.path.exists(META_PATH):
            with open(META_PATH, "r") as f:
                self.metadata = json.load(f)

    def evaluate_state(
        self,
        actual_occupancy: int,
        capacity: int,
        hour: int,
        is_weekend: int = 0,
        cost_per_hour: float = 60.0,
        power_kw: float = None,
        temperature_c: float = None
    ):
        if self.model is None or not self.metadata:
            self.load_model()

        occupancy_ratio = actual_occupancy / max(1, capacity)
        anomaly_cols = self.metadata.get("anomaly_features", [])

        if "power_kw" in anomaly_cols:
            pwr = power_kw if power_kw is not None else (0.8 + 2.5 * occupancy_ratio)
            temp = temperature_c if temperature_c is not None else (23.5 + 1.8 * occupancy_ratio)
            features = np.array([[
                actual_occupancy,
                pwr,
                temp,
                hour,
                is_weekend,
                capacity,
                occupancy_ratio
            ]])
        else:
            features = np.array([[occupancy_ratio, hour, is_weekend, cost_per_hour]])

        is_anomaly = False
        anomaly_score = 0.0

        if self.model is not None:
            pred = self.model.predict(features)[0] # -1 for anomaly, 1 for normal
            is_anomaly = (pred == -1)
            anomaly_score = float(-self.model.score_samples(features)[0])
        else:
            if (hour < 6 or hour > 22 or is_weekend) and occupancy_ratio > 0.35:
                is_anomaly = True
            elif occupancy_ratio > 1.05:
                is_anomaly = True

        anomaly_type = "Normal"
        severity = "none"

        if is_anomaly:
            if occupancy_ratio > 1.0:
                anomaly_type = "Severe Overcrowding & Safety Violation"
                severity = "critical" if occupancy_ratio > 1.25 else "high"
            elif (hour < 7 or hour > 22) and actual_occupancy > 10:
                anomaly_type = "Off-Hours Unauthorized Resource Drain"
                severity = "high"
            elif actual_occupancy == 0 and 9 <= hour <= 16 and not is_weekend:
                anomaly_type = "Ghost Booking (Underutilized Space)"
                severity = "medium"
            else:
                anomaly_type = "Unusual Occupancy / Power Deviation"
                severity = "medium"

        return {
            "is_anomaly": is_anomaly,
            "anomaly_score": round(anomaly_score, 3),
            "anomaly_type": anomaly_type,
            "severity": severity,
            "observed_value": actual_occupancy,
            "occupancy_ratio": round(occupancy_ratio * 100, 1),
            "expected_range": f"0 - {int(capacity * 0.85)} occupants"
        }

anomaly_service = AnomalyService()
