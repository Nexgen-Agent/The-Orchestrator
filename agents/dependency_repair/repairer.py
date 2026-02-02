import os
import ast
import sys
from typing import List, Set, Dict, Any
from agents.dependency_repair.models import (
    DependencyIssue, RepairSuggestion, RepairReport, RepairLogEntry
)

class DependencyRepairer:
    def __init__(self, project_path: str):
        self.project_path = os.path.abspath(project_path)
        self.mapping = {
            "fastapi": "fastapi",
            "pydantic": "pydantic",
            "uvicorn": "uvicorn",
            "httpx": "httpx",
            "networkx": "networkx",
            "yaml": "PyYAML",
            "requests": "requests",
            "pytest": "pytest"
        }

    def analyze(self) -> Dict[str, Any]:
        all_imports = self._scan_imports()
        issues = self._detect_issues(all_imports)
        suggestions = self._generate_suggestions(issues)

        return {
            "imports": list(all_imports),
            "issues": issues,
            "suggestions": suggestions
        }

    def _scan_imports(self) -> Set[str]:
        all_imports = set()
        for root, _, files in os.walk(self.project_path):
            for file in files:
                if file.endswith(".py"):
                    try:
                        with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                            tree = ast.parse(f.read())
                            for node in ast.walk(tree):
                                if isinstance(node, ast.Import):
                                    for alias in node.names:
                                        all_imports.add(alias.name)
                                elif isinstance(node, ast.ImportFrom):
                                    if node.module:
                                        all_imports.add(node.module)
                    except Exception:
                        pass
        return all_imports

    def _detect_issues(self, imports: Set[str]) -> List[DependencyIssue]:
        req_path = os.path.join(self.project_path, "requirements.txt")
        existing_reqs = set()
        if os.path.exists(req_path):
            with open(req_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        existing_reqs.add(line.split('==')[0].split('>=')[0].strip().lower())

        std_lib = sys.stdlib_module_names if hasattr(sys, 'stdlib_module_names') else set()
        issues = []

        for imp in imports:
            base = imp.split('.')[0]
            if not base or base in std_lib or base == os.path.basename(self.project_path):
                continue

            # Simple check: if we have a requirements.txt but this isn't in it, it's an issue
            pkg_name = self.mapping.get(base, base).lower()
            if existing_reqs and pkg_name not in existing_reqs:
                # Also check if it is a local module
                if not self._is_local_module(base):
                    issues.append(DependencyIssue(module=base, issue_type="missing"))

        return issues

    def _is_local_module(self, module_name: str) -> bool:
        # Check if a directory or file with this name exists in the project root
        if os.path.isdir(os.path.join(self.project_path, module_name)):
            return True
        if os.path.exists(os.path.join(self.project_path, f"{module_name}.py")):
            return True
        return False

    def _generate_suggestions(self, issues: List[DependencyIssue]) -> List[RepairSuggestion]:
        suggestions = []
        for issue in issues:
            pkg_name = self.mapping.get(issue.module, issue.module).lower()
            suggestions.append(RepairSuggestion(
                module=issue.module,
                suggested_package=pkg_name
            ))
        return suggestions

    def repair(self, auto_install: bool = False) -> RepairReport:
        analysis = self.analyze()
        issues = analysis["issues"]
        suggestions = analysis["suggestions"]
        logs = []

        req_path = os.path.join(self.project_path, "requirements.txt")

        # If requirements.txt doesn't exist, we might want to create it
        # but for now let's assume we append to it if it exists.

        for suggestion in suggestions:
            try:
                # 1. Update requirements.txt
                with open(req_path, "a") as f:
                    f.write(f"\n{suggestion.suggested_package}")

                logs.append(RepairLogEntry(
                    action="Update requirements.txt",
                    target=suggestion.suggested_package,
                    status="Success",
                    message=f"Added {suggestion.suggested_package} to requirements.txt"
                ))

                # 2. Optionally install (though usually better to just update requirements)
                if auto_install:
                    # This would involve subprocess call, skipping for safety in mock
                    logs.append(RepairLogEntry(
                        action="Install package",
                        target=suggestion.suggested_package,
                        status="Skipped",
                        message="Auto-install requested but skipped for safety in this environment"
                    ))

            except Exception as e:
                logs.append(RepairLogEntry(
                    action="Repair",
                    target=suggestion.suggested_package,
                    status="Failed",
                    message=str(e)
                ))

        status = "Success" if logs and all(l.status != "Failed" for l in logs) else "Partial"
        if not suggestions:
            status = "Success"
            summary = "No repairs needed."
        else:
            summary = f"Performed {len(logs)} repair actions."

        return RepairReport(
            project_path=self.project_path,
            issues_found=issues,
            suggestions=suggestions,
            repairs_performed=logs,
            summary=summary,
            status=status
        )
