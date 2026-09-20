"""
BharatVerse - Approvals API
Risk-Aware Human Gate & Automated Action Execution
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database.connection import get_db
from ..database.db_models import RecommendationModel, ApprovalModel, AuditLogModel
from ..schemas.schemas import ApprovalAction
from ..services.automation_service import automation_engine

router = APIRouter(prefix="/api/approvals", tags=["Approvals"])

@router.get("/pending")
def get_pending_approvals(db: Session = Depends(get_db)):
    return db.query(RecommendationModel).filter(RecommendationModel.status == "pending").all()

@router.post("/{rec_id}/approve")
def approve_recommendation(rec_id: str, payload: ApprovalAction = ApprovalAction(), db: Session = Depends(get_db)):
    result = automation_engine.execute_recommendation(
        db=db,
        recommendation_id=rec_id,
        reviewer=payload.reviewer,
        action="approved",
        comments=payload.comments
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result

@router.post("/{rec_id}/reject")
def reject_recommendation(rec_id: str, payload: ApprovalAction = ApprovalAction(decision="rejected"), db: Session = Depends(get_db)):
    result = automation_engine.execute_recommendation(
        db=db,
        recommendation_id=rec_id,
        reviewer=payload.reviewer,
        action="rejected",
        comments=payload.comments or "Rejected by administrator."
    )
    return result

@router.get("/audit-logs")
def get_audit_logs(db: Session = Depends(get_db)):
    return db.query(AuditLogModel).order_by(AuditLogModel.timestamp.desc()).all()
