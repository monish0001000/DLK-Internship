"""
SentinelX EDR - Endpoint Schemas
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class EndpointBase(BaseModel):
    hostname: str
    ip_address: str
    os_type: str
    os_version: Optional[str] = None
    agent_version: Optional[str] = "1.0.0"
    tags: Optional[str] = None

class EndpointCreate(EndpointBase):
    id: str

class EndpointUpdate(BaseModel):
    status: Optional[str] = None
    is_isolated: Optional[bool] = None
    tags: Optional[str] = None

class EndpointHeartbeat(BaseModel):
    endpoint_id: str
    timestamp: Optional[datetime] = None

class EndpointResponse(EndpointBase):
    id: str
    status: str
    is_isolated: bool
    last_seen: datetime
    registered_at: datetime

    model_config = ConfigDict(from_attributes=True)
