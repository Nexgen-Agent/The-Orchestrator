import asyncio
from typing import Dict, Any
from agents.prompt_orchestrator.orchestrator import PromptOrchestrator

async def handle_task(task_packet: Dict[str, Any]) -> Dict[str, Any]:
    """
    Orchestration handler for FOG.
    Expects 'architecture_map' in payload.
    """
    payload = task_packet.get("payload", {})
    architecture_map = payload.get("architecture_map")

    if not architecture_map:
        return {"status": "error", "message": "Missing architecture_map in payload"}

    orchestrator = PromptOrchestrator()

    try:
        # If architecture_map is a JSON string, parse it
        if isinstance(architecture_map, str):
            import json
            architecture_map = json.loads(architecture_map)

        output = orchestrator.orchestrate(architecture_map)

        return {
            "status": "success",
            "result": output.model_dump(mode='json')
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
