from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

class EvolutionProposal(BaseModel):
    proposal_id: str = Field(default_factory=lambda: str(datetime.now().timestamp()))
    change_type: str # e.g., "merge", "split", "refactor", "param_tuning"
    target_component: str
    description: str
    expected_improvement: str
    risk_score: float # 0.0 to 1.0
    confidence_score: float # 0.0 to 1.0

class EvolutionReport(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    agent_name: str
    module_changes: List[str] = []
    workflow_optimizations: List[str] = []
    performance_delta: Dict[str, Any] = {}
    risk_assessment: Dict[str, Any] = {}
    success: bool = False

class AuditReport(BaseModel):
    agent: str
    change_type: str
    expected_improvement: str
    risk_score: float
    applied_successfully: bool = False
    rollback_triggered: bool = False
    details: Optional[str] = None

class EvolutionHistory(BaseModel):
    history: List[AuditReport] = []
