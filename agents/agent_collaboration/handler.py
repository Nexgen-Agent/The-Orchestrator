import asyncio
from typing import Dict, Any, List
from agents.agent_collaboration.collaboration import CollaborationManager
from fog.models.task import TaskPacket

async def handle_task(task_packet_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Orchestration handler for Agent Collaboration Agent.
    """
    manager = CollaborationManager()
    task_packet = TaskPacket(**task_packet_dict)

    action = task_packet.payload.get("action", "coordinate")

    if action == "request_help":
        target = task_packet.payload.get("target_agent")
        help_payload = task_packet.payload.get("help_payload", {})
        request = manager.request_help(
            task_id=task_packet.task_id,
            requester=task_packet.system_name,
            target=target,
            payload=help_payload
        )
        return {
            "status": "success",
            "result": request.model_dump(mode='json')
        }

    elif action == "detect_conflicts":
        conflicts = manager.detect_conflicts()
        return {
            "status": "success",
            "result": [c.model_dump(mode='json') for c in conflicts]
        }

    elif action == "create_workflow":
        name = task_packet.payload.get("workflow_name", "Unnamed Workflow")
        tasks_data = task_packet.payload.get("tasks", [])
        task_packets = [TaskPacket(**t) for t in tasks_data]
        workflow = manager.create_workflow(name, task_packets)
        return {
            "status": "success",
            "result": workflow.model_dump(mode='json')
        }

    elif action == "merge_outputs":
        task_ids = task_packet.payload.get("task_ids", [])
        merged = manager.merge_outputs(task_ids)
        return {
            "status": "success",
            "result": merged
        }

    else:
        return {"status": "error", "message": f"Unknown action: {action}"}
