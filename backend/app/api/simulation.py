"""
BharatVerse - Simulation API
What-If Scenario execution and comparison
"""

import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database.connection import get_db
from ..database.db_models import ResourceModel, CourseModel, ScenarioModel
from ..schemas.schemas import SimulationRequest, SimulationResponse
from ..services.simulation_service import simulation_engine

router = APIRouter(prefix="/api/simulation", tags=["Simulation"])

@router.post("/run", response_model=SimulationResponse)
def run_simulation(payload: SimulationRequest, db: Session = Depends(get_db)):
    course = db.query(CourseModel).filter(CourseModel.course_id == payload.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    source_room = db.query(ResourceModel).filter(ResourceModel.resource_id == course.current_room_id).first()
    target_room = db.query(ResourceModel).filter(ResourceModel.resource_id == payload.target_room_id).first()

    if not source_room or not target_room:
        raise HTTPException(status_code=404, detail="Source or target room not found")

    sim_res = simulation_engine.simulate_course_reassignment(
        course={
            "course_id": course.course_id,
            "code": course.code,
            "name": course.name,
            "enrolled_students": payload.simulate_enrollment or course.enrolled_students,
            "required_capabilities": course.required_capabilities or []
        },
        source_room={
            "resource_id": source_room.resource_id,
            "name": source_room.name,
            "capacity": source_room.capacity,
            "cost_per_hour": source_room.cost_per_hour
        },
        target_room={
            "resource_id": target_room.resource_id,
            "name": target_room.name,
            "capacity": target_room.capacity,
            "status": target_room.status,
            "capabilities": target_room.capabilities or [],
            "cost_per_hour": target_room.cost_per_hour
        },
        simulated_enrollment=payload.simulate_enrollment
    )

    scenario_id = f"SCN_{uuid.uuid4().hex[:8].upper()}"
    scenario = ScenarioModel(
        scenario_id=scenario_id,
        name=payload.scenario_name,
        description=f"Move {course.code} from {source_room.name} to {target_room.name}",
        parameters=payload.dict(),
        results=sim_res,
        created_at=datetime.utcnow()
    )
    db.add(scenario)
    db.commit()

    return SimulationResponse(
        scenario_id=scenario_id,
        course_id=course.course_id,
        course_name=course.name,
        enrolled_students=payload.simulate_enrollment or course.enrolled_students,
        source_room_id=source_room.resource_id,
        target_room_id=target_room.resource_id,
        capacity_check=sim_res["capacity_check"],
        availability_check=sim_res["availability_check"],
        equipment_check=sim_res["equipment_check"],
        schedule_conflict=sim_res["schedule_conflict"],
        delta_utilization=sim_res["delta_utilization"],
        delta_cost=sim_res["delta_cost"],
        feasible=sim_res["feasible"],
        summary=sim_res["summary"]
    )

@router.get("/scenarios")
def list_scenarios(db: Session = Depends(get_db)):
    return db.query(ScenarioModel).order_by(ScenarioModel.created_at.desc()).all()
