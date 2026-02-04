import unittest
import os
import json
from agents.learning_feedback.feedback import LearningFeedbackAgent
from fog.core.state import state_store

class TestLearningFeedback(unittest.TestCase):
    def setUp(self):
        # Reset state
        if os.path.exists("storage/state_learning_test.json"):
            os.remove("storage/state_learning_test.json")
        if os.path.exists("storage/memory_test.json"):
            os.remove("storage/memory_test.json")
        if os.path.exists("storage/evals_test.json"):
            os.remove("storage/evals_test.json")

        state_store.storage_path = "storage/state_learning_test.json"
        state_store._state = {
            "tasks": {},
            "agents": {},
            "backups": [],
            "runs": []
        }
        state_store._save()

        # Create some mock evaluations
        self.evals_path = "storage/evals_test.json"
        self.mock_evals = [
            {
                "agent_name": "slow_agent",
                "metrics": {
                    "avg_execution_time": 15.5,
                    "success_rate": 0.95
                }
            },
            {
                "agent_name": "failing_agent",
                "metrics": {
                    "avg_execution_time": 2.0,
                    "success_rate": 0.4,
                    "failure_patterns": ["Timeout error", "Connection refused"]
                }
            }
        ]
        with open(self.evals_path, 'w') as f:
            json.dump(self.mock_evals, f)

        self.agent = LearningFeedbackAgent(memory_path="storage/memory_test.json", evaluations_path=self.evals_path)

    def tearDown(self):
        if os.path.exists("storage/state_learning_test.json"):
            os.remove("storage/state_learning_test.json")
        if os.path.exists("storage/memory_test.json"):
            os.remove("storage/memory_test.json")
        if os.path.exists("storage/evals_test.json"):
            os.remove("storage/evals_test.json")

    def test_analyze_performance(self):
        report = self.agent.analyze_performance()

        # Verify latency insight for slow_agent
        latency_insights = [i for i in report.insights if i.category == "latency"]
        self.assertTrue(any("slow_agent" in i.description for i in latency_insights))

        # Verify failure insight for failing_agent
        failure_insights = [i for i in report.insights if i.category == "failure_pattern"]
        self.assertTrue(any("failing_agent" in i.description for i in failure_insights))

        # Verify suggestions
        self.assertTrue(any("timeout" in s.suggested_update.lower() for s in report.suggestions))
        self.assertTrue(any("route complex tasks away" in s.suggested_update.lower() for s in report.suggestions))

        # Verify memory update
        self.assertTrue(len(self.agent.memory.insights) > 0)

    def test_feed_to_evolution(self):
        report = self.agent.analyze_performance()
        self.agent.feed_to_evolution_coordinator(report)

        state = state_store.get_state()
        self.assertIn("evolution_proposals", state)
        self.assertEqual(len(state["evolution_proposals"]), len(report.suggestions))

if __name__ == "__main__":
    unittest.main()
