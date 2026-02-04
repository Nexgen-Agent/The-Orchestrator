import asyncio
from typing import Dict, Any
from agents.system_resilience.resilience import ResilienceManager
from fog.models.task import TaskPacket

async def handle_task(task_packet_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Orchestration handler for System Resilience Agent.
    """
    resilience = ResilienceManager()
    task_packet = TaskPacket(**task_packet_dict)

    action = task_packet.payload.get("action", "report")

    if action == "analyze_and_fix":
        report = await resilience.detect_and_fix()
        return {
            "status": "success",
            "result": report.model_dump(mode='json')
        }
    elif action == "report":
        history = resilience.get_resilience_history()
        return {
            "status": "success",
            "result": [h.model_dump(mode='json') for h in history]
        }
    elif action == "set_safe_mode":
        active = task_packet.payload.get("active", True)
        resilience.set_safe_mode(active)
        return {"status": "success", "message": f"Safe mode set to {active}"}
    else:
        return {"status": "error", "message": f"Unknown action: {action}"}
