import asyncio
import os
from typing import List, Dict, Any, Optional
from agents.shooting_star_ingestion.models import IngestionReport, IngestionModule
from fog.core.logging import logger

# Import handlers from other agents
from agents.structure_analyzer.handler import handle_task as structure_handler
from agents.semantic_tagger.handler import handle_task as tagger_handler
from agents.logic_summarizer.handler import handle_task as summarizer_handler
from agents.dependency_graph.handler import handle_task as dependency_handler
from agents.prompt_orchestrator.handler import handle_task as prompt_handler

class ShootingStarIngestion:
    def __init__(self, project_path: str):
        self.project_path = os.path.abspath(project_path)
        self.report = IngestionReport(project_path=self.project_path)

    async def ingest(self) -> IngestionReport:
        logger.info("INGESTION_STARTED", {"project_path": self.project_path})
        self.report.status = "In Progress"

        # 1. Extract modules and architecture (Structure Analysis)
        structure_task = {
            "system_name": "structure_analyzer",
            "payload": {"project_path": self.project_path}
        }
        structure_res = await structure_handler(structure_task)
        if structure_res["status"] != "success":
            self.report.status = "Failed"
            logger.error("INGESTION_STRUCTURE_FAILED", {"error": structure_res.get("message")})
            return self.report

        analysis_data = structure_res["result"]
        files = analysis_data.get("files", [])

        # 2. Tag business/psychology logic and Produce summaries (Parallel for each file)
        module_tasks = []
        for file_info in files:
            file_path = file_info.get("file_path")
            module_tasks.append(self._process_module(file_path, file_info))

        self.report.modules = await asyncio.gather(*module_tasks)

        # 3. Feed to dependency mapper
        dependency_task = {
            "system_name": "dependency_graph",
            "payload": {"analyzer_output": analysis_data}
        }
        dependency_res = await dependency_handler(dependency_task)
        if dependency_res["status"] == "success":
            self.report.dependency_map = dependency_res["result"]

        # 4. Feed to prompt orchestrator
        prompt_task = {
            "system_name": "prompt_orchestrator",
            "payload": {"architecture_map": self.report.dependency_map}
        }
        prompt_res = await prompt_handler(prompt_task)
        if prompt_res["status"] == "success":
            self.report.build_instructions = prompt_res["result"]

        # 5. Produce architecture summary (Simplified)
        self.report.architecture_summary = f"System contains {len(files)} modules. "
        if self.report.dependency_map:
            stats = self.report.dependency_map.get("stats", {})
            self.report.architecture_summary += f"Detected {stats.get('total_edges', 0)} dependencies. "

        self.report.status = "Completed"
        logger.info("INGESTION_COMPLETED", {"ingestion_id": self.report.ingestion_id})
        return self.report

    async def _process_module(self, file_path: str, structure: Dict[str, Any]) -> IngestionModule:
        # Tagging
        tag_task = {
            "system_name": "semantic_tagger",
            "payload": {"file_path": file_path}
        }
        tag_res = await tagger_handler(tag_task)
        tags = tag_res.get("result", {}).get("tags", []) if tag_res["status"] == "success" else []

        # Summarization
        sum_task = {
            "system_name": "logic_summarizer",
            "payload": {"file_path": file_path}
        }
        sum_res = await summarizer_handler(sum_task)
        summary = sum_res.get("result", {}).get("analysis", {}).get("summary") if sum_res["status"] == "success" else None

        return IngestionModule(
            file_path=file_path,
            summary=summary,
            tags=tags,
            structure=structure
        )
