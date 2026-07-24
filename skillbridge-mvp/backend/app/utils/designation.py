"""Designation hierarchy management for Deutsche Bank career progression."""

from typing import Optional

# Designation hierarchy levels
DESIGNATION_HIERARCHY = ["analyst", "associate", "avp", "vp", "director"]


def get_designation_from_experience(experience_years: Optional[int]) -> str:
    """
    Map years of experience to designation level.
    - 0-3 years: Analyst
    - 3-6 years: Associate
    - 6-15 years: AVP
    - 15-25 years: VP
    - 25+ years: Director
    """
    if experience_years is None:
        return "analyst"
    
    if experience_years < 3:
        return "analyst"
    elif experience_years < 6:
        return "associate"
    elif experience_years < 15:
        return "avp"
    elif experience_years < 25:
        return "vp"
    else:
        return "director"


def normalize_designation(designation: Optional[str]) -> str:
    """Normalize designation to lowercase and handle aliases."""
    if not designation:
        return "analyst"
    
    normalized = designation.strip().lower().replace(" ", "")
    
    # Handle common aliases
    aliases = {
        "analyst": "analyst",
        "associate": "associate",
        "avp": "avp",
        "vp": "vp",
        "director": "director",
        "junior": "analyst",
        "mid": "associate",
        "mid-level": "associate",
        "senior": "avp",
        "lead": "vp",
        "management": "vp",
        "executive": "director",
    }
    
    return aliases.get(normalized, "analyst")


def get_next_designation(current: Optional[str]) -> Optional[str]:
    """Get the next designation level in the hierarchy."""
    if not current:
        return None
    
    normalized = normalize_designation(current)
    if normalized not in DESIGNATION_HIERARCHY:
        return None
    
    idx = DESIGNATION_HIERARCHY.index(normalized)
    if idx < len(DESIGNATION_HIERARCHY) - 1:
        return DESIGNATION_HIERARCHY[idx + 1]
    
    return None  # Already at director level


def get_applicable_designations(current: Optional[str]) -> list[str]:
    """
    Get applicable designation levels for job filtering.
    Returns current designation and next level (if exists).
    Example: analyst -> [analyst, associate]
    """
    if not current:
        return ["analyst", "associate"]
    
    normalized = normalize_designation(current)
    result = [normalized]
    
    next_designation = get_next_designation(normalized)
    if next_designation:
        result.append(next_designation)
    
    return result


def is_valid_designation(designation: Optional[str]) -> bool:
    """Check if designation is valid."""
    if not designation:
        return False
    normalized = normalize_designation(designation)
    return normalized in DESIGNATION_HIERARCHY
