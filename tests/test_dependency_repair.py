import pytest
import os
from agents.dependency_repair.repairer import DependencyRepairer

@pytest.fixture
def mock_project(tmp_path):
    project_dir = tmp_path / "mock_project"
    project_dir.mkdir()

    # Create a python file with imports
    code_file = project_dir / "app.py"
    code_file.write_text("import fastapi\nimport requests\nimport os\n")

    # Create requirements.txt missing one of the imports
    req_file = project_dir / "requirements.txt"
    req_file.write_text("fastapi\n")

    return str(project_dir)

def test_analyze_missing_dependency(mock_project):
    repairer = DependencyRepairer(mock_project)
    analysis = repairer.analyze()

    # 'os' is std lib, 'fastapi' is in requirements, 'requests' should be missing
    assert "requests" in analysis["imports"]
    assert any(issue.module == "requests" for issue in analysis["issues"])
    assert any(s.module == "requests" and s.suggested_package == "requests" for s in analysis["suggestions"])

def test_repair_updates_requirements(mock_project):
    repairer = DependencyRepairer(mock_project)
    report = repairer.repair()

    assert report.status == "Success"
    assert any(log.action == "Update requirements.txt" and log.target == "requests" for log in report.repairs_performed)

    # Verify file was updated
    req_path = os.path.join(mock_project, "requirements.txt")
    with open(req_path, "r") as f:
        content = f.read()
        assert "requests" in content

def test_is_local_module(mock_project):
    repairer = DependencyRepairer(mock_project)

    # app.py exists
    assert repairer._is_local_module("app") is True
    # helper doesn't
    assert repairer._is_local_module("helper") is False

    # Create a local dir
    os.mkdir(os.path.join(mock_project, "helper"))
    assert repairer._is_local_module("helper") is True
