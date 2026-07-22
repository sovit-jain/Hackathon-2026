import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.routes.learning import build_learning_path_name, build_role_lesson_plan, get_lesson_lock_state, get_lesson_level_for_score
from app.routes.progress import get_priority_badge
from app.utils.scoring import get_next_focus_skill


class LearningPathTests(unittest.TestCase):
    def test_beginner_path_name_for_low_score(self) -> None:
        self.assertEqual(build_learning_path_name(20, "data-analyst"), "Beginner Data Analyst Path")

    def test_standard_path_name_for_mid_score(self) -> None:
        self.assertEqual(build_learning_path_name(55, "product-manager"), "Standard Product Manager Path")

    def test_advanced_path_name_for_high_score(self) -> None:
        self.assertEqual(build_learning_path_name(85, "data-analyst"), "Advanced Data Analyst Path")

    def test_role_specific_lessons_for_tech_support(self) -> None:
        lessons = build_role_lesson_plan("tech-support", "beginner")
        self.assertGreaterEqual(len(lessons), 3)
        self.assertEqual(lessons[0]["title"], "Excel Essentials for Support")

    def test_score_maps_to_beginner_difficulty(self) -> None:
        self.assertEqual(get_lesson_level_for_score(38), "beginner")
        self.assertEqual(get_lesson_level_for_score(55), "intermediate")
        self.assertEqual(get_lesson_level_for_score(75), "advanced")

    def test_priority_badge_is_score_driven(self) -> None:
        self.assertEqual(get_priority_badge(20), "HIGH")
        self.assertEqual(get_priority_badge(38), "MEDIUM")
        self.assertEqual(get_priority_badge(75), "LOW")

    def test_first_lesson_is_ready_and_following_lessons_lock(self) -> None:
        self.assertEqual(get_lesson_lock_state(1, []), "ready")
        self.assertEqual(get_lesson_lock_state(2, []), "locked")
        self.assertEqual(get_lesson_lock_state(2, [1]), "ready")

    def test_next_focus_skill_uses_role_specific_requirements(self) -> None:
        self.assertEqual(get_next_focus_skill("data-analyst", ["python"], 60), "SQL")
        self.assertEqual(get_next_focus_skill("tech-support", ["excel"], 20), "Support")

    def test_role_lesson_plan_is_strictly_level_filtered(self) -> None:
        beginner_lessons = build_role_lesson_plan("python-developer", "beginner")
        intermediate_lessons = build_role_lesson_plan("python-developer", "intermediate")
        advanced_lessons = build_role_lesson_plan("python-developer", "advanced")

        self.assertEqual(len(beginner_lessons), 5)
        self.assertEqual(len(intermediate_lessons), 5)
        self.assertEqual(len(advanced_lessons), 5)
        self.assertTrue(all(lesson["level"] == "beginner" for lesson in beginner_lessons))
        self.assertTrue(all(lesson["level"] == "intermediate" for lesson in intermediate_lessons))
        self.assertTrue(all(lesson["level"] == "advanced" for lesson in advanced_lessons))


if __name__ == "__main__":
    unittest.main()
