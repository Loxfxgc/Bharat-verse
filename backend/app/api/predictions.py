"""
BharatVerse - Predictions API
Endpoints for XGBoost Demand and Occupancy forecasting
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database.connection import get_db
from ..database.db_models import ResourceModel
from ..schemas.schemas import PredictionRequest, PredictionResponse
from ..services.prediction_service import prediction_service

router = APIRouter(prefix="/api/predictions", tags=["Predictions"])

@router.post("/predict", response_model=PredictionResponse)
def predict_room_occupancy(payload: PredictionRequest, db: Session = Depends(get_db)):
    room = db.query(ResourceModel).filter(ResourceModel.resource_id == payload.room_id).first()
    cap = room.capacity if room else 100
    cost = room.cost_per_hour if room else 60.0
    equip_count = len(room.capabilities) if room else 2

    is_wknd = payload.is_weekend if payload.is_weekend is not None else (1 if payload.day_of_week >= 5 else 0)

    pred = prediction_service.predict_occupancy(
        room_capacity=cap,
        day_of_week=payload.day_of_week,
        hour=payload.hour,
        is_weekend=is_wknd,
        exam_period=payload.exam_period or 0,
        equipment_count=equip_count,
        cost_per_hour=cost
    )

    return PredictionResponse(
        room_id=payload.room_id,
        day_of_week=payload.day_of_week,
        hour=payload.hour,
        predicted_occupancy=pred["predicted_occupancy"],
        room_capacity=cap,
        predicted_utilization=pred["predicted_utilization"],
        confidence=pred["confidence"],
        shortage_risk=pred["shortage_risk"],
        status=pred["status"]
    )

@router.get("/{resource_id}")
def get_resource_prediction(resource_id: str, day_of_week: int = 0, db: Session = Depends(get_db)):
    room = db.query(ResourceModel).filter(ResourceModel.resource_id == resource_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Resource not found")

    forecast = prediction_service.get_24h_forecast(room.capacity, day_of_week)
    return {
        "resource_id": resource_id,
        "resource_name": room.name,
        "capacity": room.capacity,
        "day_of_week": day_of_week,
        "forecast_curve": forecast
    }
