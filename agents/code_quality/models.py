from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class FunctionMetrics(BaseModel):
    name: str
    line_number: int
    length: int
    complexity: int
    nesting_depth: int
    warnings: List[str] = Field(default_factory=list)

class FileRiskReport(BaseModel):
    file_path: str
    score: int = Field(ge=0, le=100, description="Overall quality score, 100 is best.")
    cyclomatic_complexity: int
    unused_imports: List[str]
    missing_try_except: List[str] = Field(default_factory=list, description="List of risky operations missing error handling.")
    max_nesting_depth: int
    function_reports: List[FunctionMetrics]
    risk_level: str # Low, Medium, High, Critical

class ProjectQualityReport(BaseModel):
    root_path: str
    average_score: float
    files: List[FileRiskReport]
    summary_stats: Dict[str, int]
