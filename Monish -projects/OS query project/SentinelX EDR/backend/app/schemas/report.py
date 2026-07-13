"""
SentinelX EDR - Report Schemas
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class ReportGenerate(BaseModel):
    investigation_id: Optional[str] = None
    case_id: Optional[str] = None
    report_type: str  # incident, executive, hunt

class ReportResponse(BaseModel):
    id: str
    investigation_id: Optional[str] = None
    case_id: Optional[str] = None
    title: str
    report_type: str
    content_markdown: str
    generated_by: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
