from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class MissingDependency(BaseModel):
    module: str
    suggested_package: str

class DeploymentPackage(BaseModel):
    dockerfile_content: str
    requirements_content: str
    startup_script_content: str
    target_files: List[str]

class DeploymentReport(BaseModel):
    project_path: str
    missing_dependencies: List[MissingDependency]
    generated_package: DeploymentPackage
    status: str # "Success", "Warning", "Error"
    summary: str
