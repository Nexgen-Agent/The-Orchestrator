from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

class DependencyIssue(BaseModel):
    module: str
    file_path: Optional[str] = None
    issue_type: str = "missing" # e.g., missing, broken
    severity: str = "High"

class RepairSuggestion(BaseModel):
    module: str
    suggested_package: str
    action: str = "pip install"
    confidence: float = 0.9

class RepairLogEntry(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    action: str
    target: str
    status: str
    message: str

class RepairReport(BaseModel):
    project_path: str
    issues_found: List[DependencyIssue]
    suggestions: List[RepairSuggestion]
    repairs_performed: List[RepairLogEntry]
    summary: str
    status: str # Success, Partial, Failed
