"""
SentinelX EDR - Alert Schemas
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class AlertBase(BaseModel):
    endpoint_id: str
    title: str
    description: Optional[str] = None
    severity: str
    rule_name: Optional[str] = None
    rule_type: Optional[str] = None
    rule_id: Optional[str] = None
    mitre_tactic: Optional[str] = None
    mitre_technique: Optional[str] = None
    mitre_technique_name: Optional[str] = None
    evidence: Optional[str] = None
    detection_latency_ms: Optional[float] = None

class AlertCreate(AlertBase):
    pass

class AlertUpdate(BaseModel):
    status: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

class AlertResponse(AlertBase):
    id: int
    status: str
    detected_at: datetime
    acknowledged_at: Optional[datetime]
    resolved_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)

class AlertFilter(BaseModel):
    severity: Optional[str] = None
    status: Optional[str] = None
    rule_type: Optional[str] = None
    endpoint_id: Optional[str] = None
    mitre_technique: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = 50
    offset: int = 0
