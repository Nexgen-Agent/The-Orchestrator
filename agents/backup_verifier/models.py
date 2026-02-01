from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime

class FileHash(BaseModel):
    file_path: str
    sha256: str

class VerificationReport(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.now)
    backup_id: str
    archive_path: str
    is_archive_corrupt: bool
    corruption_details: Optional[str] = None
    files_verified: int
    mismatched_files: List[str] = Field(default_factory=list)
    missing_files: List[str] = Field(default_factory=list)
    status: str # "Verified", "Mismatched", "Corrupt"

class GlobalVerificationReport(BaseModel):
    reports: List[VerificationReport]
    summary: Dict[str, Any]
