import pytest
import asyncio
from unittest.mock import MagicMock, patch
from agents.software_builder.builder import SoftwareBuilder
from agents.software_builder.models import BuildRequest
from agents.friction_solver.solver import FrictionSolver

@pytest.mark.asyncio
async def test_builder_friction_integration():
    # Mocking DependencyMapper to return a simple project structure
    with patch("agents.software_builder.builder.DependencyMapper") as MockMapper:
        mapper_instance = MockMapper.return_value
        mapper_instance.scan_project.return_value = {
            "module_a": {"path": "module_a.py", "imports": []}
        }

        builder = SoftwareBuilder(project_path=".")

        # Mock asyncio.sleep inside _build_module to raise an exception, triggering the internal try-except
        with patch("agents.software_builder.builder.asyncio.sleep", side_effect=Exception("ModuleNotFoundError: No module named 'missing_pkg'")):
            request = BuildRequest(project_path=".", target_modules=["module_a"])
            report = await builder.run_build(request)

            # Since _build_module caught the exception, run_build should complete
            assert len(report.friction_reports) == 1
            assert report.friction_reports[0]["error_type"] == "Dependency conflict"
            assert "missing_pkg" in report.friction_reports[0]["root_cause"]

@pytest.mark.asyncio
async def test_debugger_scout_integration():
    from agents.debugger.debugger import Debugger
    from agents.debugger.models import DebugRequest

    # Create a temporary file with a syntax error
    with open("temp_syntax_error.py", "w") as f:
        f.write("if True\n    print('fail')")

    try:
        debugger = Debugger(project_path=".")
        # We only want to scan our temp file
        with patch("os.walk") as mock_walk:
            mock_walk.return_value = [(".", [], ["temp_syntax_error.py"])]

            request = DebugRequest(project_path=".")
            report = await debugger.run_debug(request)

            assert any(i.issue_type == "Syntax" for i in report.issues)
            # Verify that proposed fixes include established fixes from the scout
            assert any("Established fix" in f.description for f in report.proposed_fixes)
    finally:
        import os
        if os.path.exists("temp_syntax_error.py"):
            os.remove("temp_syntax_error.py")
