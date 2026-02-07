from typing import Dict, Any
from agents.meta_agent_trainer.engine import MetaAgentTrainerEngine
from agents.meta_agent_trainer.models import AgentBlueprint

async def handle_task(task_packet: Dict[str, Any]) -> Dict[str, Any]:
    """
    Orchestration handler for Meta-Agent Trainer Engine (MATE).
    """
    payload = task_packet.get("payload", {})
    action = payload.get("action")
    engine = MetaAgentTrainerEngine()

    try:
        if action == "generate":
            blueprint_data = payload.get("blueprint")
            if not blueprint_data:
                return {"status": "error", "message": "Missing blueprint data"}
            blueprint = AgentBlueprint(**blueprint_data)
            agent_dir = engine.generate_agent_from_blueprint(blueprint)
            return {"status": "success", "agent_dir": agent_dir}

        elif action == "train":
            agent_name = payload.get("agent_name")
            project_path = payload.get("project_path")
            if not agent_name or not project_path:
                return {"status": "error", "message": "Missing agent_name or project_path"}
            report = await engine.simulate_training(agent_name, project_path)
            return {"status": "success", "result": report.model_dump(mode='json')}

        elif action == "optimize":
            agent_dir = payload.get("agent_dir")
            if not agent_dir:
                return {"status": "error", "message": "Missing agent_dir"}
            actions = engine.optimize_agent_code(agent_dir)
            return {"status": "success", "optimization_actions": actions}

        elif action == "evolve_self":
            result = engine.evolve_trainer()
            return {"status": "success", "result": result}

        elif action == "ingest":
            query = payload.get("query", "open-source agentic frameworks 2025")
            result = await engine.ingest_knowledge(query)
            return {"status": "success", "result": result}

        else:
            return {"status": "error", "message": f"Unknown action: {action}"}

    except Exception as e:
        return {"status": "error", "message": str(e)}
