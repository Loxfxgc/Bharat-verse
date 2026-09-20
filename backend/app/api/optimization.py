"""
BharatVerse - Optimization API
OR-Tools Constraint Optimization & Allocation Solver
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database.connection import get_db
from ..database.db_models import ResourceModel, CourseModel, RecommendationModel
from ..schemas.schemas import OptimizationRequest, OptimizationResponse
from ..services.optimization_service import constraint_optimizer
from ..services.explanation_service import explanation_service

router = APIRouter(prefix="/api/optimization", tags=["Optimization"])

@router.post("/run", response_model=OptimizationResponse)
def run_optimization(payload: OptimizationRequest, db: Session = Depends(get_db)):
    course = db.query(CourseModel).filter(CourseModel.course_id == payload.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    rooms = db.query(ResourceModel).all()
    rooms_data = [
        {
            "resource_id": r.resource_id,
            "name": r.name,
            "capacity": r.capacity,
            "status": r.status,
            "capabilities": r.capabilities or [],
            "cost_per_hour": r.cost_per_hour
        }
        for r in rooms
    ]

    current_room = db.query(ResourceModel).filter(ResourceModel.resource_id == course.current_room_id).first()
    current_room_dict = {
        "resource_id": current_room.resource_id if current_room else "UNKNOWN",
        "name": current_room.name if current_room else "Unknown Room",
        "capacity": current_room.capacity if current_room else 0,
        "cost_per_hour": current_room.cost_per_hour if current_room else 50.0
    }

    course_dict = {
        "course_id": course.course_id,
        "code": course.code,
        "name": course.name,
        "enrolled_students": course.enrolled_students,
        "required_capabilities": course.required_capabilities or [],
        "day": course.day,
        "time_slot": course.time_slot
    }

    # Run OR-Tools CP-SAT Solver
    solution = constraint_optimizer.solve_room_allocation(
        course=course_dict,
        available_rooms=rooms_data,
        current_room=current_room_dict
    )

    best_room_id = solution["best_allocation"]
    target_room = next((r for r in rooms_data if r["resource_id"] == best_room_id), None) if best_room_id else None

    # Generate explainable recommendation card
    explanation = {}
    if target_room:
        explanation = explanation_service.generate_recommendation_card(
            course=course_dict,
            current_room=current_room_dict,
            target_room=target_room,
            confidence=0.91
        )

        # Store recommendation in DB if not existing
        existing_rec = db.query(RecommendationModel).filter(
            RecommendationModel.rec_id == explanation["rec_id"]
        ).first()

        if not existing_rec:
            new_rec = RecommendationModel(
                rec_id=explanation["rec_id"],
                problem=explanation["problem"],
                course_id=course.course_id,
                from_room_id=current_room_dict["resource_id"],
                to_room_id=target_room["resource_id"],
                reasons=explanation["reasons"],
                impact=explanation["expected_impact"],
                confidence=explanation["confidence"],
                risk_level=explanation["risk_level"],
                status="pending"
            )
            db.add(new_rec)
            db.commit()

    return OptimizationResponse(
        solver_status=solution["solver_status"],
        course_id=course.course_id,
        course_name=course.name,
        enrolled_students=course.enrolled_students,
        current_room_id=course.current_room_id,
        best_allocation=best_room_id,
        candidates=solution["evaluated_candidates"][:10], # Top candidate rooms
        explanation=explanation,
        risk_level="medium",
        requires_approval=True
    )
