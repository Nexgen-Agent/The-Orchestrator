import ast
import os
from typing import List, Dict, Any, Set
from agents.code_quality.models import FileRiskReport, FunctionMetrics

class CodeQualityEvaluator:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.source_code = ""
        self.tree = None

    def evaluate(self) -> FileRiskReport:
        with open(self.file_path, "r", encoding="utf-8") as f:
            self.source_code = f.read()

        self.tree = ast.parse(self.source_code)

        # 1. Unused imports
        unused_imports = self._find_unused_imports()

        # 2. Function reports
        function_reports = []
        max_nesting = 0
        total_complexity = 1

        for node in ast.walk(self.tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                report = self._analyze_function(node)
                function_reports.append(report)
                max_nesting = max(max_nesting, report.nesting_depth)
                total_complexity += report.complexity

        # 3. Missing try/except
        missing_try_except = self._detect_missing_try_except()

        # 4. Scoring
        score = self._calculate_score(unused_imports, total_complexity, max_nesting, missing_try_except, function_reports)

        risk_level = "Low"
        if score < 40: risk_level = "Critical"
        elif score < 60: risk_level = "High"
        elif score < 80: risk_level = "Medium"

        return FileRiskReport(
            file_path=self.file_path,
            score=score,
            cyclomatic_complexity=total_complexity,
            unused_imports=unused_imports,
            missing_try_except=missing_try_except,
            max_nesting_depth=max_nesting,
            function_reports=function_reports,
            risk_level=risk_level
        )

    def _analyze_function(self, node: Any) -> FunctionMetrics:
        length = node.end_lineno - node.lineno + 1
        complexity = self._get_node_complexity(node)
        nesting = self._get_nesting_depth(node)

        warnings = []
        if length > 50:
            warnings.append(f"Function length ({length}) exceeds recommended 50 lines.")
        if complexity > 10:
            warnings.append(f"Cyclomatic complexity ({complexity}) is high.")
        if nesting > 3:
            warnings.append(f"Nesting depth ({nesting}) is too high.")

        return FunctionMetrics(
            name=node.name,
            line_number=node.lineno,
            length=length,
            complexity=complexity,
            nesting_depth=nesting,
            warnings=warnings
        )

    def _get_node_complexity(self, node: Any) -> int:
        complexity = 1
        for sub_node in ast.walk(node):
            if isinstance(sub_node, (ast.If, ast.While, ast.For, ast.ExceptHandler, ast.With, ast.And, ast.Or)):
                complexity += 1
        return complexity

    def _get_nesting_depth(self, node: Any) -> int:
        max_depth = 0
        for sub_node in node.body:
            if isinstance(sub_node, (ast.If, ast.While, ast.For, ast.Try, ast.With)):
                max_depth = max(max_depth, 1 + self._get_nesting_depth(sub_node))
        return max_depth

    def _find_unused_imports(self) -> List[str]:
        imported_names = {}
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported_names[alias.asname or alias.name] = alias.name
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imported_names[alias.asname or alias.name] = f"{node.module}.{alias.name}"

        used_names = set()
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                used_names.add(node.id)
            elif isinstance(node, ast.Attribute):
                # This is a bit simplified, but helps detect usage like 'os.path'
                curr = node
                while isinstance(curr, ast.Attribute):
                    curr = curr.value
                if isinstance(curr, ast.Name):
                    used_names.add(curr.id)

        unused = [full for name, full in imported_names.items() if name not in used_names]
        return unused

    def _detect_missing_try_except(self) -> List[str]:
        risky_calls = {'open', 'connect', 'request', 'execute', 'send', 'recv', 'save', 'delete', 'urlopen'}
        detected = []

        # Build map of nodes to their parent to check for Try ancestors
        parent_map = {child: node for node in ast.walk(self.tree) for child in ast.iter_child_nodes(node)}

        for node in ast.walk(self.tree):
            if isinstance(node, ast.Call):
                func_name = ""
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    func_name = node.func.attr

                if func_name in risky_calls:
                    if not self._is_wrapped_in_try_v2(node, parent_map):
                        detected.append(f"Risky operation '{func_name}' at line {node.lineno} potentially missing error handling.")
        return detected

    def _is_wrapped_in_try_v2(self, node: Any, parent_map: Dict[Any, Any]) -> bool:
        curr = node
        while curr in parent_map:
            curr = parent_map[curr]
            if isinstance(curr, ast.Try):
                return True
        return False

    def _is_wrapped_in_try(self, target_node: Any) -> bool:
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Try):
                for sub in ast.walk(node):
                    if sub == target_node:
                        return True
        return False

    def _calculate_score(self, unused_imports, complexity, max_nesting, risky_ops, func_reports) -> int:
        score = 100
        score -= len(unused_imports) * 2
        score -= max(0, complexity - 15) * 1
        score -= max(0, max_nesting - 3) * 5
        score -= len(risky_ops) * 5

        for f in func_reports:
            score -= len(f.warnings) * 2

        return max(0, min(100, int(score)))
