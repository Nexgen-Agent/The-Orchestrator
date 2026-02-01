from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class ModuleRole(str, Enum):
    CORE = "core"
    UTILITY = "utility"
    API = "api"
    MODEL = "model"
    AGENT = "agent"
    UNKNOWN = "unknown"

class LogicAnalysis(BaseModel):
    summary: str = Field(description="Human-readable summary of the module's code.")
    purpose: str = Field(description="The primary purpose or goal of the module.")
    role: ModuleRole = Field(description="Classification of the module's role in the system.")
    risk_complexity_score: int = Field(ge=1, le=10, description="Score from 1-10 representing code risk and complexity.")
    key_logic_points: List[str] = Field(default_factory=list, description="List of key logic points or algorithms identified.")

class SummarizationOutput(BaseModel):
    file_path: str
    analysis: LogicAnalysis
