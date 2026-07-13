"""
SentinelX EDR - Threat Intel Schemas
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class ThreatIntelBase(BaseModel):
    ioc_type: str
    value: str
    source: Optional[str] = "bundled"
    severity: Optional[str] = "high"
    confidence: Optional[float] = None
    description: Optional[str] = None
    tags: Optional[str] = None

class ThreatIntelCreate(ThreatIntelBase):
    pass

class ThreatIntelResponse(ThreatIntelBase):
    id: int
    is_active: bool
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ThreatIntelBulkImport(BaseModel):
    iocs: List[ThreatIntelCreate]

class FeedSyncRequest(BaseModel):
    feed_name: str  # abuseipdb, otx, malwarebazaar

class FeedSyncResponse(BaseModel):
    feed_name: str
    iocs_added: int
    iocs_updated: int
    status: str
