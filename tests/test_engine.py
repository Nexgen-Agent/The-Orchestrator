import unittest
import asyncio
from fog.core.engine import OrchestrationEngine
from fog.models.task import TaskPacket, TaskType, TaskStatus
from fog.core.connector import agent_registry, MockAgentConnector

class TestOrchestrationEngine(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.engine = OrchestrationEngine()
        self.agent = MockAgentConnector("TestAgent", "http://test")
        agent_registry.register_agent(self.agent)
        await self.engine.start(num_workers=1)

    async def asyncTearDown(self):
        await self.engine.stop()

    async def test_submit_and_process_task(self):
        task = TaskPacket(
            system_name="TestAgent",
            module_name="test_mod",
            task_type=TaskType.ANALYSIS,
            payload={}
        )

        # We need to run the engine's worker in the background for this test
        # Actually engine.start() already did that.

        await self.engine.submit_task(task)

        # Wait for task to be processed (increased timeout and polling)
        completed = False
        for _ in range(20):
            await asyncio.sleep(0.5)
            from fog.core.state import state_store
            updated_task = state_store.get_task(task.task_id)
            if updated_task and updated_task["status"] == TaskStatus.COMPLETED:
                completed = True
                break

        self.assertTrue(completed, "Task did not complete in time")
        updated_task = state_store.get_task(task.task_id)
        self.assertEqual(updated_task["status"], TaskStatus.COMPLETED)

if __name__ == "__main__":
    unittest.main()
