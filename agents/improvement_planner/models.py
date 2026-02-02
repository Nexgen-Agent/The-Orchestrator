from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

class WeakArea(BaseModel):
    target_agent: str
    metric: str
    current_value: float
    threshold: float
    reason: str

class ImprovementStrategy(BaseModel):
    id: str
    type: str # "Refactor", "Configuration", "Scaling", "Training"
    description: str
    expected_outcome: str
    priority: int = Field(ge=1, le=10)

class AgentUpgrade(BaseModel):
    agent_name: str
    change_description: str
    target_version: Optional[str] = None

class ImprovementPlan(BaseModel):
    plan_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    weak_areas: List[WeakArea]
    strategies: List[ImprovementStrategy]
    suggested_upgrades: List[AgentUpgrade]
    summary: str
