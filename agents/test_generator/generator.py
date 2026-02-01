import os
from typing import List, Dict, Any
from agents.test_generator.models import TestStub, TestFile, CoverageRecommendation, TestGenerationReport

class TestGenerator:
    def __init__(self, root_path: str = ""):
        self.root_path = root_path

    def generate_stubs_from_analysis(self, file_analysis: Dict[str, Any]) -> List[TestStub]:
        stubs = []

        # Stubs for classes
        for class_info in file_analysis.get("classes", []):
            class_name = class_info.get("name")
            stub_content = f"class Test{class_name}:\n    def setup_method(self):\n        pass\n\n"
            for method in class_info.get("methods", []):
                method_name = method.get("name")
                if method_name != "__init__":
                    stub_content += f"    def test_{method_name}(self):\n        # TODO: Implement test for {method_name}\n        assert True\n\n"
            stubs.append(TestStub(
                name=f"Test{class_name}",
                target_name=class_name,
                content=stub_content
            ))

        # Stubs for functions
        for func_info in file_analysis.get("functions", []):
            func_name = func_info.get("name")
            stub_content = f"def test_{func_name}():\n    # TODO: Implement test for {func_name}\n    assert True\n\n"
            stubs.append(TestStub(
                name=f"test_{func_name}",
                target_name=func_name,
                content=stub_content
            ))

        return stubs

    def detect_missing_coverage(self, project_analysis: Dict[str, Any]) -> List[CoverageRecommendation]:
        recommendations = []
        project_root = project_analysis.get("root_path", "")
        test_dir = os.path.join(project_root, "tests")

        existing_test_files = []
        if os.path.exists(test_dir):
            for root, _, files in os.walk(test_dir):
                for file in files:
                    if file.startswith("test_") and file.endswith(".py"):
                        existing_test_files.append(file)

        for file_info in project_analysis.get("files", []):
            file_name = file_info.get("file_name")
            if not file_name: continue

            expected_test_file = f"test_{file_name}"
            if expected_test_file not in existing_test_files:
                missing_items = []
                for cls in file_info.get("classes", []):
                    missing_items.append(f"Class: {cls.get('name')}")
                for func in file_info.get("functions", []):
                    missing_items.append(f"Function: {func.get('name')}")

                if missing_items:
                    recommendations.append(CoverageRecommendation(
                        module_name=file_name.replace(".py", ""),
                        missing_tests=missing_items,
                        importance="High" if len(missing_items) > 5 else "Medium"
                    ))

        return recommendations

    def generate_runnable_tests(self, project_analysis: Dict[str, Any]) -> List[TestFile]:
        test_files = []
        project_root = project_analysis.get("root_path", "")

        for file_info in project_analysis.get("files", []):
            file_path = file_info.get("file_path", "")
            file_name = file_info.get("file_name", "")
            if not file_name: continue

            stubs = self.generate_stubs_from_analysis(file_info)
            if not stubs: continue

            # Create import statement for the module being tested
            # Heuristic: module path relative to root
            rel_path = os.path.relpath(file_path, project_root)
            module_parts = rel_path.replace(".py", "").split(os.path.sep)

            # If the project root has an __init__.py, it's a package
            if os.path.exists(os.path.join(project_root, "__init__.py")):
                package_name = os.path.basename(project_root)
                module_parts = [package_name] + module_parts

            if module_parts[-1] == "__init__":
                module_parts.pop()

            module_import_path = ".".join(module_parts)

            content = f"import pytest\nimport {module_import_path}\n\n"
            for stub in stubs:
                content += stub.content + "\n"

            test_file_path = os.path.join(project_root, "tests", f"test_{file_name}")
            test_files.append(TestFile(
                file_path=test_file_path,
                content=content
            ))

        return test_files

    def run_full_report(self, project_analysis: Dict[str, Any]) -> TestGenerationReport:
        recommendations = self.detect_missing_coverage(project_analysis)
        generated_files = self.generate_runnable_tests(project_analysis)

        summary = f"Analyzed {len(project_analysis.get('files', []))} modules. "
        summary += f"Generated {len(generated_files)} test files. "
        summary += f"Found {len(recommendations)} coverage gaps."

        return TestGenerationReport(
            project_path=project_analysis.get("root_path", ""),
            generated_files=generated_files,
            recommendations=recommendations,
            summary=summary
        )
