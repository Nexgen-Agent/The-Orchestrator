import unittest
import os
import shutil
from agents.deployment_preparer.preparer import DeploymentPreparer

class TestDeploymentPreparer(unittest.TestCase):
    def setUp(self):
        self.test_dir = "tests/test_deployment_tmp"
        os.makedirs(self.test_dir, exist_ok=True)

        with open(os.path.join(self.test_dir, "app.py"), "w") as f:
            f.write("import fastapi\nimport pydantic\nprint('hello')")

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_prepare(self):
        preparer = DeploymentPreparer(self.test_dir)
        report = preparer.prepare()

        self.assertEqual(report.status, "Success")
        self.assertIn("fastapi", report.generated_package.requirements_content)
        self.assertIn("pydantic", report.generated_package.requirements_content)
        self.assertIn("FROM python", report.generated_package.dockerfile_content)
        self.assertIn("python3", report.generated_package.startup_script_content)

    def test_detect_missing(self):
        # Create requirements.txt with one missing
        with open(os.path.join(self.test_dir, "requirements.txt"), "w") as f:
            f.write("fastapi")

        preparer = DeploymentPreparer(self.test_dir)
        report = preparer.prepare()

        self.assertEqual(report.status, "Warning")
        missing_mods = [m.module for m in report.missing_dependencies]
        self.assertIn("pydantic", missing_mods)

if __name__ == "__main__":
    unittest.main()
