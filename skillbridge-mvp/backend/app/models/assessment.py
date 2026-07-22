import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(50), ForeignKey("users.id"), unique=True, nullable=False)
    target_role = Column(String(100), default="data-analyst")
    weekly_hours = Column(Integer, default=5)
    current_level = Column(String(50), default="beginner")
    preferred_language = Column(String(50), nullable=True)
    country = Column(String(100), nullable=True)
    age = Column(Integer, nullable=True)
    employment_status = Column(String(50), nullable=True)
    skills_json = Column(String(2000), default='[]')
    skill_score = Column(Integer, nullable=True)
    skill_level = Column(String(50), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="profile")


class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False)
    score = Column(Integer, nullable=False, default=0)
    level = Column(String(50), nullable=False, default="beginner")
    answers_json = Column(String(2000), default="[]")
    score_source = Column(String(50), default="rule")
    missing_key_skill = Column(String(100), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="assessments")
