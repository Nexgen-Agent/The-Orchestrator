import asyncio
from typing import Dict, Any
from agents.test_generator.generator import AutomatedTestGenerator

async def handle_task(task_packet: Dict[str, Any]) -> Dict[str, Any]:
    """
    Orchestration handler for FOG.
    Expects 'project_analysis' in payload.
    """
    payload = task_packet.get("payload", {})
    project_analysis = payload.get("project_analysis")

    if not project_analysis:
        return {"status": "error", "message": "Missing project_analysis in payload"}

    try:
        generator = AutomatedTestGenerator()
        report = generator.run_full_report(project_analysis)

        return {
            "status": "success",
            "result": report.model_dump(mode='json')
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
