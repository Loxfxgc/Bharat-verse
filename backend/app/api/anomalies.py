"""
BharatVerse - Anomalies API
Detection and listing of campus resource anomalies
"""

from typing import List
from datetime import datetime
import uuid
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database.connection import get_db
from ..database.db_models import AnomalyModel, ResourceModel
from ..schemas.schemas import AnomalyResponse
from ..services.anomaly_service import anomaly_service

router = APIRouter(prefix="/api/anomalies", tags=["Anomalies"])

class AnomalyDetectRequest(BaseModel):
    resource_id: str = "ROOM_R101"
    actual_occupancy: int = 98
    hour: int = 14
    is_weekend: int = 0

@router.get("", response_model=List[AnomalyResponse])
def get_anomalies(db: Session = Depends(get_db)):
    return db.query(AnomalyModel).order_by(AnomalyModel.timestamp.desc()).all()

@router.post("/detect", response_model=AnomalyResponse)
def detect_anomaly(payload: AnomalyDetectRequest, db: Session = Depends(get_db)):
    room = db.query(ResourceModel).filter(ResourceModel.resource_id == payload.resource_id).first()
    cap = room.capacity if room else 60
    cost = room.cost_per_hour if room else 50.0

    eval_res = anomaly_service.evaluate_state(
        actual_occupancy=payload.actual_occupancy,
        capacity=cap,
        hour=payload.hour,
        is_weekend=payload.is_weekend,
        cost_per_hour=cost
    )

    anomaly = AnomalyModel(
        anomaly_id=f"ANM_{uuid.uuid4().hex[:8].upper()}",
        resource_id=payload.resource_id,
        timestamp=datetime.utcnow(),
        observed_value=float(payload.actual_occupancy),
        expected_range=eval_res["expected_range"],
        anomaly_type=eval_res["anomaly_type"],
        severity=eval_res["severity"] if eval_res["is_anomaly"] else "none",
        status="active" if eval_res["is_anomaly"] else "normal"
    )
    if eval_res["is_anomaly"]:
        db.add(anomaly)
        db.commit()
        db.refresh(anomaly)

    return anomaly

@router.post("/{anomaly_id}/resolve")
def resolve_anomaly(anomaly_id: str, db: Session = Depends(get_db)):
    anm = db.query(AnomalyModel).filter(AnomalyModel.anomaly_id == anomaly_id).first()
    if anm:
        anm.status = "resolved"
        db.commit()
    return {"message": "Anomaly status updated to resolved"}
