import unittest
from agents.test_generator.generator import TestGenerator

class TestTestGenerator(unittest.TestCase):
    def setUp(self):
        self.generator = TestGenerator()
        self.file_analysis = {
            "file_path": "/app/math_utils.py",
            "file_name": "math_utils.py",
            "classes": [
                {
                    "name": "Calculator",
                    "methods": [
                        {"name": "add"},
                        {"name": "subtract"}
                    ]
                }
            ],
            "functions": [
                {"name": "is_prime"}
            ]
        }
        self.project_analysis = {
            "root_path": "/app",
            "files": [self.file_analysis]
        }

    def test_generate_stubs(self):
        stubs = self.generator.generate_stubs_from_analysis(self.file_analysis)
        self.assertEqual(len(stubs), 2) # TestCalculator and test_is_prime

        calc_stub = next(s for s in stubs if s.name == "TestCalculator")
        self.assertIn("def test_add(self):", calc_stub.content)
        self.assertIn("def test_subtract(self):", calc_stub.content)

        prime_stub = next(s for s in stubs if s.name == "test_is_prime")
        self.assertIn("def test_is_prime():", prime_stub.content)

    def test_detect_missing_coverage(self):
        # By default it should find math_utils missing since we haven't created a test file
        recommendations = self.generator.detect_missing_coverage(self.project_analysis)
        self.assertEqual(len(recommendations), 1)
        self.assertEqual(recommendations[0].module_name, "math_utils")

    def test_generate_runnable_tests(self):
        test_files = self.generator.generate_runnable_tests(self.project_analysis)
        self.assertEqual(len(test_files), 1)
        self.assertEqual(test_files[0].file_path, "/app/tests/test_math_utils.py")
        self.assertIn("import pytest", test_files[0].content)
        self.assertIn("import math_utils", test_files[0].content)

if __name__ == "__main__":
    unittest.main()
