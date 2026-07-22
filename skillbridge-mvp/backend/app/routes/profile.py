import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.routes.auth import get_current_user
from app.schemas.profile import ProfileUpdate
from app.models.assessment import Profile

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/user", tags=["user"])

ROLE_CATALOG = [
    {
        "id": "tech-support",
        "name": "Tech Support",
        "salary": "€22,000 - €32,000/year",
        "job_market": "6,700 open positions",
    },
    {
        "id": "data-analyst",
        "name": "Data Analyst",
        "salary": "€25,000 - €35,000/year",
        "job_market": "2,300 open positions",
    },
    {
        "id": "business-analyst",
        "name": "Business Analyst",
        "salary": "€30,000 - €45,000/year",
        "job_market": "5,100 open positions",
    },
    {
        "id": "python-developer",
        "name": "Python Developer",
        "salary": "€35,000 - €55,000/year",
        "job_market": "8,900 open positions",
    },
    {
        "id": "data-engineer",
        "name": "Data Engineer",
        "salary": "€40,000 - €60,000/year",
        "job_market": "3,200 open positions",
    },
    {
        "id": "ml-engineer",
        "name": "ML Engineer",
        "salary": "€55,000 - €85,000/year",
        "job_market": "1,800 open positions",
    },
]


@router.get("/roles/search")
def search_roles(q: str = "", db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> List[dict]:
    query = (q or "").strip().lower()
    if not query:
        return ROLE_CATALOG

    filtered = [
        role for role in ROLE_CATALOG
        if query in role["id"].lower() or query in role["name"].lower()
    ]
    return filtered


@router.get("/profile")
def get_profile(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        profile = Profile(user_id=current_user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)

    return {"status": "ok", "profile": {
        "preferred_language": profile.preferred_language,
        "country": profile.country,
        "age": profile.age,
        "employment_status": profile.employment_status,
        "target_role": profile.target_role,
        "weekly_hours": profile.weekly_hours,
        "current_level": profile.current_level,
    }}


@router.post("/profile")
def update_profile(payload: ProfileUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    try:
        # Upsert profile for current_user
        profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
        if not profile:
            profile = Profile(user_id=current_user.id)
            db.add(profile)

        if payload.preferred_language is not None:
            profile.preferred_language = payload.preferred_language
        if payload.country is not None:
            profile.country = payload.country
        if payload.age is not None:
            profile.age = payload.age
        if payload.employment_status is not None:
            profile.employment_status = payload.employment_status
        if payload.target_role is not None:
            profile.target_role = payload.target_role
        if payload.weekly_hours is not None:
            profile.weekly_hours = payload.weekly_hours
        if payload.current_level is not None:
            profile.current_level = payload.current_level

        # Optionally update user name
        if payload.name:
            current_user.name = payload.name

        db.commit()
        db.refresh(profile)
        logger.info("Profile updated for user_id=%s", current_user.id)
        return {"status": "ok", "profile": {
            "preferred_language": profile.preferred_language,
            "country": profile.country,
            "age": profile.age,
            "employment_status": profile.employment_status,
            "target_role": profile.target_role,
            "weekly_hours": profile.weekly_hours,
            "current_level": profile.current_level,
        }}
    except Exception as e:
        db.rollback()
        logger.exception("Failed to update profile for user_id=%s: %s", current_user.id, e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Profile update failed: {str(e)}")
