import ast
import re
import os
from typing import List, Dict, Any, Set
from agents.security_analyzer.models import SecurityRisk, UnsafePattern, SecurityReport, RiskSeverity

class SecurityAnalyzer:
    def __init__(self):
        # Regex patterns for common secrets
        self.secret_patterns = {
            "API Key": re.compile(r"(?:key|api|token|secret|pass|auth)[-_]?(?:id|key|secret|token|password)?['\"]?\s*[:=]\s*['\"]([a-zA-Z0-9]{16,})['\"]", re.IGNORECASE),
            "Generic Secret": re.compile(r"['\"](?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])[A-Za-z0-9+/]{32,}['\"]"),
        }

        # Unsafe code patterns and their risk levels
        self.unsafe_functions = {
            "eval": "Critical",
            "exec": "Critical",
            "os.system": "High",
            "subprocess.Popen": "Medium",
            "subprocess.call": "Medium",
            "subprocess.run": "Medium",
            "pickle.load": "High",
            "pickle.loads": "High",
            "yaml.load": "High", # When used without Loader=SafeLoader
        }

        # Risky dependencies
        self.risky_packages = {"pickle", "marshal", "shelve", "cryptography.hazmat.primitives.asymmetric.padding.PKCS1v15"}

    def scan_file(self, file_path: str) -> SecurityReport:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content)

        risks_detected = self._detect_secrets(content)
        unsafe_patterns = self._detect_unsafe_patterns(tree)
        risky_deps = self._detect_risky_dependencies(tree)

        # Determine overall risk level
        all_severities = [r.severity for r in risks_detected] + [p.severity for p in unsafe_patterns]
        overall_risk = self._determine_overall_severity(all_severities)

        return SecurityReport(
            file_path=file_path,
            overall_risk_level=overall_risk,
            risks_detected=risks_detected,
            unsafe_patterns=unsafe_patterns,
            risky_dependencies=risky_deps
        )

    def _detect_secrets(self, content: str) -> List[SecurityRisk]:
        risks = []
        lines = content.splitlines()
        for i, line in enumerate(lines):
            for name, pattern in self.secret_patterns.items():
                match = pattern.search(line)
                if match:
                    risks.append(SecurityRisk(
                        category="Hardcoded Secret",
                        severity=RiskSeverity.CRITICAL,
                        description=f"Potential {name} detected.",
                        line_number=i + 1,
                        evidence=match.group(0)
                    ))
        return risks

    def _detect_unsafe_patterns(self, tree: ast.AST) -> List[UnsafePattern]:
        patterns = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = self._get_func_name(node.func)
                if func_name in self.unsafe_functions:
                    severity_str = self.unsafe_functions[func_name]
                    severity = RiskSeverity[severity_str.upper()]

                    # Special check for yaml.load
                    if func_name == "yaml.load":
                        has_safe_loader = any(kw.arg == 'Loader' and self._get_func_name(kw.value) == 'SafeLoader' for kw in node.keywords)
                        if has_safe_loader:
                            continue

                    patterns.append(UnsafePattern(
                        pattern_name=func_name,
                        severity=severity,
                        description=f"Unsafe function '{func_name}' detected. This could lead to code execution vulnerabilities.",
                        line_number=node.lineno
                    ))
        return patterns

    def _detect_risky_dependencies(self, tree: ast.AST) -> List[str]:
        risky_imports = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name in self.risky_packages:
                            risky_imports.append(alias.name)
                else:
                    if node.module in self.risky_packages:
                        risky_imports.append(node.module)
        return list(set(risky_imports))

    def _get_func_name(self, node: ast.AST) -> str:
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_func_name(node.value)}.{node.attr}"
        return ""

    def _determine_overall_severity(self, severities: List[RiskSeverity]) -> RiskSeverity:
        if not severities:
            return RiskSeverity.LOW
        if RiskSeverity.CRITICAL in severities:
            return RiskSeverity.CRITICAL
        if RiskSeverity.HIGH in severities:
            return RiskSeverity.HIGH
        if RiskSeverity.MEDIUM in severities:
            return RiskSeverity.MEDIUM
        return RiskSeverity.LOW
