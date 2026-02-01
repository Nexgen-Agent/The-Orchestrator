import unittest
import os
import shutil
from agents.code_quality.evaluator import CodeQualityEvaluator

class TestCodeQualityEvaluator(unittest.TestCase):
    def setUp(self):
        self.test_dir = "tests/test_quality_tmp"
        os.makedirs(self.test_dir, exist_ok=True)
        self.test_file = os.path.join(self.test_dir, "test_code.py")

        with open(self.test_file, "w") as f:
            f.write("""
import os
import sys
from datetime import datetime

unused_import = 1

def complex_function(a):
    if a > 0:
        if a > 10:
            if a > 20:
                print("Deep nesting")

    for i in range(a):
        while i < 5:
            i += 1
            if i == 3:
                break
    return a

def risky_function():
    # Missing try/except
    f = open("nonexistent.txt", "r")
    return f.read()

def fine_function():
    try:
        f = open("exists.txt", "r")
    except:
        pass
""")

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_evaluate(self):
        evaluator = CodeQualityEvaluator(self.test_file)
        report = evaluator.evaluate()

        self.assertEqual(report.file_path, self.test_file)
        # sys and datetime are unused
        self.assertIn("sys", report.unused_imports)
        self.assertIn("datetime.datetime", report.unused_imports)

        # complex_function complexity and nesting
        comp_func = next(f for f in report.function_reports if f.name == "complex_function")
        self.assertGreater(comp_func.complexity, 5)
        self.assertGreaterEqual(comp_func.nesting_depth, 3)

        # risky_function missing try/except
        self.assertTrue(any("'open' at line 23" in msg for msg in report.missing_try_except))

        # score should be less than 100
        self.assertLess(report.score, 100)

if __name__ == "__main__":
    unittest.main()
