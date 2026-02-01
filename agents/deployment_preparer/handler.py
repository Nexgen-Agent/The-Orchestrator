import asyncio
from typing import Dict, Any
from agents.deployment_preparer.preparer import DeploymentPreparer

async def handle_task(task_packet: Dict[str, Any]) -> Dict[str, Any]:
    """
    Orchestration handler for FOG.
    Expects 'project_path' in payload.
    """
    payload = task_packet.get("payload", {})
    project_path = payload.get("project_path")

    if not project_path:
        return {"status": "error", "message": "Missing project_path in payload"}

    try:
        preparer = DeploymentPreparer(project_path)
        report = await asyncio.to_thread(preparer.prepare)

        return {
            "status": "success",
            "result": report.model_dump(mode='json')
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
