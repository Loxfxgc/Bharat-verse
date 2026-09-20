"""
BharatVerse - Database Seeder
Seeds initial campus resources, courses, faculty, equipment,
flagship constraint violation, and anomalies into the database.
"""

import os
import sys
import json
from datetime import datetime

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.app.database.connection import SessionLocal, engine, Base
from backend.app.database.db_models import (
    ResourceModel, CourseModel, FacultyModel, EquipmentModel,
    AnomalyModel, RecommendationModel, AuditLogModel, FeedbackModel
)

DATA_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "synthetic", "campus_resources.json")
)

def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Check if already seeded
        if db.query(ResourceModel).first():
            print("Database already contains records. Seeding skipped.")
            return

        if not os.path.exists(DATA_PATH):
            print(f"Data file {DATA_PATH} not found. Generate synthetic data first.")
            return

        with open(DATA_PATH, "r") as f:
            data = json.load(f)

        print("Seeding BharatVerse Database...")

        # 1. Rooms / Resources
        for r in data.get("rooms", []):
            db_res = ResourceModel(
                resource_id=r["resource_id"],
                name=r["name"],
                type=r.get("type", "room"),
                capacity=r.get("capacity", 50),
                building_id=r.get("building_id"),
                floor=r.get("floor", 1),
                location=r.get("location"),
                status=r.get("status", "available"),
                capabilities=r.get("capabilities", []),
                cost_per_hour=r.get("cost_per_hour", 50.0),
                current_occupancy=42 if r["resource_id"] == "ROOM_R102" else (60 if r["resource_id"] == "ROOM_R101" else 0)
            )
            db.add(db_res)

        # 2. Faculty
        for f in data.get("faculty", []):
            db_fac = FacultyModel(
                faculty_id=f["faculty_id"],
                name=f["name"],
                department=f.get("department"),
                title=f.get("title"),
                email=f.get("email"),
                expertise=f.get("expertise", [])
            )
            db.add(db_fac)

        # 3. Courses
        for c in data.get("courses", []):
            db_crs = CourseModel(
                course_id=c["course_id"],
                code=c["code"],
                name=c["name"],
                enrolled_students=c.get("enrolled_students", 0),
                faculty_id=c.get("faculty_id"),
                required_capabilities=c.get("required_capabilities", []),
                current_room_id=c.get("current_room_id"),
                day=c.get("day", "Monday"),
                time_slot=c.get("time_slot", "09:00 - 11:00"),
                priority=c.get("priority", "medium")
            )
            db.add(db_crs)

        # 4. Equipment
        for eq in data.get("equipment", []):
            db_eq = EquipmentModel(
                equipment_id=eq["equipment_id"],
                name=eq["name"],
                type=eq.get("type"),
                status=eq.get("status", "functional"),
                room_id=eq.get("room_id")
            )
            db.add(db_eq)

        # 5. Initial Detected Anomalies
        anomalies = [
            AnomalyModel(
                anomaly_id="ANM_OCC_SPIKE_01",
                resource_id="ROOM_R101",
                timestamp=datetime.utcnow(),
                observed_value=98.0,
                expected_range="0 - 51 occupants",
                anomaly_type="Severe Overcrowding Violation",
                severity="critical",
                status="active"
            ),
            AnomalyModel(
                anomaly_id="ANM_OFF_HOURS_02",
                resource_id="ROOM_C101",
                timestamp=datetime.utcnow(),
                observed_value=45.0,
                expected_range="0 - 5 occupants",
                anomaly_type="Off-Hours Unauthorized Resource Drain",
                severity="high",
                status="active"
            ),
            AnomalyModel(
                anomaly_id="ANM_GHOST_CLASS_03",
                resource_id="ROOM_B102",
                timestamp=datetime.utcnow(),
                observed_value=0.0,
                expected_range="35 - 50 occupants",
                anomaly_type="Ghost Booking (Idle Reserved Room)",
                severity="medium",
                status="active"
            )
        ]
        db.add_all(anomalies)

        # 6. Flagship Decision Recommendation (Section 7, 24, 36 & 56)
        flagship_rec = RecommendationModel(
            rec_id="REC_DS301_R102",
            problem="Room capacity shortage: DS301 requires 85 seats, but Room R101 only accommodates 60.",
            course_id="CRS_DS301",
            from_room_id="ROOM_R101",
            to_room_id="ROOM_R102",
            reasons=[
                "Room R101 capacity (60) is exceeded by 85 enrolled students (Constraint Violation).",
                "Room R102 has 100-student capacity, fully satisfying size requirements.",
                "Required equipment (Projector + Computer + Audio) is confirmed operational.",
                "Dr. X faculty schedule and slot availability remain conflict-free.",
                "Calculated operational cost is lower per student than alternative lecture halls."
            ],
            impact={
                "utilization_improvement": "+18%",
                "operational_cost_delta": "-5%",
                "constraint_satisfaction": "100% FEASIBLE",
                "risk_category": "Medium Impact (Automated Approval Gate)"
            },
            confidence=0.91,
            risk_level="medium",
            status="pending",
            created_at=datetime.utcnow()
        )
        db.add(flagship_rec)

        # 7. Audit log initial record
        audit = AuditLogModel(
            log_id="ACT_SYS_INIT",
            user="System Digital Twin",
            action_type="INITIALIZE_CAMPUS_MODEL",
            resource_id="ALL",
            details="Ingested Universal Resource Model and calibrated Digital Twin baseline.",
            status="success",
            timestamp=datetime.utcnow()
        )
        db.add(audit)

        # 8. Feedback initial baseline
        fb = FeedbackModel(
            feedback_id="FB_INIT_001",
            recommendation_id="REC_HIST_01",
            action_description="Previous semester relocation of CS101 to Hall B101",
            predicted_utilization=90.0,
            actual_utilization=86.5,
            deviation=3.5,
            accuracy_score=96.5,
            created_at=datetime.utcnow()
        )
        db.add(fb)

        db.commit()
        print("Database seeded successfully with campus data, models, and initial recommendation!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
