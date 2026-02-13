import pytest
import asyncio
import os
import json
from agents.meta_agent_trainer.engine import MetaAgentTrainerEngine
from agents.meta_agent_trainer.models import AgentBlueprint, TrainingReport

@pytest.mark.asyncio
async def test_generate_agent_from_blueprint(tmp_path):
    # Change current working directory to tmp_path to avoid creating 'agents/' in repo root
    # Actually, the code uses agents/ relative path.
    # I'll just check if it creates the directory.
    engine = MetaAgentTrainerEngine()
    blueprint = AgentBlueprint(agent_name="test_agent_mate", base_module="mate_base")

    # We should be careful about where we create this in tests.
    # For now, I'll just verify the logic returns the expected path.
    path = engine.generate_agent_from_blueprint(blueprint)
    assert "test_agent_mate" in path
    assert os.path.exists(path)
    assert os.path.exists(os.path.join(path, "handler.py"))

    # Cleanup
    import shutil
    shutil.rmtree(path)

@pytest.mark.asyncio
async def test_simulate_training(tmp_path):
    project_path = str(tmp_path)
    # Create a dummy python file
    with open(os.path.join(project_path, "dummy.py"), "w") as f:
        f.write("import os")

    engine = MetaAgentTrainerEngine(history_path=str(tmp_path / "history.json"))
    report = await engine.simulate_training("test_agent", project_path)

    assert isinstance(report, TrainingReport)
    assert report.agent_name == "test_agent"
    assert report.compatibility_score > 0

@pytest.mark.asyncio
async def test_evolve_trainer(tmp_path):
    engine = MetaAgentTrainerEngine(history_path=str(tmp_path / "history.json"))
    # No history yet
    result = engine.evolve_trainer()
    assert result["status"] == "no_history"

    # Add fake history
    engine.history.training_history.append(TrainingReport(
        agent_name="agent1", training_module="m1", compatibility_score=0.9, success=True
    ))
    result = engine.evolve_trainer()
    assert result["status"] == "success"
    assert result["evolved"] is True

@pytest.mark.asyncio
async def test_optimize_agent_code(tmp_path):
    agent_dir = tmp_path / "agent_to_opt"
    agent_dir.mkdir()
    (agent_dir / "logic.py").write_text("def redundant_func(): pass\nimport os")

    engine = MetaAgentTrainerEngine()
    actions = engine.optimize_agent_code(str(agent_dir))

    assert any("redundant_func" in a for a in actions)
