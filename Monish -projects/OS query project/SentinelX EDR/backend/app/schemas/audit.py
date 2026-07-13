from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AuditLogCreate(BaseModel):
    user: Optional[str] = "System"
    ip_address: Optional[str] = None
    action: str
    object: Optional[str] = None
    status: str
    execution_time_ms: Optional[float] = None

class AuditLogResponse(AuditLogCreate):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True
