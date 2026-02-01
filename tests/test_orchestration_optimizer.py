import unittest
import os
import json
import shutil
from datetime import datetime, timedelta
from agents.orchestration_optimizer.optimizer import OrchestrationOptimizer

class TestOrchestrationOptimizer(unittest.TestCase):
    def setUp(self):
        self.test_dir = "tests/test_optimizer_tmp"
        os.makedirs(self.test_dir, exist_ok=True)
        self.log_file = os.path.join(self.test_dir, "audit.log")

        # Generate mock logs
        t1 = datetime.now() - timedelta(minutes=10)
        t2 = t1 + timedelta(seconds=5)
        t3 = t2 + timedelta(seconds=1)

        logs = [
            {"timestamp": t1.isoformat(), "event": "PROCESSING_TASK", "data": {"task_id": "task1", "agent": "SlowAgent"}},
            {"timestamp": (t1 + timedelta(seconds=20)).isoformat(), "event": "TASK_FINISHED", "data": {"task_id": "task1", "status": "completed"}},

            {"timestamp": t2.isoformat(), "event": "PROCESSING_TASK", "data": {"task_id": "task2", "agent": "FastAgent"}},
            {"timestamp": (t2 + timedelta(seconds=1)).isoformat(), "event": "TASK_FINISHED", "data": {"task_id": "task2", "status": "completed"}},

            {"timestamp": t3.isoformat(), "event": "PROCESSING_TASK", "data": {"task_id": "task3", "agent": "FailingAgent"}},
            {"timestamp": (t3 + timedelta(seconds=1)).isoformat(), "event": "TASK_MAX_RETRIES_REACHED", "data": {"task_id": "task3", "error": "Connection Timeout"}},

            # More tasks to trigger suggestions
            {"timestamp": t3.isoformat(), "event": "PROCESSING_TASK", "data": {"task_id": "task4", "agent": "FailingAgent"}},
            {"timestamp": (t3 + timedelta(seconds=1)).isoformat(), "event": "TASK_MAX_RETRIES_REACHED", "data": {"task_id": "task4", "error": "Connection Timeout"}},
            {"timestamp": t3.isoformat(), "event": "PROCESSING_TASK", "data": {"task_id": "task5", "agent": "FailingAgent"}},
            {"timestamp": (t3 + timedelta(seconds=1)).isoformat(), "event": "TASK_MAX_RETRIES_REACHED", "data": {"task_id": "task5", "error": "Connection Timeout"}},
        ]

        with open(self.log_file, "w") as f:
            for log in logs:
                f.write(json.dumps(log) + "\n")

        self.optimizer = OrchestrationOptimizer(self.log_file)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_analyze(self):
        report = self.optimizer.analyze()

        # Check agent performance
        agents = {a.agent_name: a for a in report.agent_performance}
        self.assertIn("SlowAgent", agents)
        self.assertEqual(agents["SlowAgent"].avg_execution_time_seconds, 20.0)
        self.assertEqual(agents["FastAgent"].avg_execution_time_seconds, 1.0)
        self.assertEqual(agents["FailingAgent"].success_rate, 0.0)

        # Check failure patterns
        self.assertTrue(any(p.error_type == "Connection Timeout" for p in report.failure_patterns))

        # Check suggestions
        suggestion_types = [s.type for s in report.suggestions]
        self.assertIn("Agent", suggestion_types) # SlowAgent should be flagged
        self.assertIn("Retries", suggestion_types) # FailingAgent should be flagged

if __name__ == "__main__":
    unittest.main()
