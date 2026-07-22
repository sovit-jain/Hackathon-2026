from typing import List

from pydantic import BaseModel


class LessonOut(BaseModel):
    id: str
    title: str
    description: str
    category: str
    level: str
    estimated_minutes: int
    lesson_order: int
    content: str
    quiz_question: str
    quiz_options: List[str]
    quiz_correct_answer: str
    completed: bool = False
    score: int = 0
    generated_content: str | None = None
