from .jwt_handler import create_access_token, verify_token
from .scoring import calculate_assessment_score, calculate_job_match, calculate_risk, get_level_from_score

try:
    from .llm import generate_chat_reply, generate_intervention
except Exception:  # pragma: no cover - optional dependency may be unavailable in tests
    generate_chat_reply = None
    generate_intervention = None

__all__ = [
    "create_access_token",
    "verify_token",
    "generate_chat_reply",
    "generate_intervention",
    "calculate_assessment_score",
    "calculate_job_match",
    "calculate_risk",
    "get_level_from_score",
]
