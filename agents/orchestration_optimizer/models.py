from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class AgentPerformance(BaseModel):
    agent_name: str
    avg_execution_time_seconds: float
    max_execution_time_seconds: float
    total_tasks_handled: int
    success_rate: float

class FailurePattern(BaseModel):
    error_type: str
    occurrence_count: int
    affected_agents: List[str]
    sample_task_ids: List[str]

class OptimizationSuggestion(BaseModel):
    type: str # "Routing", "Timeout", "Retries", "Agent"
    target: str # e.g., agent name or task type
    reason: str
    recommendation: str

class OptimizationReport(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.now)
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    agent_performance: List[AgentPerformance]
    failure_patterns: List[FailurePattern]
    suggestions: List[OptimizationSuggestion]
    overall_efficiency_score: int = Field(ge=0, le=100)
