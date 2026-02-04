import unittest
import asyncio
import os
import shutil
from agents.software_builder.builder import SoftwareBuilder
from agents.software_builder.models import BuildRequest
from agents.debugger.debugger import Debugger
from agents.debugger.models import DebugRequest

class TestSoftwareBuilder(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.project_path = "tests/builder_test_project"
        os.makedirs(self.project_path, exist_ok=True)
        with open(os.path.join(self.project_path, "a.py"), "w") as f:
            f.write("import b\ndef a(): pass")
        with open(os.path.join(self.project_path, "b.py"), "w") as f:
            f.write("def b(): pass")

    async def asyncTearDown(self):
        if os.path.exists(self.project_path):
            shutil.rmtree(self.project_path)

    async def test_build_order(self):
        builder = SoftwareBuilder(self.project_path)
        dep_map = builder.mapper.scan_project(self.project_path)
        order = builder._get_build_order(dep_map)

        # 'b' should be in a level before 'a'
        b_level = -1
        a_level = -1
        for i, level in enumerate(order):
            if "b" in level: b_level = i
            if "a" in level: a_level = i

        self.assertLess(b_level, a_level)

    async def test_run_build(self):
        builder = SoftwareBuilder(self.project_path)
        request = BuildRequest(project_path=self.project_path, max_iterations=2)
        report = await builder.run_build(request)
        self.assertEqual(report.status, "Completed")
        self.assertEqual(len(report.modules), 2)
        self.assertEqual(report.modules["a"].total_iterations, 2)

class TestDebugger(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.project_path = "tests/debugger_test_project"
        os.makedirs(self.project_path, exist_ok=True)
        with open(os.path.join(self.project_path, "unsafe.py"), "w") as f:
            f.write("def fail():\n    eval('1+1')\n    return 0")
        with open(os.path.join(self.project_path, "broken.py"), "w") as f:
            f.write("def syntax_error():\n    return 1 +")

    async def asyncTearDown(self):
        if os.path.exists(self.project_path):
            shutil.rmtree(self.project_path)

    async def test_static_analysis(self):
        debugger = Debugger(self.project_path)
        request = DebugRequest(project_path=self.project_path, auto_fix=False)
        report = await debugger.run_debug(request)

        issue_types = [i.issue_type for i in report.issues]
        self.assertIn("Syntax", issue_types)
        self.assertIn("SafePattern", issue_types)

    async def test_auto_fix(self):
        debugger = Debugger(self.project_path)
        request = DebugRequest(project_path=self.project_path, auto_fix=True, validation_rounds=2)
        report = await debugger.run_debug(request)

        self.assertTrue(len(report.proposed_fixes) > 0)
        self.assertTrue(report.validation_passes > 0)

if __name__ == "__main__":
    unittest.main()
