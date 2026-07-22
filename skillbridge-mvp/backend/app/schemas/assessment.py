from typing import Any, List, Optional

from pydantic import BaseModel, Field


class AssessmentAnswer(BaseModel):
    question_id: int
    selected_option: str


class AssessmentSubmit(BaseModel):
    answers: List[AssessmentAnswer] = Field(default_factory=list)
    goal: str = "data-analyst"
    skills: List[str] = Field(default_factory=list)
    employment_status: Optional[str] = None


class AssessmentQuestionOut(BaseModel):
    id: int
    text: str
    options: List[str]
    topic: str


class AssessmentResult(BaseModel):
    score: int
    level: str
    recommended_path: str
    lessons: List[dict]
    explanation: Optional[str] = None
    score_source: Optional[str] = None
    label: Optional[str] = None
    summary: Optional[str] = None
    top_skill: Optional[str] = None
    missing_key_skill: Optional[str] = None
