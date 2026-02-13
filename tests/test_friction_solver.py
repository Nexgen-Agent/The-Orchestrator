import pytest
import asyncio
import os
import json
from agents.friction_solver.solver import FrictionSolver, KnowledgeScout
from agents.friction_solver.models import FrictionSolverConfig
from agents.friction_solver.handler import handle_task
from agents.friction_solver.memory import FrictionMemory

@pytest.mark.asyncio
async def test_error_classification():
    solver = FrictionSolver()

    assert solver._classify_error("ModuleNotFoundError: No module named 'requests'") == "Dependency conflict"
    assert solver._classify_error("SyntaxError: invalid syntax") == "Code error"
    assert solver._classify_error("PermissionError: [Errno 13] Permission denied") == "Security restriction"
    assert solver._classify_error("ConnectionRefusedError: [Errno 111] Connection refused") == "Network or environment issue"

@pytest.mark.asyncio
async def test_solver_logic(tmp_path):
    # Create a dummy project path
    project_path = str(tmp_path)

    solver = FrictionSolver()
    config = FrictionSolverConfig(
        project_path=project_path,
        error_message="ModuleNotFoundError: No module named 'numpy'"
    )

    report = await solver.solve(config)

    assert report.error_type == "Dependency conflict"
    assert len(report.solution_attempts) > 0
    assert report.successful_fix is not None
    assert report.confidence_score >= 0.9

@pytest.mark.asyncio
async def test_handler(tmp_path):
    project_path = str(tmp_path)
    task_packet = {
        "payload": {
            "project_path": project_path,
            "error_message": "Some generic error"
        }
    }

    result = await handle_task(task_packet)
    assert result["status"] == "success"
    assert "result" in result
    assert result["result"]["error_type"] == "General Technical Friction"

@pytest.mark.asyncio
async def test_memory_persistence(tmp_path):
    memory_path = str(tmp_path / "friction_memory.json")
    memory = FrictionMemory(memory_path=memory_path)

    memory.save_fix("Code error", "SyntaxError: invalid syntax", {"description": "Fix syntax", "action": "echo"})
    fix = memory.get_fix("Code error", "SyntaxError: invalid syntax")
    assert fix["description"] == "Fix syntax"

    # Reload memory
    new_memory = FrictionMemory(memory_path=memory_path)
    assert new_memory.get_fix("Code error", "SyntaxError: invalid syntax")["description"] == "Fix syntax"

@pytest.mark.asyncio
async def test_auto_apply(tmp_path):
    project_path = str(tmp_path)
    memory_path = str(tmp_path / "memory.json")
    # Create a dummy python file
    with open(os.path.join(project_path, "main.py"), "w") as f:
        f.write("print('hello')")

    memory = FrictionMemory(memory_path=memory_path)
    solver = FrictionSolver(memory=memory)

    # SyntaxError triggers python3 -m py_compile *.py
    config = FrictionSolverConfig(
        project_path=project_path,
        error_message="SyntaxError: invalid syntax",
        auto_apply=True
    )

    report = await solver.solve(config)
    assert report.successful_fix is not None
    assert "[AUTO-APPLIED]" in report.successful_fix

@pytest.mark.asyncio
async def test_scout_returns_dict():
    scout = KnowledgeScout()
    results = await scout.scout("ModuleNotFoundError", "Dependency conflict")
    assert isinstance(results[0], dict)
    assert "description" in results[0]
    assert "action" in results[0]
