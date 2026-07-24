from pydantic import BaseModel
from typing import Optional


class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    preferred_language: Optional[str] = None
    country: Optional[str] = None
    age: Optional[int] = None
    employment_status: Optional[str] = None
    target_role: Optional[str] = None
    weekly_hours: Optional[int] = None
    current_level: Optional[str] = None
    # DB AI Career Navigator path fields
    user_path: Optional[str] = None  # "A", "B", "C"
    current_db_position: Optional[str] = None
    current_db_department: Optional[str] = None
    current_designation: Optional[str] = None  # analyst, associate, avp, vp, director
    current_company: Optional[str] = None
    current_external_role: Optional[str] = None
    education: Optional[str] = None
    certifications: Optional[str] = None
    experience_years: Optional[int] = None
