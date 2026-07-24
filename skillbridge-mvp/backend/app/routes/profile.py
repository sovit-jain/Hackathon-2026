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
        "id": "db-risk",
        "name": "Risk Management",
        "department": "Risk",
        "salary": "€48k–200k/year",
        "job_market": "Risk Analyst → Associate → AVP → VP → MD",
        "levels": ["Analyst", "Associate", "AVP", "VP", "Managing Director"],
    },
    {
        "id": "db-technology",
        "name": "Technology & Engineering",
        "department": "Technology",
        "salary": "€48k–180k/year",
        "job_market": "Technology Analyst → Associate → AVP → VP → MD",
        "levels": ["Analyst", "Associate", "AVP", "VP", "Managing Director"],
    },
    {
        "id": "db-compliance",
        "name": "Compliance & Regulatory",
        "department": "Compliance",
        "salary": "€44k–160k/year",
        "job_market": "Compliance Analyst → Associate → AVP → VP → MD",
        "levels": ["Analyst", "Associate", "AVP", "VP", "Managing Director"],
    },
    {
        "id": "db-quant",
        "name": "Quantitative Finance",
        "department": "Quant",
        "salary": "£55k–220k/year",
        "job_market": "Quant Analyst → Associate → AVP → VP → MD",
        "levels": ["Analyst", "Associate", "AVP", "VP", "Managing Director"],
    },
    {
        "id": "db-product",
        "name": "Product Management",
        "department": "Product",
        "salary": "€46k–170k/year",
        "job_market": "Product Analyst → Associate → AVP → VP → MD",
        "levels": ["Analyst", "Associate", "AVP", "VP", "Managing Director"],
    },
    {
        "id": "db-cloud",
        "name": "Cloud Engineering",
        "department": "Cloud",
        "salary": "€52k–190k/year",
        "job_market": "Cloud Engineer → Associate → AVP → VP → MD",
        "levels": ["Analyst", "Associate", "AVP", "VP", "Managing Director"],
    },
    {
        "id": "db-ml",
        "name": "Machine Learning & AI",
        "department": "ML",
        "salary": "£55k–210k/year",
        "job_market": "ML Analyst → Associate → AVP → VP → MD",
        "levels": ["Analyst", "Associate", "AVP", "VP", "Managing Director"],
    },
    {
        "id": "db-data",
        "name": "Data Engineering & Analytics",
        "department": "Data",
        "salary": "€46k–210k/year",
        "job_market": "Data Analyst → Associate → AVP → VP → MD",
        "levels": ["Analyst", "Associate", "AVP", "VP", "Managing Director"],
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
        "user_path": profile.user_path,
        "current_db_position": profile.current_db_position,
        "current_db_department": profile.current_db_department,
        "current_designation": profile.current_designation,
        "current_company": profile.current_company,
        "current_external_role": profile.current_external_role,
        "education": profile.education,
        "certifications": profile.certifications,
        "experience_years": profile.experience_years,
        "jobs_unlocked": profile.jobs_unlocked,
        "score_type": profile.score_type,
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
        # DB path fields
        if payload.user_path is not None:
            profile.user_path = payload.user_path
            # Auto-set score_type based on path
            path_score_map = {"A": "DB Career Score", "B": "DB Readiness Score", "C": "Employability Score"}
            profile.score_type = path_score_map.get(payload.user_path, "DB Career Score")
        if payload.current_db_position is not None:
            profile.current_db_position = payload.current_db_position
        if payload.current_db_department is not None:
            profile.current_db_department = payload.current_db_department
        if payload.current_designation is not None:
            profile.current_designation = payload.current_designation
        if payload.current_company is not None:
            profile.current_company = payload.current_company
        if payload.current_external_role is not None:
            profile.current_external_role = payload.current_external_role
        if payload.education is not None:
            profile.education = payload.education
        if payload.certifications is not None:
            profile.certifications = payload.certifications
        if payload.experience_years is not None:
            profile.experience_years = payload.experience_years

        # Optionally update user name
        if payload.name:
            current_user.name = payload.name

        db.commit()
        db.refresh(profile)
        logger.info("Profile updated for user_id=%s path=%s", current_user.id, profile.user_path)
        return {"status": "ok", "profile": {
            "preferred_language": profile.preferred_language,
            "country": profile.country,
            "age": profile.age,
            "employment_status": profile.employment_status,
            "target_role": profile.target_role,
            "weekly_hours": profile.weekly_hours,
            "current_level": profile.current_level,
            "user_path": profile.user_path,
            "current_db_position": profile.current_db_position,
            "current_db_department": profile.current_db_department,
            "current_designation": profile.current_designation,
            "current_company": profile.current_company,
            "current_external_role": profile.current_external_role,
            "education": profile.education,
            "certifications": profile.certifications,
            "experience_years": profile.experience_years,
            "jobs_unlocked": profile.jobs_unlocked,
            "score_type": profile.score_type,
        }}
    except Exception as e:
        db.rollback()
        logger.exception("Failed to update profile for user_id=%s: %s", current_user.id, e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Profile update failed: {str(e)}")
