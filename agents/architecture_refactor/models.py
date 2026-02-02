from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class RefactorType(str, Enum):
    SPLIT_MODULE = "split_module"
    MERGE_MODULES = "merge_modules"
    MOVE_FUNCTION = "move_function"
    MOVE_CLASS = "move_class"
    FIX_CIRCULAR_DEPENDENCY = "fix_circular_dependency"
    DECOUPLE_MODULES = "decouple_modules"

class RefactorSuggestion(BaseModel):
    id: str
    type: RefactorType
    target: str = Field(..., description="Module or component to be refactored")
    reason: str
    description: str
    impact_score: int = Field(ge=1, le=10, description="Estimated positive impact on architecture")

class ModuleMove(BaseModel):
    item_name: str
    source_module: str
    target_module: str

class RefactorPlan(BaseModel):
    project_path: str
    suggestions: List[RefactorSuggestion]
    planned_moves: List[ModuleMove]
    summary: str
