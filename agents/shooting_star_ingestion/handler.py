import asyncio
from typing import Dict, Any
from agents.shooting_star_ingestion.ingestion import ShootingStarIngestion

async def handle_task(task_packet: Dict[str, Any]) -> Dict[str, Any]:
    """
    Orchestration handler for Shooting Star Intelligence Ingestion.
    Expects 'project_path' in payload.
    """
    payload = task_packet.get("payload", {})
    project_path = payload.get("project_path")

    if not project_path:
        return {"status": "error", "message": "Missing project_path in payload"}

    ingestion = ShootingStarIngestion(project_path)

    try:
        report = await ingestion.ingest()
        return {
            "status": "success",
            "result": report.model_dump(mode='json')
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
