from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime
import uuid

class CollaborationType(str, Enum):
    HELP_REQUEST = "help_request"
    CONFLICT_RESOLUTION = "conflict_resolution"
    WORKFLOW_COORDINATION = "workflow_coordination"
    OUTPUT_MERGE = "output_merge"

class CollaborationRequest(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.now)
    requester_agent: str
    target_agent: Optional[str] = None
    task_id: str
    collaboration_type: CollaborationType
    payload: Dict[str, Any] = {}
    status: str = "Pending" # Pending, Active, Completed, Failed

class TaskConflict(BaseModel):
    conflict_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_ids: List[str]
    resource: str # e.g., "file:fog/core/engine.py"
    conflict_type: str # e.g., "WRITE_WRITE"
    resolution: Optional[str] = None
    resolved_at: Optional[datetime] = None

class MultiAgentWorkflow(BaseModel):
    workflow_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    tasks: List[str] # List of task_ids
    sequence: List[List[str]] # e.g., [["task1"], ["task2", "task3"], ["task4"]]
    status: str = "Pending"
    created_at: datetime = Field(default_factory=datetime.now)
