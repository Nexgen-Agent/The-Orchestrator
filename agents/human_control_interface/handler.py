import asyncio
from typing import Dict, Any
from agents.human_control_interface.control import HumanControlInterface
from fog.models.task import TaskPacket, TaskType
from fog.core.state import state_store
from fog.core.backup import backup_manager

async def handle_task(task_packet_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Orchestration handler for Human Control Interface Agent.
    Handles various control tasks.
    """
    control = HumanControlInterface()
    task_packet = TaskPacket(**task_packet_dict)

    action = task_packet.payload.get("action")

    if action == "request_approval":
        # Usually this would be called by the engine, but it can be a task too
        target_task_dict = task_packet.payload.get("task")
        if not target_task_dict:
            return {"status": "error", "message": "Missing 'task' in payload for request_approval"}

        target_task = TaskPacket(**target_task_dict)
        request = control.request_approval(target_task, requester=task_packet.system_name)

        # We might want to wait here for approval if this is a blocking call
        # But for now, let's just return the request info
        return {
            "status": "success",
            "result": {
                "approval_request_id": request.request_id,
                "status": request.status
            }
        }

    elif action == "pause":
        control.set_pause(True)
        return {"status": "success", "message": "Orchestration paused"}

    elif action == "resume":
        control.set_pause(False)
        return {"status": "success", "message": "Orchestration resumed"}

    elif action == "emergency_stop":
        control.set_emergency_stop(True)
        return {"status": "success", "message": "Emergency stop activated"}

    elif action == "rollback":
        backup_id = task_packet.payload.get("backup_id")
        if not backup_id:
            return {"status": "error", "message": "Missing 'backup_id' in payload for rollback"}
        try:
            backup_manager.rollback(backup_id)
            return {"status": "success", "message": f"Rolled back to {backup_id}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    elif action == "toggle_agent":
        agent_name = task_packet.payload.get("agent_name")
        enabled = task_packet.payload.get("enabled", True)
        if not agent_name:
            return {"status": "error", "message": "Missing 'agent_name' in payload for toggle_agent"}
        control.toggle_agent(agent_name, enabled)
        return {"status": "success", "message": f"Agent {agent_name} toggled to {enabled}"}

    elif action == "dispatch_task":
        # Manual task dispatch
        # This would typically be done via the API, but could be a task too
        new_task_dict = task_packet.payload.get("new_task")
        if not new_task_dict:
            return {"status": "error", "message": "Missing 'new_task' in payload for dispatch_task"}

        # We can't easily submit a task to the engine from here without importing the engine,
        # which might cause circular imports if the engine uses the handler.
        # However, the engine is usually a global instance.
        from fog.core.engine import orchestration_engine
        new_task = TaskPacket(**new_task_dict)
        await orchestration_engine.submit_task(new_task)
        return {"status": "success", "task_id": new_task.task_id}

    else:
        return {"status": "error", "message": f"Unknown action: {action}"}
