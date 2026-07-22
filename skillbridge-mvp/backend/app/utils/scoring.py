import re
from typing import List, Optional


def _normalize_skill(skill: Optional[str]) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (skill or "").lower()).strip()


def get_required_skills_for_role(profile_role: Optional[str]) -> List[str]:
    normalized_role = (profile_role or "data-analyst").strip().lower().replace(" ", "-")
    role_map = {
        "data-analyst": ["sql", "excel", "analysis", "dashboard"],
        "tech-support": ["excel", "support", "troubleshooting", "documentation"],
        "business-analyst": ["stakeholder", "process", "requirements", "analysis"],
        "python-developer": ["python", "sql", "automation", "api"],
        "data-engineer": ["python", "sql", "pipeline", "etl"],
        "ml-engineer": ["python", "machine learning", "cloud", "model"],
    }
    return role_map.get(normalized_role, role_map["data-analyst"])


def calculate_assessment_score(answers: List[dict]) -> int:
    if not answers:
        return 0
    correct = 0
    for answer in answers:
        selected = answer.get("selected_option")
        correct_option = answer.get("correct_option")
        if selected and correct_option and selected.lower() == correct_option.lower():
            correct += 1
    return round((correct / len(answers)) * 100)


def get_next_focus_skill(profile_role: Optional[str], selected_skills: Optional[List[str]] = None, score: Optional[int] = None) -> str:
    required_skills = get_required_skills_for_role(profile_role)
    if not required_skills:
        return "Consistency"

    display_name_map = {
        "sql": "SQL",
        "excel": "Excel",
        "analysis": "Analysis",
        "dashboard": "Dashboard",
        "support": "Support",
        "troubleshooting": "Troubleshooting",
        "documentation": "Documentation",
        "stakeholder": "Stakeholder",
        "process": "Process",
        "requirements": "Requirements",
        "python": "Python",
        "automation": "Automation",
        "api": "API",
        "pipeline": "Pipeline",
        "etl": "ETL",
        "machine learning": "Machine Learning",
        "cloud": "Cloud",
        "model": "Model",
    }

    normalized_selected_tokens = set()
    for skill in selected_skills or []:
        if not skill:
            continue
        normalized_selected_tokens.update(_normalize_skill(skill).split())

    for skill in required_skills:
        required_tokens = set(_normalize_skill(skill).split())
        if not required_tokens.intersection(normalized_selected_tokens):
            normalized_skill = _normalize_skill(skill)
            return display_name_map.get(normalized_skill, skill.title())

    if score is not None and score >= 70:
        normalized_skill = _normalize_skill(required_skills[-1])
        return display_name_map.get(normalized_skill, required_skills[-1].title())
    normalized_skill = _normalize_skill(required_skills[0])
    return display_name_map.get(normalized_skill, required_skills[0].title())


def get_level_from_score(score: int) -> str:
    if score >= 70:
        return "advanced"
    if score >= 40:
        return "intermediate"
    return "beginner"


def calculate_risk(score: Optional[int], completed_lessons: int) -> str:
    if score is None:
        score = 0
    if completed_lessons == 0 and score < 35:
        return "high"
    if score < 45 or completed_lessons < 2:
        return "medium"
    return "low"


def calculate_skill_match_percentage(user_skills: Optional[List[str]], job_required_skills: Optional[List[str]], score: Optional[int] = None) -> int:
    if not user_skills or not job_required_skills:
        return 0

    normalized_user_tokens = set()
    for skill in user_skills:
        if not skill:
            continue
        normalized_user_tokens.update(_normalize_skill(skill).split())

    if not normalized_user_tokens:
        return 0

    matched = 0
    for required_skill in job_required_skills:
        if not required_skill:
            continue
        required_tokens = set(_normalize_skill(required_skill).split())
        if required_tokens.intersection(normalized_user_tokens):
            matched += 1

    if not job_required_skills:
        return 0
    return round((matched / len(job_required_skills)) * 100)


def calculate_job_match(profile_role: str, level: str, score: Optional[int] = None, skills: Optional[List[str]] = None) -> int:
    normalized_role = (profile_role or "data-analyst").strip().lower().replace(" ", "-")
    required_skills = get_required_skills_for_role(normalized_role)
    return calculate_skill_match_percentage(skills, required_skills, score=score)
