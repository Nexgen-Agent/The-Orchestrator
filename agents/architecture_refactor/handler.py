import asyncio
from typing import Dict, Any
from agents.architecture_refactor.refactorer import ArchitectureRefactorer

async def handle_task(task_packet: Dict[str, Any]) -> Dict[str, Any]:
    """
    Orchestration handler for FOG.
    Expects 'project_analysis' and 'dependency_graph' in payload.
    """
    payload = task_packet.get("payload", {})
    project_analysis = payload.get("project_analysis")
    dependency_graph = payload.get("dependency_graph")

    if not project_analysis or not dependency_graph:
        return {"status": "error", "message": "Missing project_analysis or dependency_graph in payload"}

    try:
        refactorer = ArchitectureRefactorer()
        # Offload logic to thread if it becomes heavy
        plan = await asyncio.to_thread(refactorer.analyze_and_propose, project_analysis, dependency_graph)

        return {
            "status": "success",
            "result": plan.model_dump(mode='json')
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
