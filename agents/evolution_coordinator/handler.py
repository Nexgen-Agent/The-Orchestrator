import asyncio
from typing import Dict, Any
from agents.evolution_coordinator.coordinator import EvolutionCoordinator

async def handle_task(task_packet: Dict[str, Any]) -> Dict[str, Any]:
    """
    Orchestration handler for FOG.
    Triggers an evolution cycle or applies a specific step.
    """
    payload = task_packet.get("payload", {})
    action = payload.get("action", "trigger_cycle")
    project_path = payload.get("project_path")

    coordinator = EvolutionCoordinator()

    try:
        if action == "trigger_cycle":
            cycle = coordinator.trigger_improvement_cycle()
            if not cycle:
                return {"status": "success", "message": "No improvements needed at this time."}
            return {
                "status": "success",
                "result": cycle.model_dump(mode='json')
            }
        elif action == "apply_step":
            step_data = payload.get("step")
            if not step_data or not project_path:
                return {"status": "error", "message": "Missing step data or project_path for apply_step action"}

            # Reconstruct model from dict
            from agents.evolution_coordinator.models import EvolutionStep
            step = EvolutionStep(**step_data)

            await coordinator.apply_evolution_step(step, project_path)

            return {
                "status": "success",
                "result": step.model_dump(mode='json')
            }
        else:
            return {"status": "error", "message": f"Unknown action: {action}"}

    except Exception as e:
        return {"status": "error", "message": str(e)}
