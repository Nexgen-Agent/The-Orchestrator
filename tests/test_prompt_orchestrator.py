import unittest
from agents.prompt_orchestrator.orchestrator import PromptOrchestrator

class TestPromptOrchestrator(unittest.TestCase):
    def setUp(self):
        self.orchestrator = PromptOrchestrator()
        self.architecture_map = {
            "project_name": "TestSystem",
            "adjacency_list": {
                "main": ["core", "utils"],
                "core": ["database"],
                "utils": [],
                "database": []
            }
        }

    def test_topology_sort(self):
        order = self.orchestrator.topology_sort(self.architecture_map["adjacency_list"])
        # Potential valid orders: [database, core, utils, main] or [utils, database, core, main]
        self.assertEqual(order[-1], "main")
        self.assertLess(order.index("database"), order.index("core"))
        self.assertLess(order.index("core"), order.index("main"))
        self.assertLess(order.index("utils"), order.index("main"))

    def test_orchestrate(self):
        output = self.orchestrator.orchestrate(self.architecture_map)
        self.assertEqual(output.project_name, "TestSystem")
        self.assertEqual(len(output.ordered_prompts), 1)
        self.assertEqual(len(output.ordered_prompts[0].instructions), 4)

        # Check that main is the last instruction
        self.assertEqual(output.ordered_prompts[0].instructions[-1].component_name, "main")

if __name__ == "__main__":
    unittest.main()
