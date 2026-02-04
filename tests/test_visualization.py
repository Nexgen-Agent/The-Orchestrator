import unittest
import os
import shutil
import json
from agents.visualization.visualizer import VisualizationAgent
from agents.visualization.models import VisualizationRequest, GraphType

class TestVisualizationAgent(unittest.TestCase):
    def setUp(self):
        self.output_dir = "storage/test_visualizations"
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
        self.agent = VisualizationAgent(output_dir=self.output_dir)

    def tearDown(self):
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)

    def test_generate_dependency_graph(self):
        data = {
            "edges": [["A", "B"], ["B", "C"], ["A", "C"]]
        }
        request = VisualizationRequest(
            graph_type=GraphType.DEPENDENCY,
            data=data,
            output_format="both",
            title="Test Dependency Graph"
        )
        output = self.agent.generate_visualization(request)

        self.assertEqual(output.graph_type, GraphType.DEPENDENCY)
        self.assertTrue(os.path.exists(output.png_path))
        self.assertIsNotNone(output.json_data)
        self.assertEqual(len(output.json_data["nodes"]), 3)
        self.assertEqual(len(output.json_data["edges"]), 3)

    def test_generate_agent_interaction(self):
        data = {
            "interactions": [
                {"from": "AgentA", "to": "AgentB", "task_type": "request"},
                {"from": "AgentB", "to": "AgentC", "task_type": "forward"}
            ]
        }
        request = VisualizationRequest(
            graph_type=GraphType.AGENT_INTERACTION,
            data=data,
            output_format="png",
            title="Agent Interaction Graph"
        )
        output = self.agent.generate_visualization(request)
        self.assertTrue(os.path.exists(output.png_path))

    def test_generate_orchestration_flow(self):
        data = {
            "sequence": [["Task1"], ["Task2", "Task3"], ["Task4"]]
        }
        request = VisualizationRequest(
            graph_type=GraphType.ORCHESTRATION_FLOW,
            data=data,
            output_format="png"
        )
        output = self.agent.generate_visualization(request)
        self.assertTrue(os.path.exists(output.png_path))

if __name__ == "__main__":
    unittest.main()
