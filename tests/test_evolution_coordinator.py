import unittest
import asyncio
import os
import shutil
from datetime import datetime, timedelta
from agents.evolution_coordinator.coordinator import EvolutionCoordinator
from agents.evolution_coordinator.models import EvolutionStep
from fog.core.state import state_store

class TestEvolutionCoordinator(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.test_dir = "tests/test_evolution_tmp"
        os.makedirs(self.test_dir, exist_ok=True)
        # Clear state for testing
        state_store._state["tasks"] = {}
        state_store._state["backups"] = []

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_monitor_performance(self):
        # Inject mock task data
        state_store.update_task("task1", {"system_name": "AgentA", "status": "completed", "retries": 0})
        state_store.update_task("task2", {"system_name": "AgentA", "status": "failed", "retries": 3})

        coordinator = EvolutionCoordinator()
        metrics = coordinator.monitor_agent_performance()

        self.assertIn("AgentA", metrics)
        self.assertEqual(metrics["AgentA"]["success_rate"], 0.5)
        self.assertEqual(metrics["AgentA"]["avg_retries"], 1.5)

    def test_trigger_improvement_cycle(self):
        # Inject low performing agent data
        state_store.update_task("task1", {"system_name": "BadAgent", "status": "failed", "retries": 3})

        coordinator = EvolutionCoordinator()
        cycle = coordinator.trigger_improvement_cycle()

        self.assertIsNotNone(cycle)
        self.assertEqual(len(cycle.steps), 1)
        self.assertEqual(cycle.steps[0].target_agent, "BadAgent")
        self.assertEqual(cycle.steps[0].improvement_type, "Performance")

    async def test_apply_evolution_step_triggers_backup(self):
        # Create a dummy project file
        project_path = os.path.join(self.test_dir, "my_project")
        os.makedirs(project_path, exist_ok=True)
        with open(os.path.join(project_path, "code.py"), "w") as f:
            f.write("print('hello')")

        step = EvolutionStep(
            step_id="step123",
            target_agent="AgentA",
            improvement_type="Performance",
            description="Speed up AgentA",
            status="Pending"
        )

        coordinator = EvolutionCoordinator()
        await coordinator.apply_evolution_step(step, project_path)

        self.assertEqual(step.status, "Applied")
        self.assertIsNotNone(step.backup_id)

        # Verify backup exists in state
        backups = state_store.get_backups()
        self.assertTrue(any(b["backup_id"] == step.backup_id for b in backups))

if __name__ == "__main__":
    unittest.main()
