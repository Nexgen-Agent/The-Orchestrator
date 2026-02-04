from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid

class Severity(str):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

class Issue(BaseModel):
    issue_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    module_name: str
    file_path: str
    line_number: Optional[int] = None
    severity: str # Severity
    issue_type: str # "Syntax", "Runtime", "Security", "Dependency", "SafePattern"
    description: str
    evidence: Optional[str] = None

class ProposedFix(BaseModel):
    fix_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    issue_id: str
    description: str
    code_diff: Optional[str] = None
    safety_rating: str # "Safe", "NeedsReview", "Risky"

class DebugReport(BaseModel):
    debug_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    project_path: str
    issues: List[Issue] = []
    proposed_fixes: List[ProposedFix] = []
    status: str = "Pending"
    validation_passes: int = 0
    summary: str = ""

class DebugRequest(BaseModel):
    project_path: str
    auto_fix: bool = False
    validation_rounds: int = 3
    simulation_report_id: Optional[str] = None
