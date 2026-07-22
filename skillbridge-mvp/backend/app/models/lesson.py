import uuid

from sqlalchemy import Column, DateTime, Integer, String, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False, index=True)
    description = Column(String(1000), nullable=False)
    category = Column(String(100), nullable=False, index=True)
    level = Column(String(50), nullable=False, default="beginner")
    estimated_minutes = Column(Integer, default=15)
    lesson_order = Column(Integer, default=1)
    content = Column(String(4000), nullable=False)
    quiz_question = Column(String(1000), nullable=False)
    quiz_options = Column(JSON, nullable=False, default=list)
    quiz_correct_answer = Column(String(50), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    progress = relationship("LessonProgress", back_populates="lesson", cascade="all, delete-orphan")
