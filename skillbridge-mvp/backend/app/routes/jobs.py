import ast
import json
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.assessment import Assessment, Profile
from app.models.job import Job, JobMatch, UserSavedJob
from app.models.user import User
from app.routes.auth import get_current_user
from app.schemas.job import JobOut
from app.utils.scoring import calculate_job_match, calculate_skill_match_percentage
from app.utils.designation import (
    get_applicable_designations,
    get_designation_from_experience,
    normalize_designation,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


def _normalize_role(role: Optional[str]) -> str:
    return (role or "db-technology").strip().lower().replace(" ", "-")


def _parse_skills(raw_skills: Optional[object]) -> List[str]:
    if not raw_skills:
        return []
    if isinstance(raw_skills, list):
        return [str(item).strip() for item in raw_skills if str(item).strip()]
    if isinstance(raw_skills, str):
        trimmed = raw_skills.strip()
        if trimmed.startswith("["):
            try:
                parsed = ast.literal_eval(trimmed)
                if isinstance(parsed, list):
                    return [str(item).strip() for item in parsed if str(item).strip()]
            except (SyntaxError, ValueError):
                pass
        try:
            parsed = json.loads(trimmed)
            if isinstance(parsed, list):
                return [str(item).strip() for item in parsed if str(item).strip()]
        except (TypeError, ValueError):
            return [trimmed]
    return []


def _parse_required_skills(raw_skills: Optional[object]) -> List[str]:
    if not raw_skills:
        return []
    if isinstance(raw_skills, list):
        return [str(item).strip() for item in raw_skills if str(item).strip()]
    if isinstance(raw_skills, str):
        trimmed = raw_skills.strip()
        if trimmed.startswith("["):
            try:
                parsed = ast.literal_eval(trimmed)
                if isinstance(parsed, list):
                    return [str(item).strip() for item in parsed if str(item).strip()]
            except (SyntaxError, ValueError):
                pass
        try:
            parsed = json.loads(trimmed)
            if isinstance(parsed, list):
                return [str(item).strip() for item in parsed if str(item).strip()]
        except (TypeError, ValueError):
            return [trimmed]
    return []


def _format_salary(job: Job) -> str:
    if job.salary_min and job.salary_max:
        return f"{job.currency} {job.salary_min//1000}k–{job.salary_max//1000}k/year"
    return job.salary or "Salary available on request"


def _serialize_job(job: Job, skills: List[str], saved_ids: set, reasons: str, match_score: int) -> JobOut:
    required_skills = _parse_required_skills(job.required_skills)
    matched_skills = [skill for skill in required_skills if any(skill.lower() in existing.lower() for existing in skills)]
    missing_skills = [skill for skill in required_skills if skill not in matched_skills]
    description_short = job.description_short or job.description or "A role that fits your current learning path."
    description_full = job.description_full or job.description or description_short
    return JobOut(
        id=job.id,
        title=job.title,
        company=job.company,
        company_logo_url=job.company_logo_url,
        location=job.location,
        work_type=job.work_type or "remote",
        level=job.level or "mid-level",
        salary_min=job.salary_min,
        salary_max=job.salary_max,
        currency=job.currency or "EUR",
        salary=_format_salary(job),
        description=description_short,
        description_short=description_short,
        description_full=description_full,
        required_skills=required_skills,
        role=job.role,
        date_posted=job.date_posted.strftime("%Y-%m-%d") if job.date_posted else None,
        application_url=job.application_url,
        match_score=match_score,
        reasons=reasons,
        saved=job.id in saved_ids,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
    )


@router.get("", response_model=List[JobOut])
def get_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[JobOut]:
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    latest_assessment = (
        db.query(Assessment)
        .filter(Assessment.user_id == current_user.id)
        .order_by(Assessment.created_at.desc())
        .first()
    )
    role = _normalize_role(profile.target_role if profile else "db-technology")
    level = (profile.skill_level if profile and profile.skill_level else profile.current_level if profile else "beginner") or "beginner"
    score = latest_assessment.score if latest_assessment and latest_assessment.score is not None else (profile.skill_score if profile else 0)
    skills = _parse_skills(profile.skills_json if profile and profile.skills_json else None)
    if not skills and latest_assessment and getattr(latest_assessment, "answers_json", None):
        try:
            parsed_answers = json.loads(latest_assessment.answers_json)
            if isinstance(parsed_answers, list):
                skills = [str(item) for item in parsed_answers if str(item).strip()]
        except (TypeError, ValueError):
            skills = []

    # Path C: lock jobs if score < 60 and jobs_unlocked is False
    user_path = profile.user_path if profile else None
    jobs_unlocked = profile.jobs_unlocked if profile else True
    if user_path == "C" and not jobs_unlocked:
        logger.info("Jobs locked for Path C user_id=%s score=%s", current_user.id, score)
        return []

    # Determine user's current designation
    current_designation = None
    if profile:
        if profile.current_designation:
            # Use explicitly set designation
            current_designation = normalize_designation(profile.current_designation)
        elif user_path == "C" and profile.experience_years is not None:
            # Path C: map from experience years
            current_designation = get_designation_from_experience(profile.experience_years)
        elif user_path == "A":
            # Path A: default to analyst if not set
            current_designation = "analyst"

    applicable_designations = get_applicable_designations(current_designation)
    logger.info("Job list requested for user_id=%s role=%s level=%s score=%s path=%s designation=%s applicable=%s", 
                current_user.id, role, level, score, user_path, current_designation, applicable_designations)

    # Show only Deutsche Bank jobs for DB roles; fall back to role-matched jobs for legacy roles
    db_role_prefixes = ("db-risk", "db-technology", "db-compliance", "db-quant", "db-product", "db-cloud", "db-ml", "db-data")
    if role in db_role_prefixes:
        jobs = db.query(Job).filter(
            Job.role == role,
            Job.company == "Deutsche Bank",
            Job.is_active.is_(True)
        ).all()
    else:
        jobs = db.query(Job).filter(Job.role == role, Job.is_active.is_(True)).all()

    # Filter jobs by applicable designations if designation is set
    if applicable_designations:
        filtered_jobs = []
        for job in jobs:
            job_level = normalize_designation(job.level)
            if job_level in applicable_designations:
                filtered_jobs.append(job)
        jobs = filtered_jobs
        logger.info("Filtered jobs by designation user_id=%s original=%d filtered=%d", current_user.id, len(jobs) + len(filtered_jobs), len(jobs))

    saved_jobs = db.query(UserSavedJob).filter(UserSavedJob.user_id == current_user.id).all()
    saved_ids = {saved.job_id for saved in saved_jobs}

    results: List[JobOut] = []
    for job in jobs:
        required_skills = _parse_required_skills(job.required_skills)
        match_score = calculate_skill_match_percentage(skills, required_skills, score=score)
        reasons = "Strong overlap with your current skills and Deutsche Bank target role"
        match = JobMatch(user_id=current_user.id, job_id=job.id, score=match_score, reasons=reasons)
        db.merge(match)
        results.append(_serialize_job(job, skills, saved_ids, reasons, match_score))

    db.commit()
    logger.info("Job matches updated for user_id=%s jobs=%d", current_user.id, len(results))
    return sorted(results, key=lambda item: (-item.match_score, item.title.lower()))


@router.get("/saved", response_model=List[str])
def get_saved_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[str]:
    saved_jobs = db.query(UserSavedJob).filter(UserSavedJob.user_id == current_user.id).all()
    return [saved.job_id for saved in saved_jobs]


@router.post("/{job_id}/save")
def save_job(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    existing = db.query(UserSavedJob).filter(UserSavedJob.user_id == current_user.id, UserSavedJob.job_id == job_id).first()
    if not existing:
        db.add(UserSavedJob(user_id=current_user.id, job_id=job_id))
        db.commit()
    return {"message": "Saved", "job_id": job_id}


@router.delete("/{job_id}/save")
def unsave_job(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    saved_job = db.query(UserSavedJob).filter(UserSavedJob.user_id == current_user.id, UserSavedJob.job_id == job_id).first()
    if saved_job:
        db.delete(saved_job)
        db.commit()
    return {"message": "Removed", "job_id": job_id}


@router.get("/matches", response_model=List[JobOut])
def get_job_matches(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[JobOut]:
    return get_jobs(db, current_user)
