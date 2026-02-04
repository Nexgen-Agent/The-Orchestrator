from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

class IngestionModule(BaseModel):
    file_path: str
    summary: Optional[str] = None
    tags: List[Dict[str, Any]] = []
    structure: Dict[str, Any] = {}

class IngestionReport(BaseModel):
    ingestion_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.now)
    project_path: str
    modules: List[IngestionModule] = []
    architecture_summary: Optional[str] = None
    dependency_map: Dict[str, Any] = {}
    build_instructions: Dict[str, Any] = {}
    status: str = "Pending"
