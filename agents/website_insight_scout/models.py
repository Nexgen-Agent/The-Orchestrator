from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

class UIElement(BaseModel):
    tag: str
    id: Optional[str] = None
    classes: List[str] = []
    text: Optional[str] = None
    attributes: Dict[str, str] = {}
    bounding_box: Dict[str, float] = {}
    styles: Dict[str, str] = {}

class UIHierarchy(BaseModel):
    elements: List[UIElement]

class DesignPatterns(BaseModel):
    colors: List[str]
    typography: List[str]
    spacing: List[str]

class MarketingPsychology(BaseModel):
    ctas: List[str]
    persuasion_techniques: List[str]
    engagement_loops: List[str]
    attention_hierarchy: List[str]

class ArchitecturalInsights(BaseModel):
    logic_patterns: List[str]
    reusable_components: List[str]
    optimizations: List[str]

class WebsiteAnalysisResult(BaseModel):
    url: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    ui_hierarchy: Optional[UIHierarchy] = None
    design_patterns: Optional[DesignPatterns] = None
    marketing_psychology: Optional[MarketingPsychology] = None
    architectural_insights: Optional[ArchitecturalInsights] = None
    screenshots: List[str] = []
    heatmap_path: Optional[str] = None
    ui_graph_path: Optional[str] = None
    status: str = "completed"
