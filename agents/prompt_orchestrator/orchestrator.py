from typing import List, Dict, Any, Set
from agents.prompt_orchestrator.models import ComponentInstruction, StructuredPrompt, ArchitecturePromptMap
import collections

class PromptOrchestrator:
    def __init__(self):
        pass

    def topology_sort(self, adjacency_list: Dict[str, List[str]]) -> List[str]:
        """
        Orders components based on dependencies.
        B depends on A -> A should come first.
        Input adjacency_list: {module: [dependencies]}
        """
        # Count in-degrees (how many things depend on this module)
        # and build reverse adjacency (what things depend on this module)
        # Wait, if A: [B], A depends on B. B should be built first.
        # This is standard Kahn's algorithm if we reverse the edges.

        # We want to find nodes with no dependencies.
        # But wait, the adjacency_list is {node: [dependencies]}.
        # So leaf nodes in this graph (out-degree 0) have no dependencies.

        graph = adjacency_list
        all_nodes = set(graph.keys())
        for deps in graph.values():
            all_nodes.update(deps)

        # Standard topological sort
        sorted_nodes = []
        visited = set()
        temp_visited = set()

        def visit(node):
            if node in temp_visited:
                # Cycle detected, but we'll just ignore for now or handle gracefully
                return
            if node not in visited:
                temp_visited.add(node)
                for neighbor in graph.get(node, []):
                    visit(neighbor)
                temp_visited.remove(node)
                visited.add(node)
                sorted_nodes.append(node)

        for node in all_nodes:
            visit(node)

        return sorted_nodes

    def generate_instructions(self, component_name: str, dependencies: List[str]) -> ComponentInstruction:
        return ComponentInstruction(
            component_name=component_name,
            purpose=f"Implement the {component_name} module.",
            dependencies=dependencies,
            build_steps=[
                f"Define the interface for {component_name}.",
                f"Implement core logic, ensuring compatibility with {', '.join(dependencies) if dependencies else 'none'}.",
                f"Add validation and error handling.",
                f"Write unit tests for {component_name}."
            ],
            constraints=[
                "Follow PEP 8 guidelines.",
                "Maintain async compatibility where necessary.",
                "Ensure strict typing with Pydantic or type hints."
            ]
        )

    def format_structured_prompt(self, instructions: List[ComponentInstruction]) -> StructuredPrompt:
        # For simplicity, we create one big prompt or could split it.
        # The requirement says "Output structured prompts".

        return StructuredPrompt(
            title="AI Builder Instruction Set",
            system_role="You are an expert Python Software Engineer.",
            context="You are tasked with building a modular Python system based on the following architecture map.",
            instructions=instructions,
            output_format="Provide clean, runnable Python code for each component."
        )

    def orchestrate(self, architecture_map: Dict[str, Any]) -> ArchitecturePromptMap:
        project_name = architecture_map.get("project_name", "New Project")
        adjacency_list = architecture_map.get("adjacency_list", {})

        ordered_modules = self.topology_sort(adjacency_list)

        all_instructions = []
        for module in ordered_modules:
            # Only generate for modules that were actually in the original keys?
            # Or all of them. Let's do all.
            deps = adjacency_list.get(module, [])
            all_instructions.append(self.generate_instructions(module, deps))

        # We might want to group instructions into multiple prompts
        # but for now let's just make one.
        prompt = self.format_structured_prompt(all_instructions)

        return ArchitecturePromptMap(
            project_name=project_name,
            ordered_prompts=[prompt],
            dependency_chain=ordered_modules
        )
