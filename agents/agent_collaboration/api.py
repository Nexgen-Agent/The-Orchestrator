from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from agents.agent_collaboration.collaboration import CollaborationManager
from agents.agent_collaboration.models import (
    CollaborationRequest, TaskConflict, MultiAgentWorkflow
)
from fog.models.task import TaskPacket

router = APIRouter(prefix="/collaboration", tags=["collaboration"])
manager = CollaborationManager()

@router.post("/request-help", response_model=CollaborationRequest)
async def request_help(task_id: str, requester: str, target: str, payload: Dict[str, Any] = {}):
    return manager.request_help(task_id, requester, target, payload)

@router.get("/detect-conflicts", response_model=List[TaskConflict])
async def detect_conflicts():
    return manager.detect_conflicts()

@router.post("/workflows", response_model=MultiAgentWorkflow)
async def create_workflow(name: str, tasks: List[TaskPacket]):
    return manager.create_workflow(name, tasks)

@router.post("/merge-outputs")
async def merge_outputs(task_ids: List[str]):
    return manager.merge_outputs(task_ids)

@router.get("/requests")
async def get_requests():
    from fog.core.state import state_store
    state = state_store.get_state()
    return state.get("collaboration_requests", {})
