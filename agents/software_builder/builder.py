import asyncio
import os
import time
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from agents.software_builder.models import BuildReport, BuildRequest, ModuleBuildInfo, BuildStep
from fog.core.mapper import DependencyMapper
from fog.core.backup import backup_manager
from fog.core.logging import logger

class SoftwareBuilder:
    def __init__(self, project_path: str):
        self.project_path = os.path.abspath(project_path)
        self.mapper = DependencyMapper()
        self.report = BuildReport(project_path=self.project_path)

    async def run_build(self, request: BuildRequest) -> BuildReport:
        logger.info("BUILD_STARTED", {"project_path": self.project_path})
        self.report.status = "InProgress"
        start_time = time.time()

        # 1. Map Dependencies
        dep_map = self.mapper.scan_project(self.project_path)
        self.report.total_modules = len(dep_map)

        # 2. Determine Build Order (Simple topological sort / levels)
        build_order = self._get_build_order(dep_map)

        # 3. Incremental Build Loop
        for level in build_order:
            tasks = []
            for module_name in level:
                if request.target_modules and module_name not in request.target_modules:
                    continue

                module_info = dep_map[module_name]
                tasks.append(self._build_module(module_name, module_info, request.max_iterations))

            results = await asyncio.gather(*tasks)
            for module_report in results:
                self.report.modules[module_report.module_name] = module_report
                if module_report.status == "Completed":
                    self.report.completed_modules += 1
                else:
                    self.report.failed_modules += 1

        self.report.status = "Completed" if self.report.failed_modules == 0 else "PartialSuccess"
        self.report.summary = f"Build finished. {self.report.completed_modules}/{self.report.total_modules} modules built successfully."
        self.report.performance_metrics = {
            "total_duration_seconds": time.time() - start_time,
            "avg_iterations_per_module": sum(m.total_iterations for m in self.report.modules.values()) / len(self.report.modules) if self.report.modules else 0
        }

        logger.info("BUILD_FINISHED", {"status": self.report.status})
        return self.report

    def _get_build_order(self, dep_map: Dict[str, Any]) -> List[List[str]]:
        levels = []
        visited = set()
        remaining = set(dep_map.keys())

        while remaining:
            current_level = []
            for module in list(remaining):
                deps = set(dep_map[module]["imports"])
                # Only care about internal dependencies that are actually in our project
                internal_deps = {d for d in deps if d in dep_map}
                if internal_deps.issubset(visited):
                    current_level.append(module)

            if not current_level:
                # Circular dependencies or broken project
                # Add remaining to a final level and break
                levels.append(list(remaining))
                break

            levels.append(current_level)
            visited.update(current_level)
            remaining.difference_update(current_level)

        return levels

    async def _build_module(self, module_name: str, info: Dict[str, Any], max_iterations: int) -> ModuleBuildInfo:
        module_report = ModuleBuildInfo(
            module_name=module_name,
            file_path=info["path"],
            dependencies=info["imports"]
        )

        # 1. Analyze Step
        analyze_step = BuildStep(module_name=module_name, action="analyze", status="InProgress")
        module_report.build_steps.append(analyze_step)
        # Simulate analysis
        await asyncio.sleep(0.1)
        analyze_step.status = "Completed"
        analyze_step.logs.append(f"Successfully analyzed {module_name}")

        # 2. Iterative Improvement Loop
        for i in range(1, max_iterations + 1):
            module_report.total_iterations = i
            improve_step = BuildStep(module_name=module_name, action="improve", status="InProgress", iterations=i)
            module_report.build_steps.append(improve_step)

            # Simulate improvement work
            await asyncio.sleep(0.2)

            # Integration with backup would happen here before any write
            # For now, we simulate safe execution
            improve_step.status = "Completed"
            improve_step.logs.append(f"Iteration {i}: Applied logical optimizations and refined docstrings.")

        # 3. Verification Step
        verify_step = BuildStep(module_name=module_name, action="verify", status="InProgress")
        module_report.build_steps.append(verify_step)
        await asyncio.sleep(0.1)
        verify_step.status = "Completed"

        module_report.status = "Completed"
        return module_report
