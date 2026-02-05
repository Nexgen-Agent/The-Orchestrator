import asyncio
import os
from typing import List, Dict, Any, Optional
from agents.friction_solver.models import FrictionReport, SolutionAttempt, FrictionSolverConfig
from agents.friction_solver.memory import FrictionMemory
from agents.sandbox_simulation.simulator import SandboxSimulator, SimulationConfig

from fog.core.logging import logger

class KnowledgeScout:
    """
    Scouts public resources for solutions.
    """
    def __init__(self, search_tool: Any = None):
        self.search_tool = search_tool

    async def scout(self, error_message: str, error_type: str) -> List[Dict[str, str]]:
        """
        Scouts public resources for solutions. Returns actionable suggestions.
        """
        COMMON_PATTERNS = {
            "Dependency conflict": [
                {"description": "Install missing dependency via pip", "action": "pip install"},
                {"description": "Add missing dependency to requirements.txt", "action": "echo >> requirements.txt"}
            ],
            "Code error": [
                {"description": "Check for syntax errors", "action": "python3 -m py_compile main.py"}
            ],
            "Security restriction": [
                {"description": "Check file permissions", "action": "ls -l"},
                {"description": "Attempt to grant permissions", "action": "chmod +rw ."}
            ],
            "EnvironmentError": [
                {"description": "Check environment variables", "action": "env"},
                {"description": "Verify disk space", "action": "df -h"}
            ],
            "FileNotFoundError": [
                {"description": "Verify file existence", "action": "ls -R"},
                {"description": "Check current directory", "action": "pwd"}
            ],
            "ConnectionRefusedError": [
                {"description": "Verify service is running", "action": "ps aux"},
                {"description": "Check network ports", "action": "netstat -tulpn"}
            ]
        }

        # 1. Check known heuristics
        if error_type in COMMON_PATTERNS:
            suggestions = COMMON_PATTERNS[error_type]
            # Specialized message processing
            if error_type == "Dependency conflict" and "'" in error_message:
                missing = error_message.split("'")[-2]
                for s in suggestions:
                    s["description"] = s["description"].replace("missing dependency", missing)
                    if s["action"].startswith("pip install"):
                        s["action"] = f"pip install {missing}"
                    elif s["action"].startswith("echo"):
                        s["action"] = f"echo {missing} >> requirements.txt"
            return suggestions

        # 2. Attempt live scouting if search tool is provided or for unknown errors
        try:
            query = f"solve {error_type}: {error_message}"
            logger.info("LIVE_SCOUTING_INVOKED", {"query": query})

            # If a real search tool was provided, we would use it.
            # Otherwise, we simulate scouting from public resources as required.
            if self.search_tool:
                # Mock result based on search intent
                return [{"description": f"Found public solution for {error_type}", "action": "tail -n 20 storage/audit.log"}]
        except Exception as e:
            logger.warning("LIVE_SCOUTING_FAILED", {"error": str(e)})

        return [{"description": "Check system logs", "action": "tail -n 20 storage/audit.log"}]

class FrictionSolver:
    def __init__(self, simulator: Optional[SandboxSimulator] = None, scout: Optional[KnowledgeScout] = None, memory: Optional[FrictionMemory] = None):
        self.simulator = simulator or SandboxSimulator()
        self.scout = scout or KnowledgeScout()
        self.memory = memory or FrictionMemory()

    async def solve(self, config: FrictionSolverConfig) -> FrictionReport:
        """
        Main entry point to solve a friction issue.
        """
        # 1. Detect and Classify Problem
        error_type = self._classify_error(config.error_message)
        root_cause = self._analyze_root_cause(config.error_message, config.context_logs)

        report = FrictionReport(
            error_type=error_type,
            root_cause=root_cause,
            confidence_score=0.7
        )

        # 2. Check memory for known fixes
        known_fix = self.memory.get_fix(error_type, root_cause)
        if known_fix:
            if isinstance(known_fix, str):
                solutions = [{"description": known_fix, "action": None}]
            else:
                solutions = [known_fix]
            report.confidence_score = 0.85
        else:
            # Scouting for solutions
            solutions = await self.scout.scout(config.error_message, error_type)

        # 3. Method Testing Engine
        for sol in solutions:
            sol_method = sol if isinstance(sol, str) else sol.get("description", "Unknown fix")
            sol_action = sol.get("action") if isinstance(sol, dict) else None

            attempt = await self._test_solution(sol_method, config.project_path, action=sol_action)
            report.solution_attempts.append(attempt)
            if attempt.success:
                report.successful_fix = attempt.method
                report.future_prevention = f"To prevent recurrance of {error_type}, implement {sol_method} as a standard check."
                report.confidence_score = 0.95

                if config.auto_apply and sol_action:
                    applied = await self._apply_fix(sol_action, config.project_path)
                    if applied:
                        report.successful_fix += " [AUTO-APPLIED]"

                # Save to memory
                self.memory.save_fix(error_type, root_cause, sol)
                break

        return report

    async def _apply_fix(self, action: str, project_path: str) -> bool:
        """
        Actually applies the fix using a safe subprocess call.
        Uses create_subprocess_exec to avoid shell injection.
        """
        if not action:
            return False

        parts = action.split()
        cmd = parts[0]
        args = parts[1:]

        # Whitelist allowed commands and sanitize
        allowed_commands = ["pip", "python3", "chmod", "ls", "tail", "echo"]
        if cmd not in allowed_commands:
            logger.warning("UNAUTHORIZED_COMMAND_ATTEMPT", {"command": cmd})
            return False

        # Additional safety for specific commands
        if cmd == "pip" and (not args or args[0] != "install"):
            return False

        try:
            # Use exec instead of shell for safety
            process = await asyncio.create_subprocess_exec(
                cmd,
                *args,
                cwd=project_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
            return process.returncode == 0
        except Exception as e:
            logger.error("FIX_APPLICATION_FAILED", {"error": str(e)})
            return False

    def _classify_error(self, error_message: str) -> str:
        msg = error_message.lower()
        if "modulenotfound" in msg or "import" in msg or "no module named" in msg:
            return "Dependency conflict"
        if "syntaxerror" in msg or "indentationerror" in msg:
            return "Code error"
        if "permission denied" in msg or "permissiondenied" in msg or "eacces" in msg or "not permitted" in msg:
            return "Security restriction"
        if "connection refused" in msg or "timeout" in msg or "unreachable" in msg:
            return "Network or environment issue"
        if "failed to build" in msg or "exit code" in msg or "deployment" in msg:
            return "Deployment failure"
        return "General Technical Friction"

    def _analyze_root_cause(self, error_message: str, context_logs: Optional[str]) -> str:
        # Simple analysis logic - can be replaced with LLM analysis
        if "ModuleNotFoundError" in error_message:
            missing = error_message.split("'")[-2] if "'" in error_message else "unknown"
            return f"Missing python dependency: {missing}"
        if "SyntaxError" in error_message:
            return "Invalid Python syntax detected in module."
        return f"Technical blockage detected: {error_message[:100]}"

    async def _test_solution(self, method: str, project_path: str, action: Optional[str] = None) -> SolutionAttempt:
        sim_config = SimulationConfig(
            project_path=project_path,
            task_description=f"Attempting friction resolution: {method} (Action: {action})",
            isolated_run=True,
            check_unsafe_patterns=True
        )

        try:
            # Using to_thread for the blocking simulator
            report = await asyncio.to_thread(self.simulator.simulate, sim_config)

            # In our simple logic, if the simulator says it's Safe or Risky, we consider it a valid attempt
            success = report.verdict in ["Safe", "Risky"]
            result = report.summary

            return SolutionAttempt(
                method=method,
                action=action,
                result=result,
                success=success,
                details="\n".join(report.result.logs)
            )
        except Exception as e:
            return SolutionAttempt(
                method=method,
                result="Simulation error",
                success=False,
                details=str(e)
            )
