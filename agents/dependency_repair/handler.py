import asyncio
from typing import Dict, Any
from agents.dependency_repair.repairer import DependencyRepairer

async def handle_task(task_packet: Dict[str, Any]) -> Dict[str, Any]:
    """
    Orchestration handler for FOG.
    Expects 'project_path' and 'action' in payload.
    Actions: 'analyze', 'repair'.
    """
    payload = task_packet.get("payload", {})
    project_path = payload.get("project_path")
    action = payload.get("action", "analyze")
    auto_install = payload.get("auto_install", False)

    if not project_path:
        return {"status": "error", "message": "Missing project_path in payload"}

    try:
        repairer = DependencyRepairer(project_path)

        if action == "analyze":
            result = await asyncio.to_thread(repairer.analyze)
            return {
                "status": "success",
                "result": result
            }
        elif action == "repair":
            report = await asyncio.to_thread(repairer.repair, auto_install=auto_install)
            return {
                "status": "success",
                "result": report.model_dump(mode='json')
            }
        else:
            return {"status": "error", "message": f"Unknown action: {action}"}

    except Exception as e:
        return {"status": "error", "message": str(e)}
