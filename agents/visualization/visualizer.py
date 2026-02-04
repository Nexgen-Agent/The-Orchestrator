import networkx as nx
import matplotlib.pyplot as plt
import os
import json
import uuid
from typing import Dict, Any, List, Optional
from agents.visualization.models import GraphType, VisualizationOutput, VisualizationRequest
from fog.core.logging import logger

# Use a non-interactive backend for Matplotlib
import matplotlib
matplotlib.use('Agg')

class VisualizationAgent:
    def __init__(self, output_dir: str = "storage/visualizations"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_visualization(self, request: VisualizationRequest) -> VisualizationOutput:
        logger.info("GENERATING_VISUALIZATION", {"type": request.graph_type})

        vis_id = str(uuid.uuid4())
        output = VisualizationOutput(
            visualization_id=vis_id,
            graph_type=request.graph_type
        )

        G = nx.DiGraph()

        if request.graph_type == GraphType.DEPENDENCY:
            self._build_dependency_graph(G, request.data)
        elif request.graph_type == GraphType.AGENT_INTERACTION:
            self._build_agent_interaction_graph(G, request.data)
        elif request.graph_type == GraphType.ORCHESTRATION_FLOW:
            self._build_orchestration_flow_graph(G, request.data)

        if request.output_format in ["png", "both"]:
            png_filename = f"{vis_id}.png"
            png_path = os.path.join(self.output_dir, png_filename)
            self._save_as_png(G, png_path, request.title or str(request.graph_type))
            output.png_path = png_path

        if request.output_format in ["json", "both"]:
            output.json_data = nx.node_link_data(G)

        return output

    def _build_dependency_graph(self, G: nx.DiGraph, data: Dict[str, Any]):
        # Data format from Dependency Graph agent
        edges = data.get("edges", [])
        for edge in edges:
            G.add_edge(edge[0], edge[1])

    def _build_agent_interaction_graph(self, G: nx.DiGraph, data: Dict[str, Any]):
        # Data format: list of interactions from logs or state
        # Expects {"interactions": [{"from": "agent1", "to": "agent2", "task_type": "analysis"}]}
        interactions = data.get("interactions", [])
        for inter in interactions:
            G.add_edge(inter["from"], inter["to"], label=inter.get("task_type", ""))

    def _build_orchestration_flow_graph(self, G: nx.DiGraph, data: Dict[str, Any]):
        # Data format: task lifecycle or workflow sequence
        # Expects {"sequence": [["task1"], ["task2", "task3"], ["task4"]]}
        sequence = data.get("sequence", [])
        prev_tasks = []
        for stage in sequence:
            for task in stage:
                G.add_node(task)
                for prev in prev_tasks:
                    G.add_edge(prev, task)
            prev_tasks = stage

    def _save_as_png(self, G: nx.DiGraph, path: str, title: str):
        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(G)
        nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=2000, edge_color='gray', font_size=10, font_weight='bold', arrows=True)

        # Add edge labels if they exist
        edge_labels = nx.get_edge_attributes(G, 'label')
        if edge_labels:
            nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

        plt.title(title)
        plt.savefig(path)
        plt.close()

    def list_visualizations(self) -> List[str]:
        return [f for f in os.listdir(self.output_dir) if f.endswith(".png")]
