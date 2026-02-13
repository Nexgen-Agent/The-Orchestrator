from typing import Dict, Any
from agents.friction_solver.solver import FrictionSolver
from agents.friction_solver.models import FrictionSolverConfig

async def handle_task(task_packet: Dict[str, Any]) -> Dict[str, Any]:
    """
    Orchestration handler for FOG.
    Expects 'project_path' and 'error_message' in payload.
    """
    payload = task_packet.get("payload", {})
    project_path = payload.get("project_path")
    error_message = payload.get("error_message")
    context_logs = payload.get("context_logs")

    # Chat interaction support
    if payload.get("chat_interaction") and not error_message:
        error_message = payload.get("prompt")

    if not project_path:
        project_path = "." # Default to root if missing in chat

    if not error_message:
        return {"status": "error", "message": "Missing project_path or error_message in payload"}

    try:
        config = FrictionSolverConfig(
            project_path=project_path,
            error_message=error_message,
            context_logs=context_logs
        )
        solver = FrictionSolver()
        report = await solver.solve(config)

        return {
            "status": "success",
            "result": report.model_dump(mode='json')
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
