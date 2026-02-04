import asyncio
from typing import Dict, Any
from agents.learning_feedback.feedback import LearningFeedbackAgent
from fog.models.task import TaskPacket

async def handle_task(task_packet_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Orchestration handler for Autonomous Learning Feedback Agent.
    """
    agent = LearningFeedbackAgent()
    task_packet = TaskPacket(**task_packet_dict)

    action = task_packet.payload.get("action", "analyze")

    if action == "analyze":
        report = agent.analyze_performance()
        if task_packet.payload.get("feed_to_evolution", True):
            agent.feed_to_evolution_coordinator(report)

        return {
            "status": "success",
            "result": report.model_dump(mode='json')
        }
    elif action == "get_memory":
        return {
            "status": "success",
            "result": agent.memory.model_dump(mode='json')
        }
    else:
        return {"status": "error", "message": f"Unknown action: {action}"}
