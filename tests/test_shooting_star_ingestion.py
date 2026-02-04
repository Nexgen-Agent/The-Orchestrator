import unittest
import asyncio
import os
import shutil
from agents.shooting_star_ingestion.ingestion import ShootingStarIngestion
from fog.core.state import state_store

class TestShootingStarIngestion(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Reset state
        if os.path.exists("storage/state_ingestion_test.json"):
            os.remove("storage/state_ingestion_test.json")
        state_store.storage_path = "storage/state_ingestion_test.json"
        state_store._state = {
            "tasks": {},
            "agents": {},
            "backups": [],
            "runs": []
        }
        state_store._save()

        # Create a dummy project
        self.test_project = "tests/ingestion_test_project"
        os.makedirs(self.test_project, exist_ok=True)
        with open(os.path.join(self.test_project, "main.py"), "w") as f:
            f.write("def hello():\n    print('Hello world')\n\nif __name__ == '__main__':\n    hello()")
        with open(os.path.join(self.test_project, "logic.py"), "w") as f:
            f.write("def process(data):\n    if data > 10:\n        return True\n    return False")

    async def asyncTearDown(self):
        if os.path.exists("storage/state_ingestion_test.json"):
            os.remove("storage/state_ingestion_test.json")
        if os.path.exists(self.test_project):
            shutil.rmtree(self.test_project)

    async def test_ingest(self):
        ingestion = ShootingStarIngestion(self.test_project)
        report = await ingestion.ingest()

        self.assertEqual(report.status, "Completed")
        self.assertEqual(len(report.modules), 2)

        module_paths = [m.file_path for m in report.modules]
        self.assertTrue(any("main.py" in p for p in module_paths))
        self.assertTrue(any("logic.py" in p for p in module_paths))

        # Check if summaries and tags exist (mock connectors will provide some output)
        for module in report.modules:
            self.assertIsNotNone(module.summary)
            self.assertIsNotNone(module.structure)

        self.assertIsNotNone(report.dependency_map)
        self.assertIsNotNone(report.build_instructions)
        self.assertIn("modules", report.architecture_summary)

if __name__ == "__main__":
    unittest.main()
