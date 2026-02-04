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

# Advanced Multi-Site Models

class PerformanceScore(BaseModel):
    visual_appeal: float # 0-100
    efficiency: float    # 0-100
    ux_flow: float       # 0-100
    overall: float       # 0-100

class RankedElement(BaseModel):
    element: UIElement
    score: PerformanceScore
    priority: int        # 1-10
    is_core: bool

class MultiSiteComparison(BaseModel):
    urls: List[str]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    rankings: Dict[str, float] # URL -> overall score
    top_elements: List[RankedElement]
    common_patterns: List[str]

class ReplicationManifest(BaseModel):
    source_url: str
    target_platform: str = "web"
    components: List[RankedElement]
    styling_rules: Dict[str, str]
    logic_hints: List[str]
    multi_language_support: bool = False
    language_schema: Dict[str, Any] = {}
