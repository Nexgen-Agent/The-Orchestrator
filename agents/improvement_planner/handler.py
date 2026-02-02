import asyncio
from typing import Dict, Any
from agents.improvement_planner.planner import ImprovementPlanner

async def handle_task(task_packet: Dict[str, Any]) -> Dict[str, Any]:
    """
    Orchestration handler for FOG.
    Expects 'optimization_report' in payload.
    """
    payload = task_packet.get("payload", {})
    optimization_report = payload.get("optimization_report")

    if not optimization_report:
        return {"status": "error", "message": "Missing optimization_report in payload"}

    try:
        planner = ImprovementPlanner()
        # Offload to thread for consistency
        plan = await asyncio.to_thread(planner.generate_plan, optimization_report)

        return {
            "status": "success",
            "result": plan.model_dump(mode='json')
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
