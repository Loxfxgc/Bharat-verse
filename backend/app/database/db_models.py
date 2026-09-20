"""
BharatVerse - SQLAlchemy Database Models
Implements tables for Phase 4 Universal Resource Model, Digital Twin state,
schedules, anomalies, optimizations, recommendations, approvals, and audit trail.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON
from .connection import Base

class ResourceModel(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(128), nullable=False)
    type = Column(String(32), default="room") # room, auditorium, laboratory, seminar
    capacity = Column(Integer, default=0)
    building_id = Column(String(64))
    floor = Column(Integer, default=1)
    location = Column(String(128))
    status = Column(String(32), default="available") # available, occupied, maintenance, reserved
    capabilities = Column(JSON, default=list) # e.g. ["projector", "computer", "audio"]
    cost_per_hour = Column(Float, default=50.0)
    current_occupancy = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CourseModel(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(String(64), unique=True, index=True, nullable=False)
    code = Column(String(32), nullable=False)
    name = Column(String(128), nullable=False)
    enrolled_students = Column(Integer, default=0)
    faculty_id = Column(String(64))
    required_capabilities = Column(JSON, default=list)
    current_room_id = Column(String(64))
    day = Column(String(32))
    time_slot = Column(String(64))
    priority = Column(String(32), default="medium")

class FacultyModel(Base):
    __tablename__ = "faculty"

    id = Column(Integer, primary_key=True, index=True)
    faculty_id = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(128), nullable=False)
    department = Column(String(128))
    title = Column(String(64))
    email = Column(String(128))
    expertise = Column(JSON, default=list)

class EquipmentModel(Base):
    __tablename__ = "equipment"

    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(128), nullable=False)
    type = Column(String(64))
    status = Column(String(32), default="functional")
    room_id = Column(String(64))

class AnomalyModel(Base):
    __tablename__ = "anomalies"

    id = Column(Integer, primary_key=True, index=True)
    anomaly_id = Column(String(64), unique=True, index=True)
    resource_id = Column(String(64), index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    observed_value = Column(Float)
    expected_range = Column(String(64))
    anomaly_type = Column(String(64)) # "Spike", "Ghost Occupancy", "Off-Hours Usage"
    severity = Column(String(32), default="medium") # "low", "medium", "high", "critical"
    status = Column(String(32), default="active") # "active", "resolved", "dismissed"

class ScenarioModel(Base):
    __tablename__ = "scenarios"

    id = Column(Integer, primary_key=True, index=True)
    scenario_id = Column(String(64), unique=True, index=True)
    name = Column(String(128), nullable=False)
    description = Column(Text)
    parameters = Column(JSON, default=dict)
    results = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

class RecommendationModel(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    rec_id = Column(String(64), unique=True, index=True)
    problem = Column(Text, nullable=False)
    course_id = Column(String(64), nullable=False)
    from_room_id = Column(String(64), nullable=False)
    to_room_id = Column(String(64), nullable=False)
    reasons = Column(JSON, default=list)
    impact = Column(JSON, default=dict)
    confidence = Column(Float, default=0.90)
    risk_level = Column(String(32), default="medium") # low, medium, high
    status = Column(String(32), default="pending") # pending, approved, rejected, executed
    created_at = Column(DateTime, default=datetime.utcnow)

class ApprovalModel(Base):
    __tablename__ = "approvals"

    id = Column(Integer, primary_key=True, index=True)
    approval_id = Column(String(64), unique=True, index=True)
    recommendation_id = Column(String(64), nullable=False)
    action = Column(String(32), default="approved") # approved, rejected
    reviewer = Column(String(64), default="System Admin")
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class FeedbackModel(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    feedback_id = Column(String(64), unique=True, index=True)
    recommendation_id = Column(String(64))
    action_description = Column(String(255))
    predicted_utilization = Column(Float)
    actual_utilization = Column(Float)
    deviation = Column(Float)
    accuracy_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditLogModel(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    log_id = Column(String(64), unique=True, index=True)
    user = Column(String(64), default="Admin")
    action_type = Column(String(64))
    resource_id = Column(String(64))
    details = Column(Text)
    status = Column(String(32), default="success")
    timestamp = Column(DateTime, default=datetime.utcnow)
