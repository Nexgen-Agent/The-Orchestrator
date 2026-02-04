from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from agents.human_control_interface.control import HumanControlInterface
from agents.human_control_interface.models import ApprovalRequest, ApprovalStatus

router = APIRouter(prefix="/human-control", tags=["human-control"])
control = HumanControlInterface()

@router.get("/approvals/pending", response_model=List[ApprovalRequest])
async def get_pending_approvals():
    return control.get_pending_approvals()

@router.post("/approvals/{request_id}/approve")
async def approve_request(request_id: str, approver: str = "admin", reason: Optional[str] = None):
    try:
        return control.approve_request(request_id, approver, reason)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/approvals/{request_id}/reject")
async def reject_request(request_id: str, approver: str = "admin", reason: Optional[str] = None):
    try:
        return control.reject_request(request_id, approver, reason)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/pause")
async def pause_orchestration():
    control.set_pause(True)
    return {"status": "success", "message": "Orchestration paused"}

@router.post("/resume")
async def resume_orchestration():
    control.set_pause(False)
    return {"status": "success", "message": "Orchestration resumed"}

@router.post("/emergency-stop")
async def emergency_stop():
    control.set_emergency_stop(True)
    return {"status": "success", "message": "Emergency stop activated"}

@router.get("/controls")
async def get_controls():
    return control.get_controls()

@router.post("/toggle-agent")
async def toggle_agent(agent_name: str, enabled: bool):
    control.toggle_agent(agent_name, enabled)
    return {"status": "success", "message": f"Agent {agent_name} toggled to {enabled}"}

@router.get("/agent-toggles")
async def get_agent_toggles():
    return control.get_agent_toggles()

@router.post("/rollback/{backup_id}")
async def rollback(backup_id: str):
    from fog.core.backup import backup_manager
    try:
        backup_manager.rollback(backup_id)
        return {"status": "success", "message": f"Rolled back to {backup_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/dispatch-task")
async def dispatch_task(task: Dict[str, Any]):
    from fog.core.engine import orchestration_engine
    from fog.models.task import TaskPacket
    try:
        task_packet = TaskPacket(**task)
        await orchestration_engine.submit_task(task_packet)
        return {"status": "success", "task_id": task_packet.task_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
