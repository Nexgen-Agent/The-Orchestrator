from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class TaskType(str, Enum):
    ANALYSIS = "analysis"
    MODIFICATION = "modification"
    VERIFICATION = "verification"
    DEPLOYMENT = "deployment"

class TaskPacket(BaseModel):
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    system_name: str
    module_name: str
    task_type: TaskType
    constraints: List[str] = []
    dependencies: List[str] = []
    business_rules: List[str] = []
    philosophy_tags: List[str] = []
    backup_id: Optional[str] = None
    priority: int = 0
    timestamp: datetime = Field(default_factory=datetime.now)
    payload: Dict[str, Any] = {}
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    retries: int = 0
    max_retries: int = 3

class AgentConfig(BaseModel):
    name: str
    endpoint: str
    handler_type: str = "http" # e.g., "http", "mock"

class ProjectInput(BaseModel):
    project_path: str
    description: Optional[str] = None
