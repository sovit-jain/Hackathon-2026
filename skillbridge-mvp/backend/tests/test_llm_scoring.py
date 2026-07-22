import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.utils.llm_scoring import build_skill_assessment_context
from app.utils.llm import build_curated_lesson_content


def test_build_skill_assessment_context_groups_selected_skills() -> None:
    context = build_skill_assessment_context([], "data-analyst", ["Hindi", "Microsoft Excel", "Python"], "unemployed")

    assert context["employment_status"] == "unemployed"
    assert context["selected_skills"] == ["Hindi", "Microsoft Excel", "Python"]

    categories = {item["category"]: item["skills"] for item in context["skill_categories"]}
    assert categories["Language & communication"] == ["Hindi"]
    assert categories["Office & productivity"] == ["Microsoft Excel"]
    assert categories["Technical skills"] == ["Python"]


def test_curated_lesson_content_is_level_aware() -> None:
    beginner_content = build_curated_lesson_content("Alex", "python-developer", "beginner", "Python Fundamentals", "Learn python basics")
    advanced_content = build_curated_lesson_content("Alex", "python-developer", "advanced", "Python Fundamentals", "Learn python basics")

    assert "foundation" in beginner_content.lower()
    assert "advanced" in advanced_content.lower() or "strategic" in advanced_content.lower()
