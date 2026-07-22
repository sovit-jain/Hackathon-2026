from typing import Optional, Sequence, Tuple

DEFAULT_ROLE = "data-analyst"
DEFAULT_LEVEL = "beginner"
SUPPORTED_LEVELS = {"beginner", "intermediate", "advanced"}
SUPPORTED_ROLES = {
    "data-analyst",
    "business-analyst",
    "python-developer",
    "data-engineer",
    "ml-engineer",
    "tech-support",
}


def resolve_lesson_context(target_role: Optional[str], current_level: Optional[str]) -> Tuple[str, str]:
    normalized_role = (target_role or "").strip().lower().replace(" ", "-")
    if normalized_role not in SUPPORTED_ROLES:
        normalized_role = DEFAULT_ROLE

    normalized_level = (current_level or "").strip().lower()
    if normalized_level not in SUPPORTED_LEVELS:
        normalized_level = DEFAULT_LEVEL

    return normalized_role, normalized_level


def get_lesson_level_for_score(score: Optional[int]) -> str:
    if score is None:
        return DEFAULT_LEVEL
    if score >= 70:
        return "advanced"
    if score >= 40:
        return "intermediate"
    return "beginner"


def get_lesson_levels_for_path(resolved_level: str) -> list[str]:
    if resolved_level == "beginner":
        return ["beginner", "intermediate"]
    if resolved_level == "intermediate":
        return ["intermediate", "advanced"]
    return ["advanced"]


def get_lesson_lock_state(lesson_order: int, completed_lesson_orders: Optional[Sequence[int]]) -> str:
    if lesson_order == 1:
        return "ready"

    completed_orders = set(completed_lesson_orders or [])
    for previous_order in range(1, lesson_order):
        if previous_order not in completed_orders:
            return "locked"
    return "ready"
