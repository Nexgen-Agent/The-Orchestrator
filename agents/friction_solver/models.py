from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class SolutionAttempt(BaseModel):
    method: str
    action: Optional[str] = None
    result: str
    success: bool
    details: Optional[str] = None

class FrictionReport(BaseModel):
    error_type: str
    root_cause: str
    solution_attempts: List[SolutionAttempt] = []
    successful_fix: Optional[str] = None
    future_prevention: Optional[str] = None
    confidence_score: float = 0.0

class FrictionSolverConfig(BaseModel):
    project_path: str
    error_message: str
    context_logs: Optional[str] = None
    auto_apply: bool = False
