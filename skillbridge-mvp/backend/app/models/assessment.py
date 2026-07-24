import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(50), ForeignKey("users.id"), unique=True, nullable=False)
    target_role = Column(String(100), default="db-technology")
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

    # DB AI Career Navigator path fields
    user_path = Column(String(10), nullable=True)  # "A" = DB Employee, "B" = External, "C" = Unemployed
    # Path A - DB Employee
    current_db_position = Column(String(200), nullable=True)
    current_db_department = Column(String(100), nullable=True)
    current_designation = Column(String(50), nullable=True)  # analyst, associate, avp, vp, director
    # Path B - External Candidate
    current_company = Column(String(200), nullable=True)
    current_external_role = Column(String(200), nullable=True)
    # Path C - Unemployed
    education = Column(String(500), nullable=True)
    certifications = Column(String(500), nullable=True)
    experience_years = Column(Integer, nullable=True)
    jobs_unlocked = Column(Boolean, default=False)  # Path C: unlocked when score >= 60
    # Scoring
    db_score = Column(Integer, nullable=True)
    score_type = Column(String(50), nullable=True)  # "DB Career Score" / "DB Readiness Score" / "Employability Score"

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
