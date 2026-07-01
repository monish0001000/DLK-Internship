"""
SentinelX EDR - Case Schemas
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class CaseBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Optional[str] = "medium"
    assignee: Optional[str] = None

class CaseCreate(CaseBase):
    alert_ids: Optional[List[int]] = None

class CaseUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    assignee: Optional[str] = None
    description: Optional[str] = None

class CaseResponse(CaseBase):
    id: str
    status: str
    created_by: str
    alert_ids: Optional[List[int]] = None
    investigation_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    notes_count: int = 0
    evidence_count: int = 0

    model_config = ConfigDict(from_attributes=True)

class CaseNoteCreate(BaseModel):
    content: str
    author: Optional[str] = "analyst"

class CaseNoteResponse(CaseNoteCreate):
    id: int
    case_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CaseEvidenceCreate(BaseModel):
    evidence_type: str
    title: str
    description: Optional[str] = None
    content: Optional[str] = None
    source: Optional[str] = None

class CaseEvidenceResponse(CaseEvidenceCreate):
    id: int
    case_id: str
    collected_at: datetime

    model_config = ConfigDict(from_attributes=True)
