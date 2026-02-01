from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum

class RiskSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SecurityRisk(BaseModel):
    category: str
    severity: RiskSeverity
    description: str
    line_number: Optional[int] = None
    evidence: Optional[str] = None

class UnsafePattern(BaseModel):
    pattern_name: str
    severity: RiskSeverity
    description: str
    line_number: int

class SecurityReport(BaseModel):
    file_path: str
    overall_risk_level: RiskSeverity
    risks_detected: List[SecurityRisk]
    unsafe_patterns: List[UnsafePattern]
    risky_dependencies: List[str] = Field(default_factory=list)

class ProjectSecurityReport(BaseModel):
    root_path: str
    reports: List[SecurityReport]
    summary: Dict[str, int]
