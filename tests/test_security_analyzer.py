import unittest
import os
import shutil
from agents.security_analyzer.analyzer import SecurityAnalyzer
from agents.security_analyzer.models import RiskSeverity

class TestSecurityAnalyzer(unittest.TestCase):
    def setUp(self):
        self.test_dir = "tests/test_security_tmp"
        os.makedirs(self.test_dir, exist_ok=True)
        self.test_file = os.path.join(self.test_dir, "vulnerable_code.py")

        with open(self.test_file, "w") as f:
            f.write("""
import os
import pickle
import yaml

# Hardcoded secret
AWS_KEY = "AKIA1234567890EXAMPLE"

def run_cmd(cmd):
    # Unsafe command execution
    os.system(cmd)

def load_data(data):
    # Unsafe deserialization
    return pickle.loads(data)

def unsafe_eval(expr):
    return eval(expr)

def safe_yaml(stream):
    # Safe YAML loading
    return yaml.load(stream, Loader=yaml.SafeLoader)

def unsafe_yaml(stream):
    # Unsafe YAML loading
    return yaml.load(stream)
""")

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_scan_file(self):
        analyzer = SecurityAnalyzer()
        report = analyzer.scan_file(self.test_file)

        # Check overall risk
        self.assertEqual(report.overall_risk_level, RiskSeverity.CRITICAL)

        # Check secret detection
        self.assertTrue(any(r.category == "Hardcoded Secret" for r in report.risks_detected))

        # Check unsafe patterns
        pattern_names = [p.pattern_name for p in report.unsafe_patterns]
        self.assertIn("os.system", pattern_names)
        self.assertIn("pickle.loads", pattern_names)
        self.assertIn("eval", pattern_names)
        self.assertIn("yaml.load", pattern_names)

        # Check risky dependencies
        self.assertIn("pickle", report.risky_dependencies)

if __name__ == "__main__":
    unittest.main()
