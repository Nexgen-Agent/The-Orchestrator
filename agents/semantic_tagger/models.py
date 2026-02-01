from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class TagCategory(str, Enum):
    BUSINESS = "business"
    PSYCHOLOGY = "psychology"
    PHILOSOPHY = "philosophy"

class IntentTag(BaseModel):
    category: TagCategory
    tag_name: str
    confidence: float = Field(ge=0.0, le=1.0)
    description: str

class SemanticAnalysis(BaseModel):
    file_path: Optional[str] = None
    tags: List[IntentTag]
    decision_rules_detected: List[str] = Field(default_factory=list)
    persuasion_logic_detected: List[str] = Field(default_factory=list)
    business_flows_detected: List[str] = Field(default_factory=list)
    behavioral_triggers_detected: List[str] = Field(default_factory=list)

class TaggingOutput(BaseModel):
    status: str
    analysis: SemanticAnalysis
