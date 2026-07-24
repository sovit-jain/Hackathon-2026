from typing import List, Optional

from pydantic import BaseModel


class ProgressUpdate(BaseModel):
    score: int


class DashboardOut(BaseModel):
    full_name: str
    target_role: str
    current_level: str
    completed_lessons: int
    total_lessons: int
    completion_rate: float
    latest_score: int
    risk_level: str
    next_lesson: str
    skill_score: int
    skill_level: str
    lessons_completed: int
    completion_percent: float
    avg_quiz_score: Optional[float] = None
    learning_path: str
    ai_path_explanation: str
    weekly_hours: int = 5
    next_focus_skill: Optional[str] = None
    next_move_priority: str = "MEDIUM"
    next_move: Optional[str] = None
    # DB AI Career Navigator path fields
    user_path: Optional[str] = None          # "A", "B", "C"
    score_type: Optional[str] = None          # "DB Career Score" / "DB Readiness Score" / "Employability Score"
    jobs_locked: bool = False                 # True for Path C until score >= 60
