from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

class StyleFingerprint(BaseModel):
    user_id: str
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    formal_score: float = 0.5 # 0 (casual) to 1 (formal)
    energy_level_avg: float = 0.5 # 0 (low) to 1 (high)
    sentence_length_avg: float = 0.0
    punctuation_density: float = 0.0
    slang_usage_freq: float = 0.0
    top_keywords: List[str] = []
    slang_list: List[str] = []

class EnergyMapping(BaseModel):
    energy_level: float
    emotion: str
    urgency: bool
    detected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class InteractionAnalysis(BaseModel):
    text_sample: str
    tone: str
    energy: EnergyMapping
    rhythm: Dict[str, float]
    learned_slang: List[str] = []

class AdaptationParams(BaseModel):
    target_tone: str
    mirroring_ratio: float # 0 to 1
    verbosity_target: str # 'low', 'medium', 'high'
    complexity_target: float # 0 to 1
    humor_allowed: bool = True

class StyleEvolutionReport(BaseModel):
    user_id: str
    period_start: datetime
    period_end: datetime
    changes: Dict[str, Any]
    growth_trends: List[str]
