from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime
import uuid

class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class ApprovalRequest(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_id: str
    requester: str
    status: ApprovalStatus = ApprovalStatus.PENDING
    timestamp: datetime = Field(default_factory=datetime.now)
    details: Dict[str, Any] = {}
    approver: Optional[str] = None
    approval_timestamp: Optional[datetime] = None
    reason: Optional[str] = None

class OrchestrationControl(BaseModel):
    is_paused: bool = False
    emergency_stop: bool = False

class AgentToggle(BaseModel):
    agent_name: str
    enabled: bool
