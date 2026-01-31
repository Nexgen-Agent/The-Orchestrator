import ast
import os
from typing import List, Any
from agents.structure_analyzer.models import (
    ClassMetadata, FunctionMetadata, ImportMetadata, FileAnalysis
)

class CodeStructureAnalyzer:
    def __init__(self, file_path: str, project_root: str = ""):
        self.file_path = file_path
        self.project_root = project_root
        self.source_code = ""
        self.tree = None
        self.total_lines = 0

    def analyze(self) -> FileAnalysis:
        with open(self.file_path, "r", encoding="utf-8") as f:
            self.source_code = f.read()

        self.total_lines = len(self.source_code.splitlines())
        self.tree = ast.parse(self.source_code)

        classes = []
        functions = []
        imports = []

        for node in self.tree.body:
            if isinstance(node, ast.ClassDef):
                classes.append(self._analyze_class(node))
            elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                functions.append(self._analyze_function(node))
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.extend(self._analyze_import(node))

        return FileAnalysis(
            file_path=self.file_path,
            file_name=os.path.basename(self.file_path),
            total_lines=self.total_lines,
            classes=classes,
            functions=functions,
            imports=imports
        )

    def _analyze_class(self, node: ast.ClassDef) -> ClassMetadata:
        methods = []
        for n in node.body:
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                methods.append(self._analyze_function(n, is_method=True))

        return ClassMetadata(
            name=node.name,
            bases=[self._get_source_segment(base) for base in node.bases],
            methods=methods,
            decorators=[self._get_source_segment(dec) for dec in node.decorator_list],
            line_number=node.lineno,
            end_line_number=node.end_lineno if hasattr(node, 'end_lineno') else node.lineno
        )

    def _analyze_function(self, node: Any, is_method: bool = False) -> FunctionMetadata:
        return FunctionMetadata(
            name=node.name,
            args=[arg.arg for arg in node.args.args],
            decorators=[self._get_source_segment(dec) for dec in node.decorator_list],
            line_number=node.lineno,
            end_line_number=node.end_lineno if hasattr(node, 'end_lineno') else node.lineno,
            is_method=is_method
        )

    def _analyze_import(self, node: Any) -> List[ImportMetadata]:
        results = []
        module = ""
        is_internal = False

        if isinstance(node, ast.Import):
            for alias in node.names:
                module = alias.name
                is_internal = self._is_internal(module)
                results.append(ImportMetadata(
                    module=module,
                    names=[alias.name],
                    is_internal=is_internal,
                    line_number=node.lineno
                ))
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            is_internal = self._is_internal(module)
            results.append(ImportMetadata(
                module=module,
                names=[alias.name for alias in node.names],
                is_internal=is_internal,
                line_number=node.lineno
            ))
        return results

    def _is_internal(self, module_name: str) -> bool:
        if not self.project_root:
            return False

        first_part = module_name.split('.')[0]

        # Case 1: project_root itself is the package (e.g., project_root='/app/fog' and module='fog.core')
        if first_part == os.path.basename(self.project_root):
            return True

        # Case 2: project_root contains the package (e.g., project_root='/app' and module='fog.core')
        potential_path = os.path.join(self.project_root, first_part)
        return os.path.isdir(potential_path)

    def _get_source_segment(self, node: Any) -> str:
        try:
            return ast.get_source_segment(self.source_code, node) or ""
        except Exception:
            return ""
