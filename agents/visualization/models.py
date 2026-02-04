from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime
import uuid

class GraphType(str, Enum):
    DEPENDENCY = "dependency"
    AGENT_INTERACTION = "agent_interaction"
    ORCHESTRATION_FLOW = "orchestration_flow"

class VisualizationRequest(BaseModel):
    graph_type: GraphType
    data: Dict[str, Any]
    output_format: str = "png" # "png", "json", "both"
    title: Optional[str] = None

class VisualizationOutput(BaseModel):
    visualization_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.now)
    graph_type: GraphType
    png_path: Optional[str] = None
    json_data: Optional[Dict[str, Any]] = None
