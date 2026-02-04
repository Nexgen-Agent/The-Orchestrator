import unittest
import asyncio
import os
import json
import shutil
from fog.models.task import TaskPacket, TaskType, TaskStatus
from fog.core.engine import OrchestrationEngine
from fog.core.state import state_store
from fog.core.connector import agent_registry, MockAgentConnector
from fog.core.queue import task_queue
from agents.human_control_interface.control import HumanControlInterface
from agents.human_control_interface.models import ApprovalStatus

class TestHumanControl(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Reset task queue for the new event loop
        task_queue.queue = asyncio.Queue()

        # Reset state
        if os.path.exists("storage/state_test.json"):
            os.remove("storage/state_test.json")
        state_store.storage_path = "storage/state_test.json"
        state_store._state = {"tasks": {}, "agents": {}, "backups": [], "runs": []}
        state_store._save()

        self.hci = HumanControlInterface()
        self.engine = OrchestrationEngine()

        # Register a mock agent
        self.agent_name = "test_agent"
        self.connector = MockAgentConnector(self.agent_name, "http://localhost:8001")
        agent_registry.register_agent(self.connector)
        state_store.add_agent(self.agent_name, {"name": self.agent_name, "endpoint": "http://localhost:8001", "handler_type": "mock"})

    async def asyncTearDown(self):
        if os.path.exists("storage/state_test.json"):
            os.remove("storage/state_test.json")

    async def test_pause_resume(self):
        self.hci.set_pause(True)
        self.assertTrue(self.hci.get_controls()["is_paused"])

        self.hci.set_pause(False)
        self.assertFalse(self.hci.get_controls()["is_paused"])

    async def test_emergency_stop(self):
        self.hci.set_emergency_stop(True)
        self.assertTrue(self.hci.get_controls()["emergency_stop"])

        self.hci.set_emergency_stop(False)
        self.assertFalse(self.hci.get_controls()["emergency_stop"])

    async def test_agent_toggle(self):
        self.hci.toggle_agent(self.agent_name, False)
        self.assertFalse(self.hci.get_agent_toggles()[self.agent_name])

        self.hci.toggle_agent(self.agent_name, True)
        self.assertTrue(self.hci.get_agent_toggles()[self.agent_name])

    async def test_high_risk_task_requires_approval(self):
        task = TaskPacket(
            system_name=self.agent_name,
            module_name="test_module",
            task_type=TaskType.MODIFICATION,
            payload={"project_path": "test_project"} # Added project_path to avoid backup error
        )

        # Ensure dummy project exists for backup
        os.makedirs("test_project", exist_ok=True)

        await self.engine.start(num_workers=1)
        await self.engine.submit_task(task)

        # Wait for the engine to pick it up and request approval
        for _ in range(10):
            await asyncio.sleep(0.5)
            approvals = self.hci.get_pending_approvals()
            if approvals:
                break
        else:
            self.fail("Approval request was not created in time")

        self.assertEqual(len(approvals), 1)
        self.assertEqual(approvals[0].task_id, task.task_id)

        # Task should still be pending
        current_task = state_store.get_task(task.task_id)
        self.assertEqual(current_task["status"], TaskStatus.PENDING)

        # Approve the task
        self.hci.approve_request(approvals[0].request_id, "admin")

        # Wait for engine to process it
        await asyncio.sleep(7) # Re-enqueue delay is 5s

        current_task = state_store.get_task(task.task_id)
        self.assertEqual(current_task["status"], TaskStatus.COMPLETED)

        await self.engine.stop()
        shutil.rmtree("test_project")

    async def test_rejected_task_fails(self):
        task = TaskPacket(
            system_name=self.agent_name,
            module_name="test_module",
            task_type=TaskType.MODIFICATION,
            payload={"project_path": "test_project_rejected"}
        )
        os.makedirs("test_project_rejected", exist_ok=True)

        await self.engine.start(num_workers=1)
        await self.engine.submit_task(task)

        # Wait for the engine to pick it up and request approval
        for _ in range(10):
            await asyncio.sleep(0.5)
            approvals = self.hci.get_pending_approvals()
            if approvals:
                break
        else:
            self.fail("Approval request was not created in time")

        self.hci.reject_request(approvals[0].request_id, "admin")

        await asyncio.sleep(7)

        current_task = state_store.get_task(task.task_id)
        self.assertEqual(current_task["status"], TaskStatus.FAILED)
        self.assertIn("rejected", current_task["result"]["error"])

        await self.engine.stop()
        shutil.rmtree("test_project_rejected")

if __name__ == "__main__":
    unittest.main()
