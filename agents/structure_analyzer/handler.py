import os
import asyncio
from typing import Dict, Any, List
from agents.structure_analyzer.analyzer import CodeStructureAnalyzer
from agents.structure_analyzer.models import ProjectAnalysis

async def analyze_project(root_path: str) -> ProjectAnalysis:
    root_path = os.path.abspath(root_path)
    files_to_analyze = []

    for root, _, files in os.walk(root_path):
        for file in files:
            if file.endswith(".py"):
                files_to_analyze.append(os.path.join(root, file))

    results = []
    # Process in parallel with a limit on concurrency if needed,
    # but for now we'll just run them as tasks

    def process_file(file_path):
        analyzer = CodeStructureAnalyzer(file_path, project_root=root_path)
        return analyzer.analyze()

    # Using to_thread because analyzer is CPU bound and blocking I/O
    tasks = [asyncio.to_thread(process_file, fp) for fp in files_to_analyze]
    results = await asyncio.gather(*tasks)

    return ProjectAnalysis(root_path=root_path, files=results)

async def handle_task(task_packet: Dict[str, Any]) -> Dict[str, Any]:
    """
    Orchestration handler for FOG.
    Expects 'project_path' in payload.
    """
    payload = task_packet.get("payload", {})
    project_path = payload.get("project_path")

    if not project_path:
        return {"status": "error", "message": "Missing project_path in payload"}

    if not os.path.exists(project_path):
        return {"status": "error", "message": f"Path {project_path} does not exist"}

    try:
        analysis = await analyze_project(project_path)
        return {
            "status": "success",
            "result": analysis.model_dump(mode='json')
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
