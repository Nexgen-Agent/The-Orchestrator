from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid

class BuildStep(BaseModel):
    step_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    module_name: str
    action: str # "analyze", "compile", "improve", "verify"
    status: str # "Pending", "InProgress", "Completed", "Failed"
    logs: List[str] = []
    iterations: int = 0

class ModuleBuildInfo(BaseModel):
    module_name: str
    file_path: str
    dependencies: List[str] = []
    status: str = "Pending"
    total_iterations: int = 0
    build_steps: List[BuildStep] = []

class BuildReport(BaseModel):
    build_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_path: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "Pending"
    modules: Dict[str, ModuleBuildInfo] = {}
    total_modules: int = 0
    completed_modules: int = 0
    failed_modules: int = 0
    performance_metrics: Dict[str, Any] = {}
    friction_reports: List[Dict[str, Any]] = []
    summary: str = ""

class BuildRequest(BaseModel):
    project_path: str
    target_modules: Optional[List[str]] = None
    max_iterations: int = 5
    incremental: bool = True
