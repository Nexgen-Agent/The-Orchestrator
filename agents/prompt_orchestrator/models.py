from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ComponentInstruction(BaseModel):
    component_name: str
    purpose: str
    dependencies: List[str]
    build_steps: List[str]
    constraints: List[str]

class StructuredPrompt(BaseModel):
    title: str
    system_role: str
    context: str
    instructions: List[ComponentInstruction]
    output_format: str

class ArchitecturePromptMap(BaseModel):
    project_name: str
    ordered_prompts: List[StructuredPrompt]
    dependency_chain: List[str]
