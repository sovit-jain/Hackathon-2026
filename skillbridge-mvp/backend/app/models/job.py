import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False, index=True)
    company = Column(String(255), nullable=False)
    company_logo_url = Column(String(500), nullable=True)
    location = Column(String(255), nullable=False)
    work_type = Column(String(50), nullable=False, default="remote")
    level = Column(String(50), nullable=False, default="mid-level")
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    currency = Column(String(10), nullable=False, default="EUR")
    salary = Column(String(100), nullable=False, default="")
    description = Column(String(2000), nullable=False, default="")
    description_short = Column(String(500), nullable=False, default="")
    description_full = Column(String(4000), nullable=False, default="")
    required_skills = Column(String(2000), nullable=False, default="[]")
    role = Column(String(100), nullable=False, index=True)
    date_posted = Column(DateTime, nullable=True)
    application_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, server_default=func.now())

    matches = relationship("JobMatch", back_populates="job", cascade="all, delete-orphan")
    saved_by = relationship("UserSavedJob", back_populates="job", cascade="all, delete-orphan")


class JobMatch(Base):
    __tablename__ = "job_matches"

    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False, index=True)
    job_id = Column(String(50), ForeignKey("jobs.id"), nullable=False, index=True)
    score = Column(Integer, nullable=False, default=0)
    reasons = Column(String(1000), nullable=False, default="")
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="job_matches")
    job = relationship("Job", back_populates="matches")


class UserSavedJob(Base):
    __tablename__ = "user_saved_jobs"

    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False, index=True)
    job_id = Column(String(50), ForeignKey("jobs.id"), nullable=False, index=True)
    saved_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="saved_jobs")
    job = relationship("Job", back_populates="saved_by")
