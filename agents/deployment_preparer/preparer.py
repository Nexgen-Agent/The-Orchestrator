import os
import ast
import sys
from typing import List, Set, Dict, Any
from agents.deployment_preparer.models import DeploymentReport, DeploymentPackage, MissingDependency

class DeploymentPreparer:
    def __init__(self, project_path: str):
        self.project_path = os.path.abspath(project_path)

    def prepare(self) -> DeploymentReport:
        # 1. Scan for imports
        all_imports = self._scan_imports()

        # 2. Check for missing dependencies
        missing = self.detect_missing_dependencies(all_imports)

        # 3. Generate contents
        dockerfile = self.generate_dockerfile()
        requirements = self.generate_requirements(all_imports)
        startup = self.generate_startup_script()

        package = DeploymentPackage(
            dockerfile_content=dockerfile,
            requirements_content=requirements,
            startup_script_content=startup,
            target_files=["Dockerfile", "requirements.txt", "start.sh"]
        )

        status = "Success"
        if missing:
            status = "Warning"

        summary = f"Generated deployment package for {self.project_path}. "
        if missing:
            summary += f"Detected {len(missing)} potentially missing dependencies."
        else:
            summary += "No missing dependencies detected."

        return DeploymentReport(
            project_path=self.project_path,
            missing_dependencies=missing,
            generated_package=package,
            status=status,
            summary=summary
        )

    def generate_dockerfile(self, python_version: str = "3.11-slim") -> str:
        return f"""FROM python:{python_version}

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x start.sh

CMD ["./start.sh"]
"""

    def generate_requirements(self, imports: Set[str]) -> str:
        # Filter standard library
        std_lib = sys.stdlib_module_names if hasattr(sys, 'stdlib_module_names') else set()
        # Common external packages mapping (simple version)
        external = {imp for imp in imports if imp.split('.')[0] not in std_lib and imp.split('.')[0] != os.path.basename(self.project_path)}

        # Map some common modules to their pip package names
        mapping = {
            "fastapi": "fastapi",
            "pydantic": "pydantic",
            "uvicorn": "uvicorn",
            "httpx": "httpx",
            "networkx": "networkx",
            "yaml": "PyYAML",
            "requests": "requests"
        }

        pkgs = set()
        for imp in external:
            base = imp.split('.')[0]
            pkgs.add(mapping.get(base, base))

        return "\n".join(sorted(list(pkgs)))

    def generate_startup_script(self) -> str:
        # Heuristic to find entry point
        entry = "main.py"
        if os.path.exists(os.path.join(self.project_path, "api", "main.py")):
            entry = "fog/api/main.py" # Specifc to FOG for now or generic

        return f"""#!/bin/bash
export PYTHONPATH=$PYTHONPATH:.
python3 {entry}
"""

    def detect_missing_dependencies(self, imports: Set[str]) -> List[MissingDependency]:
        # This is hard without a real environment check,
        # but we can check if they are in an existing requirements.txt if it exists
        req_path = os.path.join(self.project_path, "requirements.txt")
        existing_reqs = set()
        if os.path.exists(req_path):
            with open(req_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        existing_reqs.add(line.split('==')[0].split('>=')[0].strip().lower())

        std_lib = sys.stdlib_module_names if hasattr(sys, 'stdlib_module_names') else set()
        missing = []

        mapping = {
            "fastapi": "fastapi",
            "pydantic": "pydantic",
            "uvicorn": "uvicorn",
            "httpx": "httpx",
            "networkx": "networkx",
            "yaml": "PyYAML"
        }

        for imp in imports:
            base = imp.split('.')[0]
            if base in std_lib or base == os.path.basename(self.project_path) or not base:
                continue

            pkg_name = mapping.get(base, base).lower()
            if pkg_name not in existing_reqs and existing_reqs:
                missing.append(MissingDependency(module=base, suggested_package=pkg_name))

        return missing

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
