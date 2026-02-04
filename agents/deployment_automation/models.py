from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime
import uuid

class DeploymentStatus(str, Enum):
    PENDING = "pending"
    BUILDING = "building"
    PUSHING = "pushing"
    DEPLOYING = "deploying"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"

class DeploymentAction(BaseModel):
    action_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.now)
    action_type: str # build, push, deploy, rollback
    status: str = "Pending"
    logs: List[str] = []

class DeploymentManifest(BaseModel):
    service_name: str
    image_tag: str
    env_vars: Dict[str, str] = {}
    replicas: int = 1
    ports: List[int] = [8000]

class DeploymentReport(BaseModel):
    deployment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.now)
    project_path: str
    status: DeploymentStatus = DeploymentStatus.PENDING
    manifest: Optional[DeploymentManifest] = None
    actions: List[DeploymentAction] = []
    error_message: Optional[str] = None
