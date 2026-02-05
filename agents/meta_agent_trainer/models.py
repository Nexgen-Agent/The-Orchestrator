from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

class AgentBlueprint(BaseModel):
    agent_name: str
    version: str = "1.0.0"
    base_module: str
    required_capabilities: List[str] = []
    constraints: List[str] = []

class TrainingReport(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    agent_name: str
    training_module: str
    compatibility_score: float
    performance_metrics: Dict[str, Any] = {}
    optimization_actions: List[str] = []
    success: bool = False
    rollback_triggered: bool = False

class AuditReport(BaseModel):
    agent: str
    version: str
    training_phase: str
    compatibility_score: float
    expected_improvement: str
    risk_score: float
    deployed_successfully: bool = False
    rollback_triggered: bool = False
    details: Optional[str] = None

class MATEHistory(BaseModel):
    training_history: List[TrainingReport] = []
    audit_history: List[AuditReport] = []
    blueprints: List[AgentBlueprint] = []
