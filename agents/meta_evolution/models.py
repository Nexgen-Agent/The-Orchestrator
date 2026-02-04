from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

class EcosystemSnapshot(BaseModel):
    snapshot_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.now)
    num_agents: int
    num_tasks: int
    agent_distribution: Dict[str, int] # agent_name -> task_count
    total_success_rate: float
    avg_latency: float = 0.0

class StructuralUpgrade(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    rationale: str
    estimated_impact: str # e.g., "High", "Medium", "Low"

class AgentMergeSplitSuggestion(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    suggestion_type: str # "Merge" or "Split"
    target_agents: List[str]
    reason: str
    proposed_action: str

class TrendAnalysis(BaseModel):
    metric: str
    growth_rate: float
    trend_direction: str # "Increasing", "Decreasing", "Stable"
    observation: str

class EvolutionStrategy(BaseModel):
    strategy_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.now)
    trends: List[TrendAnalysis]
    upgrades: List[StructuralUpgrade]
    agent_changes: List[AgentMergeSplitSuggestion]
    summary: str
