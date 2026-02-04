from typing import Dict, List, Any, Optional
from datetime import datetime
from agents.human_control_interface.models import ApprovalRequest, ApprovalStatus, OrchestrationControl, AgentToggle
from fog.core.state import state_store
from fog.core.logging import logger
from fog.models.task import TaskPacket, TaskStatus

class HumanControlInterface:
    def __init__(self):
        self._ensure_state_keys()

    def _ensure_state_keys(self):
        state = state_store.get_state()
        if "approvals" not in state:
            state["approvals"] = {}
        if "controls" not in state:
            state["controls"] = {"is_paused": False, "emergency_stop": False}
        if "agent_toggles" not in state:
            state["agent_toggles"] = {}
        state_store._save()

    def request_approval(self, task: TaskPacket, requester: str) -> ApprovalRequest:
        request = ApprovalRequest(
            task_id=task.task_id,
            requester=requester,
            details=task.model_dump(mode='json')
        )
        state = state_store.get_state()
        state["approvals"][request.request_id] = request.model_dump(mode='json')
        state_store._save()
        logger.info("APPROVAL_REQUESTED", {"request_id": request.request_id, "task_id": task.task_id})
        return request

    def get_pending_approvals(self) -> List[ApprovalRequest]:
        state = state_store.get_state()
        approvals = state.get("approvals", {})
        return [ApprovalRequest(**a) for a in approvals.values() if a["status"] == ApprovalStatus.PENDING]

    def approve_request(self, request_id: str, approver: str, reason: Optional[str] = None):
        state = state_store.get_state()
        if request_id not in state["approvals"]:
            raise ValueError(f"Approval request {request_id} not found")

        request_data = state["approvals"][request_id]
        request = ApprovalRequest(**request_data)
        request.status = ApprovalStatus.APPROVED
        request.approver = approver
        request.approval_timestamp = datetime.now()
        request.reason = reason

        state["approvals"][request_id] = request.model_dump(mode='json')
        state_store._save()
        logger.info("APPROVAL_GRANTED", {"request_id": request_id, "approver": approver})
        return request

    def reject_request(self, request_id: str, approver: str, reason: Optional[str] = None):
        state = state_store.get_state()
        if request_id not in state["approvals"]:
            raise ValueError(f"Approval request {request_id} not found")

        request_data = state["approvals"][request_id]
        request = ApprovalRequest(**request_data)
        request.status = ApprovalStatus.REJECTED
        request.approver = approver
        request.approval_timestamp = datetime.now()
        request.reason = reason

        state["approvals"][request_id] = request.model_dump(mode='json')
        state_store._save()
        logger.info("APPROVAL_REJECTED", {"request_id": request_id, "approver": approver})
        return request

    def set_pause(self, paused: bool):
        state = state_store.get_state()
        state["controls"]["is_paused"] = paused
        state_store._save()
        logger.info("ORCHESTRATION_PAUSE_TOGGLED", {"is_paused": paused})

    def set_emergency_stop(self, stop: bool):
        state = state_store.get_state()
        state["controls"]["emergency_stop"] = stop
        state_store._save()
        logger.info("EMERGENCY_STOP_TOGGLED", {"emergency_stop": stop})

    def toggle_agent(self, agent_name: str, enabled: bool):
        state = state_store.get_state()
        state["agent_toggles"][agent_name] = enabled
        state_store._save()
        logger.info("AGENT_TOGGLED", {"agent_name": agent_name, "enabled": enabled})

    def get_controls(self) -> Dict[str, Any]:
        state = state_store.get_state()
        return state.get("controls", {"is_paused": False, "emergency_stop": False})

    def get_agent_toggles(self) -> Dict[str, bool]:
        state = state_store.get_state()
        return state.get("agent_toggles", {})
