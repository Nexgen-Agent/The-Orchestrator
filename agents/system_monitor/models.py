from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class AgentHealth(BaseModel):
    name: str
    status: str # "Healthy", "Unhealthy", "Unknown"
    uptime_seconds: float
    last_heartbeat: Optional[datetime] = None

class TaskMetrics(BaseModel):
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    success_rate: float
    average_retries: float

class FailurePattern(BaseModel):
    pattern_type: str
    description: str
    affected_components: List[str]
    occurrence_count: int

class ResourceUsage(BaseModel):
    cpu_percent: float
    memory_percent: float
    disk_usage_percent: float

class SystemHealthReport(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.now)
    agents: List[AgentHealth]
    overall_task_metrics: TaskMetrics
    resource_usage: ResourceUsage
    detected_patterns: List[FailurePattern]
    system_status: str # "Nominal", "Degraded", "Critical"
