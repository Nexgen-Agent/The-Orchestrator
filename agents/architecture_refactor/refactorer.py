import uuid
from typing import List, Dict, Any
from agents.architecture_refactor.models import (
    RefactorPlan, RefactorSuggestion, RefactorType, ModuleMove
)

class ArchitectureRefactorer:
    def __init__(self, project_path: str = ""):
        self.project_path = project_path

    def analyze_and_propose(self, project_analysis: Dict[str, Any], dependency_graph: Dict[str, Any]) -> RefactorPlan:
        suggestions = []
        moves = []

        # 1. Detect God Modules (Large files)
        files = project_analysis.get("files", [])
        for file_info in files:
            total_lines = file_info.get("total_lines", 0)
            file_name = file_info.get("file_name", "unknown")
            num_classes = len(file_info.get("classes", []))
            num_functions = len(file_info.get("functions", []))

            if total_lines > 500 or (num_classes + num_functions) > 15:
                suggestions.append(RefactorSuggestion(
                    id=str(uuid.uuid4()),
                    type=RefactorType.SPLIT_MODULE,
                    target=file_name,
                    reason=f"Module is too large ({total_lines} lines) or contains too many components ({num_classes + num_functions}).",
                    description=f"Consider splitting {file_name} into smaller, more focused sub-modules.",
                    impact_score=8
                ))

        # 2. Detect Circular Dependencies
        stats = dependency_graph.get("stats", {})
        circular = stats.get("circular_dependencies", [])
        for cycle in circular:
            cycle_str = " -> ".join(cycle)
            suggestions.append(RefactorSuggestion(
                id=str(uuid.uuid4()),
                type=RefactorType.FIX_CIRCULAR_DEPENDENCY,
                target=cycle[0],
                reason=f"Circular dependency detected: {cycle_str}",
                description=f"Break the cycle between {cycle_str} by moving shared logic to a common leaf module.",
                impact_score=9
            ))

        # 3. Highly Coupled Modules (High Centrality/Degree)
        # We can look at centrality from dependency graph
        centrality = dependency_graph.get("centrality_ranking", [])
        for rank in centrality[:3]: # Top 3 most central modules
            if rank.get("score", 0) > 0.5:
                suggestions.append(RefactorSuggestion(
                    id=str(uuid.uuid4()),
                    type=RefactorType.DECOUPLE_MODULES,
                    target=rank.get("module"),
                    reason=f"Module '{rank.get('module')}' is highly central (score: {rank.get('score')}), indicating high coupling.",
                    description=f"Review dependencies of {rank.get('module')} to see if some logic can be decentralized or abstracted.",
                    impact_score=7
                ))

        summary = f"Analyzed {len(files)} modules. Identified {len(suggestions)} potential structural improvements."

        return RefactorPlan(
            project_path=self.project_path or project_analysis.get("root_path", ""),
            suggestions=suggestions,
            planned_moves=moves,
            summary=summary
        )
