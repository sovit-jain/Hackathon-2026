import re
from typing import List, Optional


def _normalize_skill(skill: Optional[str]) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (skill or "").lower()).strip()


def get_required_skills_for_role(profile_role: Optional[str]) -> List[str]:
    normalized_role = (profile_role or "db-technology").strip().lower().replace(" ", "-")
    role_map = {
        # Deutsche Bank roles
        "db-risk": ["risk management", "python", "excel", "sql", "financial modelling", "basel iii"],
        "db-technology": ["python", "sql", "api development", "agile", "cloud"],
        "db-compliance": ["aml", "kyc", "regulatory compliance", "risk assessment", "excel"],
        "db-quant": ["python", "statistics", "derivatives pricing", "monte carlo", "linear algebra"],
        "db-product": ["product management", "agile", "stakeholder management", "analytics", "roadmapping"],
        "db-cloud": ["aws", "azure", "terraform", "kubernetes", "docker", "python"],
        "db-ml": ["python", "machine learning", "tensorflow", "statistics", "mlops", "sql"],
        "db-data": ["sql", "python", "etl", "data pipeline", "apache spark", "data warehouse"],
        # Legacy roles (backward compat)
        "data-analyst": ["sql", "excel", "analysis", "dashboard"],
        "tech-support": ["excel", "support", "troubleshooting", "documentation"],
        "business-analyst": ["stakeholder", "process", "requirements", "analysis"],
        "python-developer": ["python", "sql", "automation", "api"],
        "data-engineer": ["python", "sql", "pipeline", "etl"],
        "ml-engineer": ["python", "machine learning", "cloud", "model"],
    }
    return role_map.get(normalized_role, role_map["db-technology"])


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
        # Legacy
        "sql": "SQL", "excel": "Excel", "analysis": "Analysis", "dashboard": "Dashboard",
        "support": "Support", "troubleshooting": "Troubleshooting", "documentation": "Documentation",
        "stakeholder": "Stakeholder", "process": "Process", "requirements": "Requirements",
        "python": "Python", "automation": "Automation", "api": "API",
        "pipeline": "Pipeline", "etl": "ETL", "machine learning": "Machine Learning",
        "cloud": "Cloud", "model": "Model",
        # DB roles
        "risk management": "Risk Management", "financial modelling": "Financial Modelling",
        "basel iii": "Basel III", "aml": "AML", "kyc": "KYC",
        "regulatory compliance": "Regulatory Compliance", "risk assessment": "Risk Assessment",
        "api development": "API Development", "agile": "Agile", "ci cd": "CI/CD",
        "microservices": "Microservices", "java": "Java",
        "derivatives pricing": "Derivatives Pricing", "monte carlo": "Monte Carlo",
        "linear algebra": "Linear Algebra", "statistics": "Statistics", "r": "R",
        "product management": "Product Management", "analytics": "Analytics",
        "roadmapping": "Roadmapping", "ux design": "UX Design",
        "aws": "AWS", "azure": "Azure", "gcp": "GCP", "terraform": "Terraform",
        "kubernetes": "Kubernetes", "docker": "Docker", "devops": "DevOps",
        "tensorflow": "TensorFlow", "pytorch": "PyTorch", "deep learning": "Deep Learning",
        "mlops": "MLOps", "data pipeline": "Data Pipeline", "apache spark": "Apache Spark",
        "airflow": "Airflow", "power bi": "Power BI", "data warehouse": "Data Warehouse",
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
