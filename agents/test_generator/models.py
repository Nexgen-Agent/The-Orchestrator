from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class TestStub(BaseModel):
    name: str
    target_name: str
    content: str

class CoverageRecommendation(BaseModel):
    module_name: str
    missing_tests: List[str]
    importance: str # e.g., "High", "Medium", "Low"

class TestFile(BaseModel):
    file_path: str
    content: str

class TestGenerationReport(BaseModel):
    project_path: str
    generated_files: List[TestFile]
    recommendations: List[CoverageRecommendation]
    summary: str
