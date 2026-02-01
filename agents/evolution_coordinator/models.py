from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class EvolutionStep(BaseModel):
    step_id: str
    target_agent: str
    improvement_type: str # "Performance", "Accuracy", "Safety", "Stability"
    description: str
    status: str # "Pending", "Applied", "RolledBack", "Failed"
    backup_id: Optional[str] = None
    applied_at: Optional[datetime] = None

class ImprovementCycle(BaseModel):
    cycle_id: str
    triggered_at: datetime = Field(default_factory=datetime.now)
    analysis_period_start: datetime
    analysis_period_end: datetime
    steps: List[EvolutionStep]
    overall_status: str

class EvolutionReport(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.now)
    active_cycles: List[ImprovementCycle]
    history: List[EvolutionStep]
    ecosystem_health_score: int = Field(ge=0, le=100)
