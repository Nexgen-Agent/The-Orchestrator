import unittest
import os
import json
from agents.meta_evolution.analyzer import MetaEvolutionAnalyzer
from fog.core.state import state_store

class TestMetaEvolution(unittest.TestCase):
    def setUp(self):
        # Reset state
        if os.path.exists("storage/state_meta_test.json"):
            os.remove("storage/state_meta_test.json")
        state_store.storage_path = "storage/state_meta_test.json"
        state_store._state = {
            "tasks": {},
            "agents": {"agent1": {}, "agent2": {}},
            "backups": [],
            "runs": [],
            "ecosystem_snapshots": []
        }
        state_store._save()
        self.analyzer = MetaEvolutionAnalyzer()

    def tearDown(self):
        if os.path.exists("storage/state_meta_test.json"):
            os.remove("storage/state_meta_test.json")

    def test_take_snapshot(self):
        # Add some tasks
        state_store._state["tasks"] = {
            "t1": {"system_name": "agent1", "status": "completed"},
            "t2": {"system_name": "agent1", "status": "completed"},
            "t3": {"system_name": "agent2", "status": "failed"}
        }
        state_store._save()

        snapshot = self.analyzer.take_snapshot()
        self.assertEqual(snapshot.num_agents, 2)
        self.assertEqual(snapshot.num_tasks, 3)
        self.assertEqual(snapshot.agent_distribution["agent1"], 2)
        self.assertEqual(snapshot.agent_distribution["agent2"], 1)
        self.assertAlmostEqual(snapshot.total_success_rate, 2/3)

    def test_analyze_trends(self):
        # Create two snapshots manually
        state_store._state["ecosystem_snapshots"] = [
            {
                "snapshot_id": "s1",
                "timestamp": "2026-01-01T00:00:00",
                "num_agents": 2,
                "num_tasks": 10,
                "agent_distribution": {"a1": 5, "a2": 5},
                "total_success_rate": 0.8
            },
            {
                "snapshot_id": "s2",
                "timestamp": "2026-01-02T00:00:00",
                "num_agents": 3,
                "num_tasks": 20,
                "agent_distribution": {"a1": 10, "a2": 5, "a3": 5},
                "total_success_rate": 0.85
            }
        ]
        state_store._save()

        trends = self.analyzer.analyze_trends()
        self.assertEqual(len(trends), 2)

        task_trend = next(t for t in trends if t.metric == "Task Volume")
        self.assertEqual(task_trend.growth_rate, 1.0) # 10 to 20 is 100% growth
        self.assertEqual(task_trend.trend_direction, "Increasing")

        agent_trend = next(t for t in trends if t.metric == "Agent Count")
        self.assertEqual(agent_trend.growth_rate, 1.0) # 2 to 3 is +1 change
        self.assertEqual(agent_trend.trend_direction, "Increasing")

    def test_propose_evolution(self):
        # Case 1: High volume agent (Split)
        state_store._state["tasks"] = {f"t{i}": {"system_name": "busy_agent", "status": "completed"} for i in range(120)}
        state_store._save()

        strategy = self.analyzer.propose_evolution()
        split_suggestions = [s for s in strategy.agent_changes if s.suggestion_type == "Split"]
        self.assertTrue(any(s.target_agents == ["busy_agent"] for s in split_suggestions))
        self.assertTrue(any(u.title == "Implement Task Caching Layer" for u in strategy.upgrades))

        # Case 2: Low volume agent (Merge)
        state_store._state["tasks"]["t_rare"] = {"system_name": "lazy_agent", "status": "completed"}
        # Ensure we have enough total tasks for the merge logic to trigger (count < 2 and total > 20)
        state_store._save()

        strategy = self.analyzer.propose_evolution()
        merge_suggestions = [s for s in strategy.agent_changes if s.suggestion_type == "Merge"]
        self.assertTrue(any(s.target_agents == ["lazy_agent"] for s in merge_suggestions))

if __name__ == "__main__":
    unittest.main()
