import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import database


class DatabaseSchemaSetupTests(unittest.TestCase):
    def test_schema_setup_statements_create_a_custom_schema(self) -> None:
        statements = database.get_schema_setup_statements()
        self.assertEqual(statements[0], 'CREATE SCHEMA IF NOT EXISTS "skillbridge_schema"')


if __name__ == "__main__":
    unittest.main()
