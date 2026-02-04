import unittest
import asyncio
import os
from agents.system_resilience.resilience import ResilienceManager
from agents.system_resilience.models import ResilienceActionType
from fog.core.state import state_store
from fog.models.task import TaskStatus

class TestSystemResilience(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Reset state
        if os.path.exists("storage/state_resilience_test.json"):
            os.remove("storage/state_resilience_test.json")
        state_store.storage_path = "storage/state_resilience_test.json"
        state_store._state = {
            "tasks": {},
            "agents": {},
            "backups": [],
            "runs": [],
            "resilience_actions": [],
            "safe_mode": False
        }
        state_store._save()
        self.resilience = ResilienceManager()

    async def asyncTearDown(self):
        if os.path.exists("storage/state_resilience_test.json"):
            os.remove("storage/state_resilience_test.json")

    async def test_detect_and_recover_task(self):
        # Add a failed task that looks like a timeout
        state_store._state["tasks"]["t1"] = {
            "task_id": "t1",
            "system_name": "agent1",
            "module_name": "mod1",
            "task_type": "analysis",
            "status": "failed",
            "result": {"error": "Task timed out"}
        }
        state_store._save()

        report = await self.resilience.detect_and_fix()

        self.assertEqual(report.recovered_tasks_count, 1)
        self.assertEqual(len(report.actions_taken), 1)
        self.assertEqual(report.actions_taken[0].action_type, ResilienceActionType.RECOVER_TASK)

        history = self.resilience.get_resilience_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0].target, "t1")

    async def test_detect_unhealthy_agent(self):
        # Add multiple failures for one agent
        for i in range(6):
            state_store._state["tasks"][f"t{i}"] = {
                "task_id": f"t{i}",
                "system_name": "unstable_agent",
                "status": "failed",
                "result": {"error": "Internal error"}
            }
        state_store._save()

        report = await self.resilience.detect_and_fix()

        self.assertTrue(any("unstable_agent" in p for p in report.failing_patterns))
        self.assertTrue(any(a.action_type == ResilienceActionType.RESTART_AGENT and a.target == "unstable_agent" for a in report.actions_taken))

    async def test_trigger_safe_mode(self):
        # Add multiple patterns of failure
        for agent in ["a1", "a2", "a3"]:
            for i in range(6):
                state_store._state["tasks"][f"{agent}_t{i}"] = {
                    "task_id": f"{agent}_t{i}",
                    "system_name": agent,
                    "status": "failed",
                    "result": {"error": "Boom"}
                }
        state_store._save()

        report = await self.resilience.detect_and_fix()

        self.assertTrue(report.safe_mode_active)
        self.assertEqual(report.system_status, "Critical")
        self.assertTrue(state_store.get_state().get("safe_mode"))

if __name__ == "__main__":
    unittest.main()
