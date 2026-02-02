from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

class SimulationConfig(BaseModel):
    project_path: str
    task_description: str
    isolated_run: bool = True
    timeout_seconds: int = 30
    check_unsafe_patterns: bool = True

class SafeCheck(BaseModel):
    check_name: str
    passed: bool
    details: Optional[str] = None

class SimulationResult(BaseModel):
    success: bool
    logs: List[str]
    conflicts: List[str]
    side_effects: List[str]
    safety_checks: List[SafeCheck]

class SimulationReport(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    config: SimulationConfig
    result: SimulationResult
    summary: str
    verdict: str # "Safe", "Risky", "Unsafe", "Failed"
