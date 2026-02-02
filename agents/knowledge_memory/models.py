from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

class KnowledgeEntry(BaseModel):
    """A piece of knowledge stored in the memory system."""
    id: str = Field(..., description="Unique entry ID")
    title: str = Field(..., description="Short title")
    problem: str = Field(..., description="Problem description")
    solution: str = Field(..., description="Solution or key knowledge")
    tags: List[str] = Field(default_factory=list, description="Categorization tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SearchResult(BaseModel):
    """Result of a search operation."""
    entries: List[KnowledgeEntry]
    count: int
    query: Optional[str] = None
    tags: Optional[List[str]] = None

class MemoryOperationResult(BaseModel):
    """Common result for memory operations."""
    success: bool
    message: str
    entry_id: Optional[str] = None
    data: Optional[Any] = None
