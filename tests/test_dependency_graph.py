import unittest
import json
from agents.dependency_graph.graph import DependencyGraphAgent

class TestDependencyGraphAgent(unittest.TestCase):
    def setUp(self):
        self.analyzer_output = {
            "root_path": "/app",
            "files": [
                {
                    "file_path": "/app/main.py",
                    "file_name": "main.py",
                    "total_lines": 10,
                    "classes": [],
                    "functions": [],
                    "imports": [
                        {"module": "utils", "names": ["foo"], "is_internal": True, "line_number": 1}
                    ]
                },
                {
                    "file_path": "/app/utils.py",
                    "file_name": "utils.py",
                    "total_lines": 5,
                    "classes": [],
                    "functions": [],
                    "imports": [
                        {"module": "core", "names": ["bar"], "is_internal": True, "line_number": 1}
                    ]
                },
                {
                    "file_path": "/app/core.py",
                    "file_name": "core.py",
                    "total_lines": 5,
                    "classes": [],
                    "functions": [],
                    "imports": [
                        {"module": "utils", "names": ["baz"], "is_internal": True, "line_number": 1}
                    ]
                },
                {
                    "file_path": "/app/leaf.py",
                    "file_name": "leaf.py",
                    "total_lines": 5,
                    "classes": [],
                    "functions": [],
                    "imports": [
                        {"module": "core", "names": ["bar"], "is_internal": True, "line_number": 1}
                    ]
                },
                {
                    "file_path": "/app/bottom.py",
                    "file_name": "bottom.py",
                    "total_lines": 5,
                    "classes": [],
                    "functions": [],
                    "imports": []
                }
            ]
        }

    def test_build_graph(self):
        agent = DependencyGraphAgent()
        agent.build_graph(self.analyzer_output)

        self.assertEqual(agent.graph.number_of_nodes(), 5)
        self.assertTrue(agent.graph.has_edge("main", "utils"))
        self.assertTrue(agent.graph.has_edge("utils", "core"))
        self.assertTrue(agent.graph.has_edge("core", "utils"))
        self.assertTrue(agent.graph.has_edge("leaf", "core"))

    def test_analyze(self):
        agent = DependencyGraphAgent()
        agent.build_graph(self.analyzer_output)
        analysis = agent.analyze()

        self.assertFalse(analysis.stats.is_dag)
        self.assertEqual(len(analysis.stats.circular_dependencies), 1)
        self.assertIn("utils", analysis.stats.circular_dependencies[0])
        self.assertIn("core", analysis.stats.circular_dependencies[0])

        self.assertIn("utils", analysis.shared_modules)
        self.assertIn("core", analysis.shared_modules)

        self.assertIn("bottom", analysis.leaf_modules)

        # Centrality
        self.assertEqual(analysis.centrality_ranking[0].module, "utils")

if __name__ == "__main__":
    unittest.main()
