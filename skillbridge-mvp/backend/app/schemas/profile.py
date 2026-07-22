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
