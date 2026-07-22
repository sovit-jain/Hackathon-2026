import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import database


class DatabaseConfigTests(unittest.TestCase):
    def test_database_url_is_loaded_from_env_and_normalized_for_postgres(self) -> None:
        self.assertTrue(database.DATABASE_URL.startswith("postgresql://"), database.DATABASE_URL)
        self.assertNotIn("DATABASE_URL=", database.DATABASE_URL)
        self.assertIn("localhost", database.DATABASE_URL)


if __name__ == "__main__":
    unittest.main()
