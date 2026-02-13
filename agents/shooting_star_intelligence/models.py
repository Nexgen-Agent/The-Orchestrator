from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

class IntelligenceSource(BaseModel):
    source_url: str
    reliability_score: float
    topic_tags: List[str] = []
    solution_type: str

class InnovationOpportunity(BaseModel):
    title: str
    description: str
    impact_score: float
    feasibility_score: float

class CapabilityProgress(BaseModel):
    agent_name: str
    version: str
    capability_percentage: float
    deployment_probability: float
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class IntelligenceReport(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    agent_name: str
    version: str
    capability_percentage: float
    deployment_probability: float
    innovation_opportunities: List[InnovationOpportunity] = []
    optimization_actions: List[str] = []
    learning_sources: List[IntelligenceSource] = []
    status: str # "ready" or "not_ready"
    notes: Optional[str] = None

class SystemReadiness(BaseModel):
    overall_readiness: float
    module_progress: List[CapabilityProgress] = []
    historical_improvement: List[Dict[str, Any]] = []
