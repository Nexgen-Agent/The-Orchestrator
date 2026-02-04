import asyncio
from typing import Dict, Any
from agents.meta_evolution.analyzer import MetaEvolutionAnalyzer
from fog.models.task import TaskPacket

async def handle_task(task_packet_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Orchestration handler for Meta-System Evolution Agent.
    """
    analyzer = MetaEvolutionAnalyzer()
    task_packet = TaskPacket(**task_packet_dict)

    action = task_packet.payload.get("action", "analyze")

    if action == "analyze":
        strategy = analyzer.propose_evolution()
        return {
            "status": "success",
            "result": strategy.model_dump(mode='json')
        }
    elif action == "snapshot":
        snapshot = analyzer.take_snapshot()
        return {
            "status": "success",
            "result": snapshot.model_dump(mode='json')
        }
    elif action == "trends":
        trends = analyzer.analyze_trends()
        return {
            "status": "success",
            "result": [t.model_dump(mode='json') for t in trends]
        }
    else:
        return {"status": "error", "message": f"Unknown action: {action}"}
