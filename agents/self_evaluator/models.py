from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

class EvaluationInput(BaseModel):
    agent_name: str
    task_id: str
    success: bool
    execution_time_seconds: float
    error_message: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AgentMetrics(BaseModel):
    total_tasks: int
    success_rate: float
    avg_execution_time: float
    failure_patterns: List[str] = []

class EvaluationReport(BaseModel):
    agent_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metrics: AgentMetrics
    performance_score: int = Field(ge=0, le=100)
    improvement_suggestions: List[str]
    history_depth: int
