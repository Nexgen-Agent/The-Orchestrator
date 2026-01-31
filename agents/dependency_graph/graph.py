import networkx as nx
import os
from typing import Dict, List, Any
from agents.dependency_graph.models import (
    GraphStats, ModuleRanking, DependencyGraphOutput
)

class DependencyGraphAgent:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.root_path = ""

    def build_graph(self, analyzer_json: Dict[str, Any]):
        """
        Builds a directed graph from the Code Structure Analyzer JSON output.
        """
        self.graph = nx.DiGraph()
        self.root_path = analyzer_json.get("root_path", "")
        files = analyzer_json.get("files", [])

        # First pass: map file paths to module names and add nodes
        path_to_module = {}
        for file_info in files:
            file_path = file_info.get("file_path", "")
            module_name = self._get_module_name(file_path)
            path_to_module[file_path] = module_name
            self.graph.add_node(module_name, file_path=file_path)

        # Second pass: add edges for internal imports
        for file_info in files:
            file_path = file_info.get("file_path", "")
            current_module = path_to_module.get(file_path)
            imports = file_info.get("imports", [])

            for imp in imports:
                if imp.get("is_internal"):
                    target_module = imp.get("module")
                    if target_module:
                        # Find the best match in our nodes
                        # (The analyzer might return a sub-module, we want the node)
                        matched_node = self._match_module_to_node(target_module)
                        if matched_node and matched_node != current_module:
                            self.graph.add_edge(current_module, matched_node)

    def _get_module_name(self, file_path: str) -> str:
        if not self.root_path:
            return os.path.basename(file_path).replace(".py", "")

        is_package = os.path.exists(os.path.join(self.root_path, "__init__.py"))
        base_name = os.path.basename(self.root_path)

        rel_path = os.path.relpath(file_path, self.root_path)
        module_parts = rel_path.replace(".py", "").split(os.path.sep)

        if module_parts[-1] == "__init__":
            module_parts.pop()

        if is_package:
            module_name = ".".join([base_name] + module_parts)
        else:
            module_name = ".".join(module_parts)

        if not module_name:
            module_name = base_name

        return module_name

    def _match_module_to_node(self, module_name: str) -> str:
        if module_name in self.graph.nodes:
            return module_name

        # Check for parent modules that might be nodes (e.g., fog.core for fog.core.engine)
        parts = module_name.split(".")
        for i in range(len(parts) - 1, 0, -1):
            parent = ".".join(parts[:i])
            if parent in self.graph.nodes:
                return parent

        # Check for sub-modules if the current module is a package node
        # (Though usually imports go the other way)

        return ""

    def analyze(self) -> DependencyGraphOutput:
        """
        Analyzes the graph and returns structural insights.
        """
        stats = self._get_stats()
        shared_modules = [n for n, d in self.graph.in_degree() if d > 1]
        leaf_modules = [n for n, d in self.graph.out_degree() if d == 0]

        centrality = nx.degree_centrality(self.graph)
        rankings = [ModuleRanking(module=m, score=s) for m, s in sorted(centrality.items(), key=lambda x: x[1], reverse=True)]

        # Core modules: Top 20% by centrality, at least 1
        num_core = max(1, len(rankings) // 5)
        core_modules = [r.module for r in rankings[:num_core]]

        return DependencyGraphOutput(
            stats=stats,
            shared_modules=shared_modules,
            leaf_modules=leaf_modules,
            core_modules=core_modules,
            adjacency_list={n: list(self.graph.successors(n)) for n in self.graph.nodes},
            centrality_ranking=rankings,
            graph_json=nx.node_link_data(self.graph)
        )

    def _get_stats(self) -> GraphStats:
        circular = list(nx.simple_cycles(self.graph))
        return GraphStats(
            num_nodes=self.graph.number_of_nodes(),
            num_edges=self.graph.number_of_edges(),
            density=nx.density(self.graph),
            is_dag=nx.is_directed_acyclic_graph(self.graph),
            circular_dependencies=circular
        )
