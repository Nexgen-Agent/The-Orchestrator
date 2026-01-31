import unittest
import os
import shutil
from fog.core.mapper import DependencyMapper

class TestDependencyMapper(unittest.TestCase):
    def setUp(self):
        self.project_path = "tests/test_mapper_project"
        os.makedirs(self.project_path, exist_ok=True)

        # Create a small package structure
        os.makedirs(os.path.join(self.project_path, "pkg"), exist_ok=True)
        with open(os.path.join(self.project_path, "__init__.py"), "w") as f:
            pass
        with open(os.path.join(self.project_path, "main.py"), "w") as f:
            f.write("from test_mapper_project.pkg import sub\nimport os")
        with open(os.path.join(self.project_path, "pkg", "__init__.py"), "w") as f:
            pass
        with open(os.path.join(self.project_path, "pkg", "sub.py"), "w") as f:
            f.write("x = 1")

    def tearDown(self):
        if os.path.exists(self.project_path):
            shutil.rmtree(self.project_path)

    def test_scan_project(self):
        mapper = DependencyMapper()
        graph = mapper.scan_project(self.project_path)

        # Project name is test_mapper_project
        self.assertIn("test_mapper_project.main", graph)
        self.assertIn("test_mapper_project.pkg.sub", graph)

        main_info = graph["test_mapper_project.main"]
        self.assertIn("test_mapper_project.pkg", main_info["imports"])

if __name__ == "__main__":
    unittest.main()
