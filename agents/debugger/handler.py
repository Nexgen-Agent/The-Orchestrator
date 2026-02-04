import asyncio
from typing import Dict, Any
from agents.debugger.debugger import Debugger
from agents.debugger.models import DebugRequest
from fog.core.state import state_store

async def handle_task(task_packet: Dict[str, Any]) -> Dict[str, Any]:
    """
    Orchestration handler for Debugger Agent.
    Expects 'project_path' in payload.
    """
    payload = task_packet.get("payload", {})
    project_path = payload.get("project_path")

    if not project_path:
        return {"status": "error", "message": "Missing project_path in payload"}

    request = DebugRequest(
        project_path=project_path,
        auto_fix=payload.get("auto_fix", False),
        validation_rounds=payload.get("validation_rounds", 3),
        simulation_report_id=payload.get("simulation_report_id")
    )

    debugger = Debugger(project_path)
    try:
        report = await debugger.run_debug(request)

        # Save to state
        state = state_store.get_state()
        if "debug_history" not in state:
            state["debug_history"] = []
        state["debug_history"].append(report.model_dump(mode='json'))
        state_store._save()

        return {
            "status": "success",
            "result": report.model_dump(mode='json')
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
