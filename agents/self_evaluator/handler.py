import asyncio
from typing import Dict, Any
from agents.self_evaluator.evaluator import SelfEvaluator
from agents.self_evaluator.models import EvaluationInput

async def handle_task(task_packet: Dict[str, Any]) -> Dict[str, Any]:
    """
    Orchestration handler for FOG.
    Actions: 'log_task', 'evaluate'.
    """
    payload = task_packet.get("payload", {})
    action = payload.get("action", "evaluate")

    evaluator = SelfEvaluator()

    try:
        if action == "log_task":
            # Record a task result
            eval_input = EvaluationInput(
                agent_name=payload.get("agent_name"),
                task_id=payload.get("task_id"),
                success=payload.get("success", True),
                execution_time_seconds=payload.get("execution_time_seconds", 0.0),
                error_message=payload.get("error_message")
            )
            await asyncio.to_thread(evaluator.add_task_result, eval_input)
            return {
                "status": "success",
                "message": f"Task result logged for agent {eval_input.agent_name}"
            }

        elif action == "evaluate":
            # Generate a report for an agent
            agent_name = payload.get("agent_name")
            if not agent_name:
                return {"status": "error", "message": "agent_name is required for evaluate action"}

            report = await asyncio.to_thread(evaluator.evaluate_agent, agent_name)
            if not report:
                return {"status": "error", "message": f"No data found for agent {agent_name}"}

            return {
                "status": "success",
                "result": report.model_dump(mode='json')
            }

        else:
            return {"status": "error", "message": f"Unknown action: {action}"}

    except Exception as e:
        return {"status": "error", "message": str(e)}
