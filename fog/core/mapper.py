import ast
import os
from typing import Dict, List, Set, Any

class DependencyMapper:
    def scan_project(self, project_path: str) -> Dict[str, Any]:
        graph = {}
        all_modules = self._find_all_python_files(project_path)

        for module_name, file_path in all_modules.items():
            imports = self._get_imports(file_path)
            # Filter imports to only include those within the project
            internal_imports = [imp for imp in imports if any(imp.startswith(m) for m in all_modules.keys())]
            graph[module_name] = {
                "path": file_path,
                "imports": internal_imports,
                "is_isolated": len(internal_imports) == 0
            }

        # Mark shared dependencies
        usage_count = {}
        for module, info in graph.items():
            for imp in info["imports"]:
                usage_count[imp] = usage_count.get(imp, 0) + 1

        for module in graph:
            graph[module]["is_shared"] = usage_count.get(module, 0) > 1

        return graph

    def _find_all_python_files(self, project_path: str) -> Dict[str, str]:
        modules = {}
        project_path = os.path.abspath(project_path)
        base_name = os.path.basename(project_path)
        is_package = os.path.exists(os.path.join(project_path, "__init__.py"))

        for root, _, files in os.walk(project_path):
            for file in files:
                if file.endswith(".py"):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, project_path)

                    if rel_path.endswith(".py"):
                        module_parts = rel_path[:-3].split(os.path.sep)
                        if module_parts[-1] == "__init__":
                            module_parts.pop()

                        if is_package:
                            module_name = ".".join([base_name] + module_parts)
                        else:
                            module_name = ".".join(module_parts)

                        if not module_name: # Handle the case where it was just __init__.py in a non-package root?
                            module_name = base_name

                        modules[module_name] = full_path
        return modules

    def _get_imports(self, file_path: str) -> List[str]:
        imports = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read())

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
        except Exception:
            # Skip files that can't be parsed
            pass
        return list(set(imports))
