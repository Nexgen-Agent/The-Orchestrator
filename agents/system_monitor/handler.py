import asyncio
from typing import Dict, Any
from agents.system_monitor.monitor import SystemMonitor
from fog.core.state import state_store

async def handle_task(task_packet: Dict[str, Any]) -> Dict[str, Any]:
    """
    Orchestration handler for FOG.
    Produces a health report of the entire system.
    """
    monitor = SystemMonitor(state_store)

    try:
        report = monitor.get_health_report()
        return {
            "status": "success",
            "result": report.model_dump(mode='json')
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
