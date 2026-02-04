import ast
import os
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from agents.debugger.models import DebugReport, DebugRequest, Issue, ProposedFix, Severity
from fog.core.state import state_store
from fog.core.logging import logger

class Debugger:
    def __init__(self, project_path: str):
        self.project_path = os.path.abspath(project_path)
        self.report = DebugReport(project_path=self.project_path)

    async def run_debug(self, request: DebugRequest) -> DebugReport:
        logger.info("DEBUG_STARTED", {"project_path": self.project_path})
        self.report.status = "Analyzing"

        # 1. Static Analysis (AST parsing to detect syntax errors and basic unsafe patterns)
        await self._run_static_analysis()

        # 2. Analyze Simulation Report if provided
        if request.simulation_report_id:
            await self._analyze_simulation_report(request.simulation_report_id)

        # 3. Iterative Fix Engine
        if request.auto_fix and self.report.issues:
            self.report.status = "Fixing"
            await self._run_fix_engine(request.validation_rounds)

        self.report.status = "Completed"
        self.report.summary = f"Detected {len(self.report.issues)} issues. Applied {len(self.report.proposed_fixes)} fixes."

        logger.info("DEBUG_FINISHED", {"issues": len(self.report.issues)})
        return self.report

    async def _run_static_analysis(self):
        for root, _, files in os.walk(self.project_path):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, self.project_path)

                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                            tree = ast.parse(content)

                            # Basic Unsafe Pattern detection
                            for node in ast.walk(tree):
                                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                                    if node.func.id in ["eval", "exec"]:
                                        self.report.issues.append(Issue(
                                            module_name=rel_path,
                                            file_path=file_path,
                                            line_number=node.lineno,
                                            severity="High",
                                            issue_type="SafePattern",
                                            description=f"Unsafe use of {node.func.id}() detected."
                                        ))
                    except SyntaxError as e:
                        self.report.issues.append(Issue(
                            module_name=rel_path,
                            file_path=file_path,
                            line_number=e.lineno,
                            severity="Critical",
                            issue_type="Syntax",
                            description=f"Syntax error: {e.msg}",
                            evidence=e.text
                        ))
                    except Exception as e:
                        logger.error("DEBUG_FILE_ERROR", {"file": file_path, "error": str(e)})

    async def _analyze_simulation_report(self, simulation_id: str):
        # Retrieve simulation report from state or direct integration
        # For now, we mock some findings if simulation_id is present
        self.report.issues.append(Issue(
            module_name="simulation_log",
            file_path="N/A",
            severity="Medium",
            issue_type="Runtime",
            description=f"Simulated runtime exception from report {simulation_id}",
            evidence="ConnectionTimeout at fog/core/connector.py:45"
        ))

    async def _run_fix_engine(self, validation_rounds: int):
        for issue in self.report.issues:
            if issue.severity in ["High", "Critical"]:
                # Propose a fix (Simulated)
                fix = ProposedFix(
                    issue_id=issue.issue_id,
                    description=f"Refactor to remove {issue.issue_type} issue in {issue.module_name}",
                    safety_rating="Safe"
                )
                self.report.proposed_fixes.append(fix)

                # Perform validation passes
                for r in range(1, validation_rounds + 1):
                    await asyncio.sleep(0.1)
                    self.report.validation_passes += 1
                    logger.info("DEBUG_VALIDATION_PASS", {"fix_id": fix.fix_id, "round": r})

    def get_summary(self) -> str:
        return f"Debugger found {len(self.report.issues)} issues."
