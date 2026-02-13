import pytest
import asyncio
import os
import json
from agents.self_evolution_engine.engine import SelfEvolutionEngine
from agents.self_evolution_engine.models import EvolutionReport, AuditReport

@pytest.mark.asyncio
async def test_analyze_health():
    engine = SelfEvolutionEngine()
    # Mock some data in state_store if necessary,
    # but analyze_health should handle empty state gracefully.
    health = engine.analyze_health()
    assert isinstance(health, dict)

@pytest.mark.asyncio
async def test_analyze_architecture(tmp_path):
    # Create a dummy project structure
    project_path = tmp_path / "project"
    project_path.mkdir()
    (project_path / "__init__.py").write_text("")
    (project_path / "main.py").write_text("import project.utils\nprint('hello')")
    (project_path / "utils.py").write_text("def helper(): pass")

    engine = SelfEvolutionEngine()
    arch = engine.analyze_architecture(str(project_path))

    assert "graph_summary" in arch
    assert arch["graph_summary"]["total_modules"] >= 2
    assert isinstance(arch["issues"], list)

@pytest.mark.asyncio
async def test_propose_evolution():
    engine = SelfEvolutionEngine()
    health = {"agent_a": {"success_rate": 0.5, "latency_score": 0.8, "failure_rate": 0.5}}
    arch = {"issues": [{"type": "God module", "module": "agent_a"}]}

    proposals = engine.propose_evolution(health, arch)
    assert len(proposals) >= 2 # One for success rate, one for God module
    assert any(p.change_type == "split" for p in proposals)
    assert any(p.change_type == "refactor" for p in proposals)

@pytest.mark.asyncio
async def test_run_optimization_cycle(tmp_path):
    project_path = str(tmp_path)
    # Create a dummy python file to avoid empty project issues
    with open(os.path.join(project_path, "dummy.py"), "w") as f:
        f.write("import os")

    engine = SelfEvolutionEngine(history_path=str(tmp_path / "history.json"))
    report = await engine.run_optimization_cycle(project_path)

    assert isinstance(report, EvolutionReport)
    assert report.agent_name == "SelfEvolutionEngine"
    # Even if no proposals are generated, success should be True
    assert report.success is True
