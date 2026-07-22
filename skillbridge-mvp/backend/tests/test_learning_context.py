import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.utils.lesson_context import resolve_lesson_context


class ResolveLessonContextTests(unittest.TestCase):
    def test_returns_defaults_for_missing_profile(self) -> None:
        self.assertEqual(resolve_lesson_context(None, None), ("data-analyst", "beginner"))

    def test_returns_defaults_for_unseeded_role(self) -> None:
        self.assertEqual(resolve_lesson_context("product-manager", "beginner"), ("data-analyst", "beginner"))

    def test_keeps_supported_profile_values(self) -> None:
        self.assertEqual(resolve_lesson_context("data-analyst", "intermediate"), ("data-analyst", "intermediate"))


if __name__ == "__main__":
    unittest.main()
