import unittest
import asyncio
import os
from agents.deployment_automation.automation import DeploymentAutomation
from agents.deployment_automation.models import DeploymentStatus
from fog.core.state import state_store

class TestDeploymentAutomation(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Reset state
        if os.path.exists("storage/state_deploy_test.json"):
            os.remove("storage/state_deploy_test.json")
        state_store.storage_path = "storage/state_deploy_test.json"
        state_store._state = {
            "tasks": {},
            "agents": {},
            "backups": [],
            "runs": [],
            "deployments": {}
        }
        state_store._save()
        self.automation = DeploymentAutomation("test_project")

    async def asyncTearDown(self):
        if os.path.exists("storage/state_deploy_test.json"):
            os.remove("storage/state_deploy_test.json")

    async def test_run_deployment(self):
        manifest = self.automation.generate_manifest("test-service", "v1")
        report = await self.automation.run_deployment(manifest)

        self.assertEqual(report.status, DeploymentStatus.SUCCESS)
        self.assertEqual(len(report.actions), 3) # build, push, deploy
        self.assertEqual(report.actions[0].action_type, "build")

        state = state_store.get_state()
        self.assertIn(report.deployment_id, state["deployments"])

    async def test_rollback(self):
        manifest = self.automation.generate_manifest("test-service", "v1")
        report = await self.automation.run_deployment(manifest)

        rollback_report = await self.automation.rollback(report.deployment_id)
        self.assertEqual(rollback_report.status, DeploymentStatus.ROLLED_BACK)
        self.assertEqual(len(rollback_report.actions), 4) # 3 deploy + 1 rollback

if __name__ == "__main__":
    unittest.main()
