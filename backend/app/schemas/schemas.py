"""
BharatVerse - Pydantic Schemas
Defines request and response schemas for all API endpoints.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

# 1. Resource Schemas (Universal Resource Model)
class ResourceBase(BaseModel):
    resource_id: str
    name: str
    type: str = "room"
    capacity: int = 0
    building_id: Optional[str] = None
    floor: int = 1
    location: Optional[str] = None
    status: str = "available" # available, occupied, maintenance, reserved
    capabilities: List[str] = []
    cost_per_hour: float = 50.0
    current_occupancy: int = 0

class ResourceCreate(ResourceBase):
    pass

class ResourceUpdate(BaseModel):
    name: Optional[str] = None
    capacity: Optional[int] = None
    status: Optional[str] = None
    capabilities: Optional[List[str]] = None
    cost_per_hour: Optional[float] = None
    current_occupancy: Optional[int] = None

class ResourceResponse(ResourceBase):
    id: int
    utilization_rate: Optional[float] = 0.0

    class Config:
        from_attributes = True

# 2. Prediction Schemas
class PredictionRequest(BaseModel):
    room_id: str
    day_of_week: int = Field(..., ge=0, le=6, description="0=Monday, 6=Sunday")
    hour: int = Field(..., ge=0, le=23, description="Hour of day (0-23)")
    is_weekend: Optional[int] = None
    exam_period: Optional[int] = 0

class PredictionResponse(BaseModel):
    room_id: str
    day_of_week: int
    hour: int
    predicted_occupancy: int
    room_capacity: int
    predicted_utilization: float
    confidence: float
    shortage_risk: bool
    status: str

# 3. Anomaly Schemas
class AnomalyResponse(BaseModel):
    anomaly_id: str
    resource_id: str
    timestamp: datetime
    observed_value: float
    expected_range: str
    anomaly_type: str
    severity: str
    status: str

    class Config:
        from_attributes = True

# 4. Simulation Schemas
class SimulationRequest(BaseModel):
    scenario_name: str = "Class Relocation Test"
    course_id: str = "CRS_DS301"
    target_room_id: str = "ROOM_R102"
    simulate_enrollment: Optional[int] = None

class SimulationResponse(BaseModel):
    scenario_id: str
    course_id: str
    course_name: str
    enrolled_students: int
    source_room_id: str
    target_room_id: str
    capacity_check: str # PASS / FAIL
    availability_check: str # PASS / FAIL
    equipment_check: str # PASS / FAIL
    schedule_conflict: str # NONE / CONFLICT
    delta_utilization: float
    delta_cost: float
    feasible: bool
    summary: str

# 5. Optimization Schemas (OR-Tools)
class OptimizationRequest(BaseModel):
    course_id: str = "CRS_DS301"
    force_solver: bool = True

class OptimizationCandidate(BaseModel):
    room_id: str
    name: str
    capacity: int
    status: str
    capabilities: List[str]
    feasible: bool
    rejection_reasons: List[str] = []
    objective_score: float

class OptimizationResponse(BaseModel):
    solver_status: str
    course_id: str
    course_name: str
    enrolled_students: int
    current_room_id: str
    best_allocation: Optional[str]
    candidates: List[OptimizationCandidate]
    explanation: Dict[str, Any]
    risk_level: str
    requires_approval: bool

# 6. Recommendation Schemas
class RecommendationResponse(BaseModel):
    rec_id: str
    problem: str
    course_id: str
    from_room_id: str
    to_room_id: str
    reasons: List[str]
    impact: Dict[str, Any]
    confidence: float
    risk_level: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

# 7. Approval & Feedback Schemas
class ApprovalAction(BaseModel):
    decision: str = "approved" # approved, rejected
    reviewer: str = "Campus Operations Director"
    comments: Optional[str] = "Approved after constraint verification."

class FeedbackResponse(BaseModel):
    feedback_id: str
    recommendation_id: Optional[str]
    action_description: str
    predicted_utilization: float
    actual_utilization: float
    deviation: float
    accuracy_score: float
    created_at: datetime

    class Config:
        from_attributes = True
