import asyncio
from typing import Dict, Any
from agents.software_builder.builder import SoftwareBuilder
from agents.software_builder.models import BuildRequest
from fog.core.state import state_store

async def handle_task(task_packet: Dict[str, Any]) -> Dict[str, Any]:
    """
    Orchestration handler for Software Builder.
    Expects 'project_path' in payload.
    """
    payload = task_packet.get("payload", {})
    project_path = payload.get("project_path")

    # Chat interaction support
    if not project_path:
        project_path = "." # Default to root if missing in chat

    if not project_path:
        return {"status": "error", "message": "Missing project_path in payload"}

    request = BuildRequest(
        project_path=project_path,
        max_iterations=payload.get("max_iterations", 5),
        incremental=payload.get("incremental", True),
        target_modules=payload.get("target_modules")
    )

    builder = SoftwareBuilder(project_path)
    try:
        report = await builder.run_build(request)

        # Save report to state store for traceability
        state = state_store.get_state()
        if "build_history" not in state:
            state["build_history"] = []
        state["build_history"].append(report.model_dump(mode='json'))
        state_store._save()

        return {
            "status": "success",
            "result": report.model_dump(mode='json')
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
