import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.sql import func

from app.database import Base


class LessonContent(Base):
    __tablename__ = "lesson_content"

    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False, index=True)
    lesson_id = Column(String(50), ForeignKey("lessons.id"), nullable=False, index=True)
    generated_content = Column(String(10000), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
