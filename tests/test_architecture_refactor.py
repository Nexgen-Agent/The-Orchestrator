import pytest
from agents.architecture_refactor.refactorer import ArchitectureRefactorer
from agents.architecture_refactor.models import RefactorType

def test_refactorer_god_module():
    refactorer = ArchitectureRefactorer()
    analysis = {
        "files": [
            {
                "file_name": "big_module.py",
                "total_lines": 600,
                "classes": [{"name": "C1"}],
                "functions": [{"name": "f1"}]
            }
        ]
    }
    graph = {"stats": {"circular_dependencies": []}, "centrality_ranking": []}

    plan = refactorer.analyze_and_propose(analysis, graph)
    assert len(plan.suggestions) == 1
    assert plan.suggestions[0].type == RefactorType.SPLIT_MODULE
    assert "big_module.py" in plan.suggestions[0].target

def test_refactorer_circular_dependency():
    refactorer = ArchitectureRefactorer()
    analysis = {"files": []}
    graph = {
        "stats": {
            "circular_dependencies": [["A", "B", "A"]]
        },
        "centrality_ranking": []
    }

    plan = refactorer.analyze_and_propose(analysis, graph)
    assert len(plan.suggestions) == 1
    assert plan.suggestions[0].type == RefactorType.FIX_CIRCULAR_DEPENDENCY
    assert "A" in plan.suggestions[0].target

def test_refactorer_high_coupling():
    refactorer = ArchitectureRefactorer()
    analysis = {"files": []}
    graph = {
        "stats": {"circular_dependencies": []},
        "centrality_ranking": [
            {"module": "core.py", "score": 0.9}
        ]
    }

    plan = refactorer.analyze_and_propose(analysis, graph)
    assert len(plan.suggestions) == 1
    assert plan.suggestions[0].type == RefactorType.DECOUPLE_MODULES
    assert "core.py" in plan.suggestions[0].target
