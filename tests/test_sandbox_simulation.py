import pytest
import os
import shutil
from agents.sandbox_simulation.simulator import SandboxSimulator, SimulationConfig

@pytest.fixture
def mock_project(tmp_path):
    project_dir = tmp_path / "mock_project"
    project_dir.mkdir()

    # Create a python file with an unsafe pattern
    unsafe_file = project_dir / "unsafe.py"
    unsafe_file.write_text("x = 1\neval('x + 1')\n")

    # Create a safe file
    safe_file = project_dir / "safe.py"
    safe_file.write_text("def add(a, b): return a + b\n")

    return str(project_dir)

def test_simulation_isolation(mock_project, tmp_path):
    simulator = SandboxSimulator()
    config = SimulationConfig(
        project_path=mock_project,
        task_description="Delete all files",
        isolated_run=True
    )

    report = simulator.simulate(config)
    assert report.result.success is True

    # Verify original project still exists and hasn't been modified
    assert os.path.exists(mock_project)
    assert os.path.exists(os.path.join(mock_project, "safe.py"))
    assert "Isolated environment cleaned up" in report.result.logs[len(report.result.logs)-1]

def test_unsafe_pattern_detection(mock_project):
    simulator = SandboxSimulator()
    config = SimulationConfig(
        project_path=mock_project,
        task_description="Run project analysis",
        check_unsafe_patterns=True
    )

    report = simulator.simulate(config)

    # Check that eval was detected
    unsafe_check = next(c for c in report.result.safety_checks if c.check_name == "Unsafe Builtins")
    assert unsafe_check.passed is False
    assert "eval" in unsafe_check.details
    assert report.verdict == "Unsafe"

def test_conflict_detection(mock_project):
    simulator = SandboxSimulator()
    config = SimulationConfig(
        project_path=mock_project,
        task_description="Overwrite safe.py with new logic"
    )

    report = simulator.simulate(config)
    assert any("Potential file deletion detected" in c for c in report.result.conflicts)
    assert report.verdict in ["Risky", "Unsafe"]
