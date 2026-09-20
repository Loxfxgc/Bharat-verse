"""
BharatVerse - Resources API
Universal Resource Model & Digital Twin state endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database.connection import get_db
from ..database.db_models import ResourceModel, CourseModel, AnomalyModel, RecommendationModel
from ..schemas.schemas import ResourceResponse, ResourceCreate, ResourceUpdate

router = APIRouter(prefix="/api/resources", tags=["Resources"])

@router.get("", response_model=List[ResourceResponse])
def get_resources(
    type: Optional[str] = None,
    status: Optional[str] = None,
    building_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(ResourceModel)
    if type:
        query = query.filter(ResourceModel.type == type)
    if status:
        query = query.filter(ResourceModel.status == status)
    if building_id:
        query = query.filter(ResourceModel.building_id == building_id)

    resources = query.all()
    # Populate dynamic utilization rate
    for r in resources:
        r.utilization_rate = round((r.current_occupancy / max(1, r.capacity)) * 100.0, 1)
    return resources

@router.get("/digital-twin/overview")
def get_digital_twin_overview(db: Session = Depends(get_db)):
    resources = db.query(ResourceModel).all()
    total_resources = len(resources)
    available = sum(1 for r in resources if r.status == "available")
    occupied = sum(1 for r in resources if r.status == "occupied")
    maintenance = sum(1 for r in resources if r.status == "maintenance")

    total_cap = sum(r.capacity for r in resources)
    total_occ = sum(r.current_occupancy for r in resources)
    avg_utilization = round((total_occ / max(1, total_cap)) * 100.0, 1)

    active_alerts = db.query(AnomalyModel).filter(AnomalyModel.status == "active").count()
    pending_approvals = db.query(RecommendationModel).filter(RecommendationModel.status == "pending").count()

    return {
        "total_resources": total_resources,
        "available_resources": available,
        "occupied_resources": occupied,
        "maintenance_resources": maintenance,
        "overall_utilization_pct": avg_utilization,
        "active_alerts_count": active_alerts,
        "pending_approvals_count": pending_approvals,
        "system_status": "ONLINE",
        "digital_twin_sync_rate": "100%"
    }

@router.get("/{resource_id}", response_model=ResourceResponse)
def get_resource_by_id(resource_id: str, db: Session = Depends(get_db)):
    r = db.query(ResourceModel).filter(ResourceModel.resource_id == resource_id).first()
    if not r:
        raise HTTPException(status_code=404, detail=f"Resource {resource_id} not found")
    r.utilization_rate = round((r.current_occupancy / max(1, r.capacity)) * 100.0, 1)
    return r

@router.post("", response_model=ResourceResponse)
def create_resource(payload: ResourceCreate, db: Session = Depends(get_db)):
    existing = db.query(ResourceModel).filter(ResourceModel.resource_id == payload.resource_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Resource ID already exists")

    new_res = ResourceModel(**payload.dict())
    db.add(new_res)
    db.commit()
    db.refresh(new_res)
    new_res.utilization_rate = 0.0
    return new_res

@router.put("/{resource_id}", response_model=ResourceResponse)
def update_resource(resource_id: str, payload: ResourceUpdate, db: Session = Depends(get_db)):
    res = db.query(ResourceModel).filter(ResourceModel.resource_id == resource_id).first()
    if not res:
        raise HTTPException(status_code=404, detail="Resource not found")

    for field, val in payload.dict(exclude_unset=True).items():
        setattr(res, field, val)

    db.commit()
    db.refresh(res)
    res.utilization_rate = round((res.current_occupancy / max(1, res.capacity)) * 100.0, 1)
    return res

@router.delete("/{resource_id}")
def delete_resource(resource_id: str, db: Session = Depends(get_db)):
    res = db.query(ResourceModel).filter(ResourceModel.resource_id == resource_id).first()
    if not res:
        raise HTTPException(status_code=404, detail="Resource not found")
    db.delete(res)
    db.commit()
    return {"message": f"Resource {resource_id} deleted successfully"}
