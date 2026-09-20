"""
BharatVerse - Anomaly Service
Loads trained Isolation Forest model and evaluates campus sensor events
to detect abnormal occupancy spikes, ghost sessions, or off-hours resource drain.
"""

import os
import joblib
import numpy as np
from datetime import datetime

MODELS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "ml", "models")
)
ISO_MODEL_PATH = os.path.join(MODELS_DIR, "isolation_forest_anomaly.joblib")

class AnomalyService:
    def __init__(self):
        self.model = None
        self.load_model()

    def load_model(self):
        if os.path.exists(ISO_MODEL_PATH):
            self.model = joblib.load(ISO_MODEL_PATH)

    def evaluate_state(
        self,
        actual_occupancy: int,
        capacity: int,
        hour: int,
        is_weekend: int = 0,
        cost_per_hour: float = 60.0
    ):
        if self.model is None:
            self.load_model()

        occupancy_ratio = actual_occupancy / max(1, capacity)
        features = np.array([[occupancy_ratio, hour, is_weekend, cost_per_hour]])

        is_anomaly = False
        anomaly_score = 0.0

        if self.model is not None:
            pred = self.model.predict(features)[0] # -1 for anomaly, 1 for normal
            is_anomaly = (pred == -1)
            anomaly_score = float(-self.model.score_samples(features)[0])
        else:
            # Rule-based fallback if model not loaded
            if (hour < 6 or hour > 22 or is_weekend) and occupancy_ratio > 0.4:
                is_anomaly = True
            elif occupancy_ratio > 1.05:
                is_anomaly = True

        anomaly_type = "Normal"
        severity = "none"

        if is_anomaly:
            if occupancy_ratio > 1.0:
                anomaly_type = "Overcrowding & Safety Hazard"
                severity = "critical" if occupancy_ratio > 1.25 else "high"
            elif (hour < 7 or hour > 22) and actual_occupancy > 15:
                anomaly_type = "Off-Hours Unauthorized Resource Drain"
                severity = "high"
            elif actual_occupancy == 0 and 9 <= hour <= 16 and not is_weekend:
                anomaly_type = "Ghost Booking (Underutilized Space)"
                severity = "medium"
            else:
                anomaly_type = "Unusual Occupancy Deviation"
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
