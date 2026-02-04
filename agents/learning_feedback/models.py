from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid

class LearningInsight(BaseModel):
    insight_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    category: str # e.g., "latency", "failure_pattern", "resource_utilization"
    description: str
    evidence: Dict[str, Any]
    impact_score: int = Field(ge=1, le=10)

class RuleUpdateSuggestion(BaseModel):
    suggestion_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    original_rule: Optional[str] = None
    suggested_update: str
    rationale: str
    affected_components: List[str]

class LearningMemory(BaseModel):
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    insights: List[LearningInsight] = []
    applied_rules: List[RuleUpdateSuggestion] = []
    metrics_summary: Dict[str, Any] = {}

class FeedbackReport(BaseModel):
    report_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    insights: List[LearningInsight]
    suggestions: List[RuleUpdateSuggestion]
    summary: str
