import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.data.questions import QUESTIONS
from app.database import get_db
from app.models.assessment import Assessment, Profile
from app.models.lesson import Lesson
from app.models.user import User
from app.routes.auth import get_current_user
from app.schemas.assessment import AssessmentQuestionOut, AssessmentResult, AssessmentSubmit
import json
from app.utils.scoring import calculate_assessment_score, get_level_from_score
from app.utils.llm_scoring import llm_score_assessment, score_skills_assessment

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/assessment", tags=["assessment"])


SKILL_CATEGORIES = [
    {
        "category": "Finance & Banking",
        "weight": "High",
        "skills": ["Risk Management", "Financial Modelling", "Basel III", "Credit Analysis", "None"],
    },
    {
        "category": "Data & Analytics",
        "weight": "High",
        "skills": ["SQL", "Python", "Power BI", "Statistics", "None"],
    },
    {
        "category": "Technology",
        "weight": "High",
        "skills": ["Cloud (AWS/Azure)", "Java", "API Development", "Agile/DevOps", "None"],
    },
    {
        "category": "Compliance & Regulation",
        "weight": "Medium",
        "skills": ["AML", "KYC", "Regulatory Compliance", "Risk Assessment", "None"],
    },
    {
        "category": "Quantitative Methods",
        "weight": "Expert",
        "skills": ["Derivatives Pricing", "Monte Carlo", "Machine Learning", "Linear Algebra", "None"],
    },
    {
        "category": "Product & Business",
        "weight": "Medium",
        "skills": ["Product Management", "Stakeholder Management", "Roadmapping", "Business Analysis", "None"],
    },
]


@router.get("/questions", response_model=List[AssessmentQuestionOut])
def get_questions() -> List[AssessmentQuestionOut]:
    logger.info("Assessment questions requested, returning %d items", len(QUESTIONS))
    return [AssessmentQuestionOut(**question) for question in QUESTIONS]


@router.get("/skills")
def get_skills() -> List[dict]:
    return SKILL_CATEGORIES


@router.post("/submit-skills", response_model=AssessmentResult)
def submit_skills(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AssessmentResult:
    skills = payload.get("skills") or []
    if not isinstance(skills, list) or not skills:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Select at least one skill")

    goal = payload.get("goal") or "data-analyst"
    employment_status = payload.get("employment_status")
    llm_result = llm_score_assessment([], goal, skills, employment_status)
    score = llm_result.get("score", 0)
    level = llm_result.get("level") or get_level_from_score(score)
    explanation = llm_result.get("explanation", "")
    label = llm_result.get("label")
    summary = llm_result.get("summary")
    top_skill = llm_result.get("top_skill")
    missing_key_skill = llm_result.get("missing_key_skill")
    score_source = llm_result.get("source", "llm")

    assessment = Assessment(
        user_id=current_user.id,
        score=score,
        level=level,
        answers_json=str(skills),
        score_source=score_source,
        missing_key_skill=missing_key_skill,
    )
    db.add(assessment)

    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        profile = Profile(user_id=current_user.id)
        db.add(profile)
    profile.target_role = goal or profile.target_role
    profile.current_level = level
    profile.weekly_hours = 5 if score < 50 else 8
    profile.skills_json = json.dumps(skills)
    profile.skill_score = score
    profile.skill_level = level
    # Path C: auto-unlock jobs when initial score >= 60
    if profile.user_path == "C" and score >= 60:
        profile.jobs_unlocked = True
    db.commit()
    db.refresh(profile)

    return AssessmentResult(
        score=score,
        level=level,
        recommended_path=profile.target_role,
        lessons=[],
        explanation=explanation,
        score_source=score_source,
        label=label,
        summary=summary,
        top_skill=top_skill,
        missing_key_skill=missing_key_skill,
    )


@router.post("/submit", response_model=AssessmentResult)
def submit_assessment(
    payload: AssessmentSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AssessmentResult:
    logger.info("Assessment submit received for user_id=%s goal=%s answers=%d", current_user.id, payload.goal, len(payload.answers))
    answer_payloads = []
    for answer in payload.answers:
        question = next((q for q in QUESTIONS if q["id"] == answer.question_id), None)
        if not question:
            logger.warning("Invalid question id submitted user_id=%s question_id=%s", current_user.id, answer.question_id)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid question id")
        answer_payloads.append({"selected_option": answer.selected_option, "correct_option": question["correct_option"]})

    llm_result = llm_score_assessment(
        answer_payloads,
        payload.goal,
        getattr(payload, 'skills', []),
        getattr(payload, 'employment_status', None),
    )
    if llm_result and isinstance(llm_result.get('score'), int):
        score = llm_result['score']
        level = llm_result.get('level') or get_level_from_score(score)
        explanation = llm_result.get('explanation', '')
        score_source = llm_result.get('source', 'llm')
        logger.info('Assessment scoring used for user_id=%s score=%s level=%s source=%s', current_user.id, score, level, score_source)
    else:
        score = score_skills_assessment(getattr(payload, 'skills', []), payload.goal, getattr(payload, 'employment_status', None)).get('score', 0)
        level = get_level_from_score(score)
        explanation = ''
        score_source = 'rule'
        logger.info('Rule-based scoring used for user_id=%s score=%s level=%s', current_user.id, score, level)
    assessment = Assessment(
        user_id=current_user.id,
        score=score,
        level=level,
        answers_json=str([a.model_dump() for a in payload.answers]),
        score_source=score_source,
        missing_key_skill=llm_result.get('missing_key_skill') if isinstance(llm_result, dict) else None,
    )
    db.add(assessment)

    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        profile = Profile(user_id=current_user.id)
        db.add(profile)
    profile.target_role = payload.goal or profile.target_role
    profile.current_level = level
    profile.weekly_hours = 5 if score < 50 else 8
    # persist skills list if provided by frontend
    try:
        if getattr(payload, 'skills', None):
            profile.skills_json = json.dumps(payload.skills)
        profile.skill_score = score
        profile.skill_level = level
    except Exception:
        logger.exception("Failed to persist skills or skill fields for user_id=%s", current_user.id)
    # store skill scoring on profile so frontend can show progress
    try:
        profile.skill_score = score
        profile.skill_level = level
        # keep skills_json unchanged unless provided elsewhere
    except Exception:
        logger.exception("Failed to update profile skill fields for user_id=%s", current_user.id)

    lessons = db.query(Lesson).filter(Lesson.category == profile.target_role).order_by(Lesson.lesson_order).all()
    if not lessons:
        lessons = db.query(Lesson).order_by(Lesson.lesson_order).all()

    db.commit()
    db.refresh(profile)

    logger.info("Assessment stored user_id=%s score=%s level=%s target_role=%s", current_user.id, score, level, profile.target_role)
    return AssessmentResult(
        score=score,
        level=level,
        recommended_path=profile.target_role,
        lessons=[{
            "id": lesson.id,
            "title": lesson.title,
            "description": lesson.description,
            "level": lesson.level,
            "estimated_minutes": lesson.estimated_minutes,
        } for lesson in lessons[:4]],
        explanation=explanation,
        score_source=score_source,
    )
