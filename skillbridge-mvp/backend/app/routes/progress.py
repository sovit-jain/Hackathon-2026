import json
import logging
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.assessment import Assessment, Profile
from app.models.lesson import Lesson
from app.models.progress import LessonProgress
from app.models.user import User
from app.routes.auth import get_current_user
from app.schemas.progress import DashboardOut
from app.utils.scoring import calculate_risk, get_next_focus_skill
from app.utils.lesson_context import get_lesson_level_for_score, get_lesson_levels_for_path, resolve_lesson_context
from app.routes.learning import build_role_lesson_plan, ensure_role_lessons

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/progress", tags=["progress"])


def get_priority_badge(score: Optional[int]) -> str:
    if score is None:
        score = 0
    if score < 30:
        return "HIGH"
    if score <= 60:
        return "MEDIUM"
    return "LOW"


@router.get("/dashboard", response_model=DashboardOut)
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DashboardOut:
    logger.info("Dashboard requested for user_id=%s", current_user.id)
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    ensure_role_lessons(db, profile.target_role if profile else None)
    latest_assessment = (
        db.query(Assessment)
        .filter(Assessment.user_id == current_user.id)
        .order_by(Assessment.created_at.desc())
        .first()
    )

    latest_score = latest_assessment.score if latest_assessment else 0
    target_role = profile.target_role if profile else "data-analyst"
    current_level = profile.current_level if profile else "beginner"
    target_role_context, resolved_level = resolve_lesson_context(target_role, current_level)
    resolved_level = get_lesson_level_for_score(latest_score) if latest_score is not None else resolved_level

    from app.routes.learning import build_role_lesson_plan
    
    lessons_for_path = (
        db.query(Lesson)
        .filter(Lesson.category == target_role)
        .order_by(Lesson.lesson_order)
        .all()
    )
    if not lessons_for_path:
        lessons_for_path = db.query(Lesson).order_by(Lesson.lesson_order).all()

    lesson_ids_for_path = {lesson.id for lesson in lessons_for_path}
    
    # Include generated lessons in count (up to 5 total) to match learning path display
    lesson_payloads_for_count = list(lessons_for_path[:5])
    if len(lesson_payloads_for_count) < 5:
        for generated_lesson in build_role_lesson_plan(target_role, resolved_level)[:5]:
            if len(lesson_payloads_for_count) >= 5:
                break
            if any(db_lesson.title == generated_lesson["title"] for db_lesson in lessons_for_path):
                continue
            lesson_ids_for_path.add(f"generated-{len(lesson_payloads_for_count)}")
            lesson_payloads_for_count.append(generated_lesson)
    
    completed_progress = (
        db.query(LessonProgress)
        .filter(
            LessonProgress.user_id == current_user.id,
            LessonProgress.completed.is_(True),
            LessonProgress.lesson_id.in_(list(lesson_ids_for_path)),
        )
        .all()
    )
    completed_lessons = len(completed_progress)
    total_lessons = len(lesson_payloads_for_count)
    completion_rate = round((completed_lessons / total_lessons) * 100) if total_lessons else 0
    risk_level = calculate_risk(latest_score, completed_lessons).upper()

    next_lesson = "Start the next lesson"
    unfinished = None
    completed_ids = {progress.lesson_id for progress in completed_progress}
    if completed_lessons < total_lessons:
        unfinished = next((lesson for lesson in lessons_for_path if lesson.id not in completed_ids), None)
        if unfinished:
            next_lesson = unfinished.title

    learning_path = f"{'Beginner' if latest_score < 40 else 'Standard' if latest_score < 70 else 'Advanced'} {target_role_context.replace('-', ' ').title()} Path"
    level_name = resolved_level.lower()
    if level_name == "advanced":
        ai_path_explanation = (
            f"{current_user.name}, your {learning_path} is designed to sharpen higher-impact execution and help you move into more strategic work."
        )
    elif level_name == "intermediate":
        ai_path_explanation = (
            f"{current_user.name}, your {learning_path} is built to deepen your current skills and turn practice into stronger momentum."
        )
    else:
        ai_path_explanation = (
            f"{current_user.name}, your {learning_path} is tailored to your foundation and will guide you toward the next practical step with confidence."
        )

    selected_skills = []
    if profile and profile.skills_json:
        try:
            selected_skills = json.loads(profile.skills_json)
        except (TypeError, ValueError):
            selected_skills = []
    elif latest_assessment and getattr(latest_assessment, 'answers_json', None):
        try:
            selected_skills = json.loads(latest_assessment.answers_json)
        except (TypeError, ValueError):
            selected_skills = []

    next_focus_skill = get_next_focus_skill(target_role, selected_skills, latest_score)
    next_move_text = next_lesson
    if next_focus_skill:
        next_move_text = f"Learn {next_focus_skill} — a key skill for {target_role_context.replace('-', ' ').title()}"
    elif unfinished:
        next_move_text = f"Start {unfinished.title}"

    result = DashboardOut(
        full_name=current_user.name,
        target_role=target_role,
        current_level=current_level,
        completed_lessons=completed_lessons,
        total_lessons=total_lessons,
        completion_rate=completion_rate,
        latest_score=latest_score,
        risk_level=risk_level,
        next_lesson=next_lesson,
        skill_score=latest_score,
        skill_level=(profile.skill_level if profile and profile.skill_level else "beginner"),
        lessons_completed=completed_lessons,
        completion_percent=completion_rate,
        avg_quiz_score=None,
        learning_path=learning_path,
        ai_path_explanation=ai_path_explanation,
        weekly_hours=profile.weekly_hours if profile and profile.weekly_hours is not None else 5,
        next_focus_skill=next_focus_skill or "Consistency",
        next_move_priority=get_priority_badge(latest_score),
        next_move=next_move_text,
    )
    logger.info("Dashboard returned user_id=%s completed_lessons=%s total_lessons=%s latest_score=%s", current_user.id, completed_lessons, total_lessons, latest_score)
    return result
