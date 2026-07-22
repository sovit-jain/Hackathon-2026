import logging
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.assessment import Assessment, Profile
from app.models.progress import LessonProgress
from app.models.user import User
from app.routes.auth import get_current_user
from app.utils.llm import generate_intervention
from app.utils.scoring import calculate_risk

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/risk", tags=["risk"])


@router.get("/assessment")
def get_risk(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    logger.info("Risk assessment requested for user_id=%s", current_user.id)
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    latest_score = 0
    latest_assessment = (
        db.query(Assessment)
        .filter(Assessment.user_id == current_user.id)
        .order_by(Assessment.created_at.desc())
        .first()
    )
    if latest_assessment:
        latest_score = latest_assessment.score

    completed_lessons = db.query(LessonProgress).filter(LessonProgress.user_id == current_user.id, LessonProgress.completed.is_(True)).count()
    risk_level = calculate_risk(latest_score, completed_lessons).upper()
    days_since_login = 0
    if current_user.last_login:
        days_since_login = max(0, (datetime.utcnow().date() - current_user.last_login.date()).days)
    logger.info("Risk assessment calculated user_id=%s latest_score=%s completed_lessons=%s risk_level=%s", current_user.id, latest_score, completed_lessons, risk_level)
    return {"risk_level": risk_level, "message": "Great start! Keep the momentum going.", "days_since_login": days_since_login}


@router.get("/status")
def get_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    return get_risk(db, current_user)


@router.post("/intervention")
async def intervention(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    logger.info("Intervention requested for user_id=%s", current_user.id)
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    latest_assessment = (
        db.query(Assessment)
        .filter(Assessment.user_id == current_user.id)
        .order_by(Assessment.created_at.desc())
        .first()
    )
    latest_score = latest_assessment.score if latest_assessment else 0
    completed_lessons = db.query(LessonProgress).filter(LessonProgress.user_id == current_user.id, LessonProgress.completed.is_(True)).count()

    message = await generate_intervention(current_user.name, latest_score, completed_lessons)
    result = {"risk_level": calculate_risk(latest_score, completed_lessons), "message": message, "role": profile.target_role if profile else "data-analyst"}
    logger.info("Intervention response user_id=%s risk_level=%s", current_user.id, result["risk_level"])
    return result
