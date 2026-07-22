from typing import List, Optional

from pydantic import BaseModel


class JobOut(BaseModel):
    id: str
    title: str
    company: str
    company_logo_url: Optional[str] = None
    location: str
    work_type: str
    level: str
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    currency: str = "EUR"
    salary: str
    description: str
    description_short: str
    description_full: str
    required_skills: List[str] = []
    role: str
    date_posted: Optional[str] = None
    application_url: Optional[str] = None
    match_score: int
    reasons: str
    saved: bool = False
    matched_skills: List[str] = []
    missing_skills: List[str] = []


class JobMatchOut(BaseModel):
    job: JobOut
