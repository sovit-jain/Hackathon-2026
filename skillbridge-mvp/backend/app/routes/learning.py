import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.assessment import Assessment, Profile
from app.models.lesson import Lesson
from app.models.lesson_content import LessonContent
from app.models.progress import LessonProgress
from app.models.user import User
from app.routes.auth import get_current_user
from app.schemas.lesson import LessonOut
from app.utils.lesson_context import get_lesson_level_for_score, get_lesson_levels_for_path, get_lesson_lock_state, resolve_lesson_context
from app.utils.llm import generate_lesson_content

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/learning", tags=["learning"])


def _normalize_role(role: Optional[str]) -> str:
    normalized_role = (role or "data-analyst").strip().lower().replace(" ", "-")
    if normalized_role not in ROLE_LESSON_BLUEPRINTS:
        return "data-analyst"
    return normalized_role


def _build_level_variant_lessons(role: Optional[str], level: Optional[str]) -> List[Dict[str, Any]]:
    normalized_role = _normalize_role(role)
    normalized_level = (level or "beginner").strip().lower()
    if normalized_level not in {"beginner", "intermediate", "advanced"}:
        normalized_level = "beginner"

    base_lessons = ROLE_LESSON_BLUEPRINTS[normalized_role]
    variants: List[Dict[str, Any]] = []
    for lesson_data in base_lessons:
        description = lesson_data["description"]
        if normalized_level == "advanced":
            description = f"{description} Focus on deeper practice, stronger judgment, and more ownership."
        elif normalized_level == "intermediate":
            description = f"{description} Build on the basics with more practical application."
        else:
            description = f"{description} Start with a steady foundation and simple, practical habits."

        variants.append(
            {
                **lesson_data,
                "level": normalized_level,
                "description": description,
            }
        )

    return variants


def ensure_role_lessons(db: Session, role: Optional[str]) -> None:
    normalized_role = _normalize_role(role)

    for lesson_level in ("beginner", "intermediate", "advanced"):
        for lesson_data in _build_level_variant_lessons(normalized_role, lesson_level):
            existing = (
                db.query(Lesson)
                .filter(
                    Lesson.category == normalized_role,
                    Lesson.title == lesson_data["title"],
                    Lesson.level == lesson_data["level"],
                )
                .first()
            )
            if existing:
                continue

            lesson = Lesson(
                title=lesson_data["title"],
                description=lesson_data["description"],
                category=normalized_role,
                level=lesson_data["level"],
                estimated_minutes=lesson_data["estimated_minutes"],
                lesson_order=lesson_data["lesson_order"],
                content=lesson_data["description"],
                quiz_question=f"What is the main takeaway from {lesson_data['title']}?",
                quiz_options=["Use it in a real workflow", "Ignore it", "Skip practice", "Pretend it is not needed"],
                quiz_correct_answer="Use it in a real workflow",
            )
            db.add(lesson)

    db.commit()


ROLE_LESSON_BLUEPRINTS: Dict[str, List[Dict[str, Any]]] = {
    "tech-support": [
        {"title": "Excel Essentials for Support", "description": "Build confidence with the spreadsheets and documentation habits that support teams rely on.", "level": "beginner", "estimated_minutes": 20, "lesson_order": 1},
        {"title": "Troubleshooting and Ticket Triage", "description": "Learn how to classify problems, document symptoms, and move requests forward with clarity.", "level": "beginner", "estimated_minutes": 25, "lesson_order": 2},
        {"title": "Service Communication", "description": "Practice calm, clear updates that help customers feel informed and supported.", "level": "beginner", "estimated_minutes": 20, "lesson_order": 3},
        {"title": "Workflow Documentation", "description": "Create repeatable notes and guides so common support tasks become easier to hand off.", "level": "intermediate", "estimated_minutes": 25, "lesson_order": 4},
        {"title": "Support Metrics Basics", "description": "Track response times, resolution trends, and priority work so you can improve service quality.", "level": "intermediate", "estimated_minutes": 20, "lesson_order": 5},
    ],
    "data-analyst": [
        {"title": "SQL Foundations for Analysts", "description": "Learn how to query, filter, and shape tables so your analysis is reliable.", "level": "beginner", "estimated_minutes": 25, "lesson_order": 1},
        {"title": "Data Cleaning Basics", "description": "Turn rough spreadsheets and exports into trustworthy analysis-ready data.", "level": "beginner", "estimated_minutes": 20, "lesson_order": 2},
        {"title": "Dashboard Storytelling", "description": "Present findings with clear visuals and a concise narrative people can act on.", "level": "intermediate", "estimated_minutes": 25, "lesson_order": 3},
        {"title": "Metrics and KPIs", "description": "Define what success looks like and connect numbers to business goals.", "level": "intermediate", "estimated_minutes": 20, "lesson_order": 4},
        {"title": "Insight Communication", "description": "Translate analysis into decisions, recommendations, and follow-up actions.", "level": "intermediate", "estimated_minutes": 25, "lesson_order": 5},
    ],
    "business-analyst": [
        {"title": "Stakeholder Interviews", "description": "Learn how to gather requirements and turn conversations into clear business needs.", "level": "beginner", "estimated_minutes": 20, "lesson_order": 1},
        {"title": "Process Mapping", "description": "Document current workflows so opportunities become easier to spot.", "level": "beginner", "estimated_minutes": 20, "lesson_order": 2},
        {"title": "Requirement Writing", "description": "Turn messy ideas into usable user stories and acceptance criteria.", "level": "intermediate", "estimated_minutes": 25, "lesson_order": 3},
        {"title": "Change Management Basics", "description": "Understand how to support adoption when new processes or tools are introduced.", "level": "intermediate", "estimated_minutes": 20, "lesson_order": 4},
        {"title": "Business Case Building", "description": "Frame initiatives around value, cost, and expected outcomes.", "level": "intermediate", "estimated_minutes": 25, "lesson_order": 5},
    ],
    "python-developer": [
        {"title": "Python Fundamentals", "description": "Build a strong base in variables, loops, functions, and debugging.", "level": "beginner", "estimated_minutes": 25, "lesson_order": 1},
        {"title": "Working with Data", "description": "Learn to load, inspect, and transform structured data with Python.", "level": "beginner", "estimated_minutes": 20, "lesson_order": 2},
        {"title": "Testing Basics", "description": "Write small tests that make your code easier to trust and extend.", "level": "intermediate", "estimated_minutes": 20, "lesson_order": 3},
        {"title": "APIs and Requests", "description": "Fetch and use data from public services and internal endpoints.", "level": "intermediate", "estimated_minutes": 25, "lesson_order": 4},
        {"title": "Automation Patterns", "description": "Create simple scripts that save time and reduce repetitive work.", "level": "intermediate", "estimated_minutes": 20, "lesson_order": 5},
    ],
    "data-engineer": [
        {"title": "Data Modeling Foundations", "description": "Learn how to shape data for reliability, scale, and useful downstream analysis.", "level": "beginner", "estimated_minutes": 25, "lesson_order": 1},
        {"title": "ETL Design Basics", "description": "Build simple pipelines that move data from source to warehouse with confidence.", "level": "beginner", "estimated_minutes": 20, "lesson_order": 2},
        {"title": "SQL for Pipelines", "description": "Use SQL to transform data and support recurring business reporting.", "level": "intermediate", "estimated_minutes": 25, "lesson_order": 3},
        {"title": "Storage and Performance", "description": "Learn the trade-offs that affect speed, cost, and reliability.", "level": "intermediate", "estimated_minutes": 20, "lesson_order": 4},
        {"title": "Observability Basics", "description": "Set up routine checks so pipeline health is visible before issues grow.", "level": "intermediate", "estimated_minutes": 25, "lesson_order": 5},
    ],
    "ml-engineer": [
        {"title": "Machine Learning Foundations", "description": "Understand the core workflow behind training, evaluating, and improving models.", "level": "beginner", "estimated_minutes": 25, "lesson_order": 1},
        {"title": "Data Preparation", "description": "Prepare and clean features so models learn from high-quality input.", "level": "beginner", "estimated_minutes": 20, "lesson_order": 2},
        {"title": "Model Evaluation", "description": "Measure whether a model is actually useful for the problem you care about.", "level": "intermediate", "estimated_minutes": 25, "lesson_order": 3},
        {"title": "Deployment Basics", "description": "Learn how to package a model so it can be used in real workflows.", "level": "intermediate", "estimated_minutes": 20, "lesson_order": 4},
        {"title": "Monitoring and Feedback", "description": "Build habits for tracking drift and keeping your model useful over time.", "level": "intermediate", "estimated_minutes": 25, "lesson_order": 5},
    ],
}


def build_role_lesson_plan(role: Optional[str], level: Optional[str]) -> List[Dict[str, Any]]:
    return _build_level_variant_lessons(role, level)


def build_learning_path_name(score: int, role: Optional[str]) -> str:
    normalized_role = (role or "data-analyst").strip().lower().replace(" ", "-")
    role_label = normalized_role.replace("-", " ").title()
    if score < 40:
        stage = "Beginner"
    elif score < 70:
        stage = "Standard"
    else:
        stage = "Advanced"
    return f"{stage} {role_label} Path"


def build_learning_path_explanation(user_name: Optional[str], score: int, role: Optional[str], level: str) -> str:
    normalized_role = (role or "data-analyst").strip().replace("-", " ").title()
    normalized_level = (level or "beginner").strip().lower()
    if normalized_level == "advanced" or score >= 70:
        message = (
            "You are already showing strong momentum, so this path focuses on polishing your evidence "
            "and moving into more strategic work."
        )
    elif normalized_level == "intermediate" or score >= 40:
        message = (
            "You are in a strong middle ground, so this path emphasizes a few high-impact skills while keeping "
            "the pace manageable."
        )
    else:
        message = (
            "You are at the start of the journey, so this path emphasizes confidence-building fundamentals and "
            "a steady routine."
        )
    return f"{user_name or 'You'} are well positioned for a {normalized_role} transition. {message}"


def generate_learning_path_explanation(user_name: Optional[str], score: int, role: Optional[str], level: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return build_learning_path_explanation(user_name, score, role, level)

    prompt = (
        f"Write a concise onboarding explanation for a learner named {user_name or 'you'} who has a skill score of {score} "
        f"and wants to grow toward the {role or 'data-analyst'} role at a {level} level. Keep it to two short sentences, "
        "encouraging and useful for career growth."
    )

    try:
        base_url = os.getenv("OPENAI_BASE_URL") or os.getenv("OPENAI_API_BASE") or "https://api.openai.com/v1"
        response = httpx.post(
            f"{base_url.rstrip('/')}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.4,
                "max_tokens": 120,
            },
            timeout=15.0,
        )
        response.raise_for_status()
        data = response.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        if content:
            return content
    except Exception as exc:
        logger.warning("LLM explanation request failed: %s", exc)

    return build_learning_path_explanation(user_name, score, role, level)


@router.get("/lessons", response_model=List[LessonOut])
def get_lessons(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[LessonOut]:
    logger.info("Lesson list requested for user_id=%s", current_user.id)
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    ensure_role_lessons(db, profile.target_role if profile else None)
    assessment = db.query(Assessment).filter(Assessment.user_id == current_user.id).order_by(Assessment.created_at.desc()).first()
    target_role, level = resolve_lesson_context(
        profile.target_role if profile else None,
        profile.current_level if profile else None,
    )
    score = assessment.score if assessment and assessment.score is not None else (profile.skill_score if profile else 0)
    resolved_level = get_lesson_level_for_score(score) if score is not None else level

    lessons = db.query(Lesson).filter(Lesson.category == target_role, Lesson.level == resolved_level).order_by(Lesson.lesson_order).all()
    if not lessons:
        lessons = db.query(Lesson).filter(Lesson.category == target_role).order_by(Lesson.lesson_order).all()

    results: List[LessonOut] = []
    for lesson in lessons:
        progress = db.query(LessonProgress).filter(LessonProgress.user_id == current_user.id, LessonProgress.lesson_id == lesson.id).first()
        results.append(
            LessonOut(
                id=lesson.id,
                title=lesson.title,
                description=lesson.description,
                category=lesson.category,
                level=lesson.level,
                estimated_minutes=lesson.estimated_minutes,
                lesson_order=lesson.lesson_order,
                content=lesson.content,
                quiz_question=lesson.quiz_question,
                quiz_options=lesson.quiz_options,
                quiz_correct_answer=lesson.quiz_correct_answer,
                completed=progress.completed if progress else False,
                score=progress.score if progress else 0,
            )
        )
    logger.info("Lesson list returned user_id=%s lessons=%d", current_user.id, len(results))
    return results


@router.get("/lessons/{lesson_id}", response_model=LessonOut)
async def get_lesson_detail(
    lesson_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LessonOut:
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    ensure_role_lessons(db, profile.target_role if profile else None)
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")

    progress = db.query(LessonProgress).filter(LessonProgress.user_id == current_user.id, LessonProgress.lesson_id == lesson.id).first()
    lesson_content_record = db.query(LessonContent).filter(LessonContent.user_id == current_user.id, LessonContent.lesson_id == lesson.id).first()
    generated_content = lesson_content_record.generated_content if lesson_content_record else None

    if not generated_content:
        try:
            profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
            assessment = db.query(Assessment).filter(Assessment.user_id == current_user.id).order_by(Assessment.created_at.desc()).first()
            score = assessment.score if assessment and assessment.score is not None else (profile.skill_score if profile else 0)
            skill_level = profile.skill_level if profile and profile.skill_level else get_lesson_level_for_score(score)
            generated_content = await generate_lesson_content(
                current_user.name,
                profile.target_role if profile else "data-analyst",
                skill_level,
                lesson.title,
                lesson.description,
            )
            if generated_content:
                lesson_content_record = LessonContent(
                    user_id=current_user.id,
                    lesson_id=lesson.id,
                    generated_content=generated_content,
                )
                db.add(lesson_content_record)
                db.commit()
        except Exception:
            logger.exception("Lesson content generation failed for lesson_id=%s user_id=%s", lesson_id, current_user.id)

    if not generated_content:
        generated_content = "Content is being prepared. Please try again in a moment."

    return LessonOut(
        id=lesson.id,
        title=lesson.title,
        description=lesson.description,
        category=lesson.category,
        level=lesson.level,
        estimated_minutes=lesson.estimated_minutes,
        lesson_order=lesson.lesson_order,
        content=lesson.content,
        quiz_question=lesson.quiz_question,
        quiz_options=lesson.quiz_options,
        quiz_correct_answer=lesson.quiz_correct_answer,
        completed=progress.completed if progress else False,
        score=progress.score if progress else 0,
        generated_content=generated_content,
    )


@router.post("/lessons/{lesson_id}/complete")
def complete_lesson(
    lesson_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    logger.info("Complete lesson requested lesson_id=%s user_id=%s", lesson_id, current_user.id)
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        logger.warning("Lesson not found lesson_id=%s user_id=%s", lesson_id, current_user.id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")

    progress = db.query(LessonProgress).filter(LessonProgress.user_id == current_user.id, LessonProgress.lesson_id == lesson.id).first()
    if not progress:
        progress = LessonProgress(
            user_id=current_user.id,
            lesson_id=lesson.id,
            completed=True,
            score=100,
            completed_at=datetime.utcnow(),
        )
        db.add(progress)
    else:
        progress.completed = True
        progress.score = max(progress.score, 100)
        progress.completed_at = progress.completed_at or datetime.utcnow()

    db.commit()
    logger.info("Lesson completed lesson_id=%s user_id=%s", lesson_id, current_user.id)
    return {"message": f"Completed {lesson.title}", "lesson_id": lesson.id}


@router.get("/path")
def get_path(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    ensure_role_lessons(db, profile.target_role if profile else None)
    assessment = db.query(Assessment).filter(Assessment.user_id == current_user.id).order_by(Assessment.created_at.desc()).first()

    role = profile.target_role if profile else "data-analyst"
    level = (profile.current_level if profile else "beginner") or "beginner"
    level = level.strip().lower()
    if level not in {"beginner", "intermediate", "advanced"}:
        level = "beginner"

    score = 0
    if assessment and assessment.score is not None:
        score = assessment.score
    elif profile and profile.skill_score is not None:
        score = profile.skill_score

    target_role, resolved_level = resolve_lesson_context(role, level)
    resolved_level = get_lesson_level_for_score(score) if score is not None else resolved_level
    lessons = (
        db.query(Lesson)
        .filter(Lesson.category == target_role)
        .filter(Lesson.level == resolved_level)
        .order_by(Lesson.lesson_order)
        .all()
    )
    if not lessons:
        lessons = db.query(Lesson).filter(Lesson.category == target_role, Lesson.level == resolved_level).order_by(Lesson.lesson_order).all()
    if not lessons:
        lessons = db.query(Lesson).filter(Lesson.category == "data-analyst").order_by(Lesson.lesson_order).all()

    progress_records = db.query(LessonProgress).filter(LessonProgress.user_id == current_user.id).all()
    completed_lesson_ids = {record.lesson_id for record in progress_records if record.completed}
    completed_lesson_orders = [lesson.lesson_order for lesson in lessons if lesson.id in completed_lesson_ids]

    lesson_payloads = []
    if lessons:
        for lesson in lessons[:5]:
            progress = next((record for record in progress_records if record.lesson_id == lesson.id), None)
            display_index = len(lesson_payloads)
            lesson_status = "ready" if display_index == 0 else ("completed" if progress and progress.completed else "locked")
            if progress and progress.completed:
                lesson_status = "completed"
            elif display_index == 0:
                lesson_status = "ready"
            else:
                # Check if all previous lessons in display order are completed
                all_previous_completed = all(lesson_payloads[i]["completed"] for i in range(display_index))
                lesson_status = "ready" if all_previous_completed else "locked"
            lesson_payloads.append(
                {
                    "id": lesson.id,
                    "title": lesson.title,
                    "description": lesson.description,
                    "level": lesson.level,
                    "estimated_minutes": lesson.estimated_minutes,
                    "lesson_order": lesson.lesson_order,
                    "completed": progress.completed if progress else False,
                    "status": lesson_status,
                    "locked": lesson_status == "locked",
                }
            )
    if len(lesson_payloads) < 5:
        for lesson in build_role_lesson_plan(role, resolved_level)[:5]:
            if len(lesson_payloads) >= 5:
                break
            if any(existing["title"] == lesson["title"] for existing in lesson_payloads):
                continue

            db_lesson = db.query(Lesson).filter(Lesson.category == target_role, Lesson.title == lesson["title"]).first()
            display_index = len(lesson_payloads)
            all_previous_completed = all(lesson_payloads[i]["completed"] for i in range(display_index))
            lesson_status = "ready" if display_index == 0 else ("ready" if all_previous_completed else "locked")

            if db_lesson:
                progress = next((record for record in progress_records if record.lesson_id == db_lesson.id), None)
                lesson_payloads.append(
                    {
                        "id": db_lesson.id,
                        "title": db_lesson.title,
                        "description": db_lesson.description,
                        "level": db_lesson.level,
                        "estimated_minutes": db_lesson.estimated_minutes,
                        "lesson_order": db_lesson.lesson_order,
                        "completed": progress.completed if progress else False,
                        "status": lesson_status,
                        "locked": lesson_status == "locked",
                    }
                )
                continue

            lesson_payloads.append(
                {
                    "id": f"role-{role}-{lesson['lesson_order']}",
                    "title": lesson["title"],
                    "description": lesson["description"],
                    "level": lesson["level"],
                    "estimated_minutes": lesson["estimated_minutes"],
                    "lesson_order": lesson["lesson_order"],
                    "completed": False,
                    "status": lesson_status,
                    "locked": lesson_status == "locked",
                }
            )

    path_name = build_learning_path_name(score, role)
    explanation = generate_learning_path_explanation(current_user.name, score, role, resolved_level)
    result = {
        "path_name": path_name,
        "role": role,
        "target_role": target_role,
        "level": resolved_level,
        "score": score,
        "explanation": explanation,
        "lessons": lesson_payloads,
    }
    logger.info("Learning path requested user_id=%s role=%s level=%s score=%s", current_user.id, role, resolved_level, score)
    return result
