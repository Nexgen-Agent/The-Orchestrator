import os
import shutil
import tempfile
import ast
from typing import List, Dict, Any, Optional
from agents.sandbox_simulation.models import (
    SimulationConfig, SimulationResult, SafeCheck, SimulationReport
)

class SandboxSimulator:
    def __init__(self):
        self.unsafe_builtins = {"eval", "exec", "compile"}
        self.unsafe_modules = {"os", "subprocess", "shutil", "pickle"}

    def simulate(self, config: SimulationConfig) -> SimulationReport:
        logs = []
        conflicts = []
        side_effects = []
        safety_checks = []

        # 1. Create Isolated Environment
        temp_dir = None
        if config.isolated_run:
            temp_dir = tempfile.mkdtemp(prefix="fog_sim_")
            logs.append(f"Created isolated environment at {temp_dir}")
            try:
                self._duplicate_project(config.project_path, temp_dir)
                logs.append("Project duplicated successfully.")
            except Exception as e:
                return self._error_report(config, f"Failed to duplicate project: {str(e)}")

        # 2. Safety Checks
        if config.check_unsafe_patterns:
            safety_results = self._run_safety_checks(config.project_path)
            safety_checks.extend(safety_results)
            if any(not c.passed for c in safety_results):
                logs.append("Unsafe patterns detected during pre-scan.")

        # 3. Task Simulation (Dry-run)
        # In a real scenario, this would involve running the code with mock inputs
        # Here we simulate the process
        logs.append(f"Simulating task: {config.task_description}")

        # Mock detection of conflicts
        if "delete" in config.task_description.lower() or "overwrite" in config.task_description.lower():
             conflicts.append("Potential file deletion detected.")
             side_effects.append("Modification of project structure.")

        # Cleanup
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            logs.append("Isolated environment cleaned up.")

        result = SimulationResult(
            success=True,
            logs=logs,
            conflicts=conflicts,
            side_effects=side_effects,
            safety_checks=safety_checks
        )

        return self._generate_report(config, result)

    def _duplicate_project(self, src: str, dst: str):
        if not os.path.exists(src):
            raise FileNotFoundError(f"Source project path {src} not found.")

        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dst, item)
            if os.path.isdir(s):
                if item not in {".git", "__pycache__", "backups", "storage"}:
                    shutil.copytree(s, d)
            else:
                shutil.copy2(s, d)

    def _run_safety_checks(self, project_path: str) -> List[SafeCheck]:
        checks = []
        unsafe_calls = []

        for root, _, files in os.walk(project_path):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            tree = ast.parse(f.read())
                            for node in ast.walk(tree):
                                if isinstance(node, ast.Call):
                                    func_name = self._get_func_name(node.func)
                                    if func_name in self.unsafe_builtins:
                                        unsafe_calls.append(f"{func_name} in {file}:{node.lineno}")
                    except Exception:
                        pass

        checks.append(SafeCheck(
            check_name="Unsafe Builtins",
            passed=len(unsafe_calls) == 0,
            details=", ".join(unsafe_calls) if unsafe_calls else "No unsafe builtins found."
        ))

        return checks

    def _get_func_name(self, node: ast.AST) -> str:
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return node.attr
        return ""

    def _generate_report(self, config: SimulationConfig, result: SimulationResult) -> SimulationReport:
        summary = f"Simulation for task '{config.task_description}' completed. "
        verdict = "Safe"

        if any(not c.passed for c in result.safety_checks):
            verdict = "Unsafe"
            summary += "Critical safety violations found. "
        elif result.conflicts:
            verdict = "Risky"
            summary += "Potential conflicts or side effects identified. "

        return SimulationReport(
            config=config,
            result=result,
            summary=summary,
            verdict=verdict
        )

    def _error_report(self, config: SimulationConfig, message: str) -> SimulationReport:
        return SimulationReport(
            config=config,
            result=SimulationResult(
                success=False,
                logs=[message],
                conflicts=[],
                side_effects=[],
                safety_checks=[]
            ),
            summary=f"Simulation failed: {message}",
            verdict="Failed"
        )
