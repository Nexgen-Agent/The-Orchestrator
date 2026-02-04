from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime
import uuid

class ResilienceActionType(str, Enum):
    RESTART_AGENT = "restart_agent"
    RECOVER_TASK = "recover_task"
    TRIGGER_SAFE_MODE = "trigger_safe_mode"
    RETRY_FAILED_TASKS = "retry_failed_tasks"

class ResilienceAction(BaseModel):
    action_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.now)
    action_type: ResilienceActionType
    target: str # agent name or task id
    reason: str
    status: str = "Pending" # Pending, Completed, Failed
    details: Dict[str, Any] = {}

class ResilienceReport(BaseModel):
    report_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.now)
    failing_patterns: List[str]
    actions_taken: List[ResilienceAction]
    recovered_tasks_count: int
    system_status: str
    safe_mode_active: bool
