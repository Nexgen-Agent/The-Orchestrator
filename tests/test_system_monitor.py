import unittest
from agents.system_monitor.monitor import SystemMonitor

class MockStateStore:
    def get_state(self):
        return {
            "tasks": {
                "1": {"system_name": "AgentA", "status": "completed", "retries": 0},
                "2": {"system_name": "AgentA", "status": "failed", "retries": 3},
                "3": {"system_name": "AgentA", "status": "failed", "retries": 3},
                "4": {"system_name": "AgentA", "status": "failed", "retries": 3},
                "5": {"system_name": "AgentA", "status": "failed", "retries": 3},
                "6": {"system_name": "AgentB", "status": "completed", "retries": 1}
            },
            "agents": {
                "AgentA": {},
                "AgentB": {}
            }
        }

class TestSystemMonitor(unittest.TestCase):
    def setUp(self):
        self.state_store = MockStateStore()
        self.monitor = SystemMonitor(self.state_store)

    def test_get_health_report(self):
        report = self.monitor.get_health_report()

        self.assertEqual(len(report.agents), 2)
        self.assertEqual(report.overall_task_metrics.total_tasks, 6)
        # 2 completed, 4 failed. success_rate = 2/6 = 0.33
        self.assertLess(report.overall_task_metrics.success_rate, 0.4)

        # Pattern detection
        self.assertTrue(any("AgentA" in p.description for p in report.detected_patterns))

        # Overall status should be Critical due to low success rate
        self.assertEqual(report.system_status, "Critical")

if __name__ == "__main__":
    unittest.main()
