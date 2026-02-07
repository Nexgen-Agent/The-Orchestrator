from typing import Dict, Any
from agents.shooting_star_intelligence.intelligence import ShootingStarIntelligence

async def handle_task(task_packet: Dict[str, Any]) -> Dict[str, Any]:
    """
    Orchestration handler for Shooting Star Intelligence.
    """
    payload = task_packet.get("payload", {})
    action = payload.get("action")
    agent_name = payload.get("agent_name")
    engine = ShootingStarIntelligence()

    try:
        if action == "track":
            capability = payload.get("capability", 50.0)
            progress = await engine.track_progress(agent_name, capability)
            return {"status": "success", "result": progress.model_dump(mode='json')}

        elif action == "audit":
            project_path = payload.get("project_path")
            if not project_path:
                return {"status": "error", "message": "Missing project_path"}
            report = await engine.perform_readiness_audit(agent_name, project_path)
            return {"status": "success", "result": report.model_dump(mode='json')}

        elif action == "gather":
            intel = await engine.gather_intelligence(agent_name)
            return {"status": "success", "result": [i.model_dump(mode='json') for i in intel]}

        elif action == "evolve":
            project_path = payload.get("project_path")
            await engine.autonomous_evolution_cycle(agent_name, project_path)
            return {"status": "success", "message": f"Evolution cycle triggered for {agent_name}"}

        else:
            return {"status": "error", "message": f"Unknown action: {action}"}

    except Exception as e:
        return {"status": "error", "message": str(e)}
