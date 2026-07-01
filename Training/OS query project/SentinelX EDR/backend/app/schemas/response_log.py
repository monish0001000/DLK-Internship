from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class ResponseActionRequest(BaseModel):
    action_type: str
    target: str
    endpoint_id: str
    execution_mode: str = "simulation" # live or simulation
    reason: Optional[str] = None

class ResponseLogResponse(BaseModel):
    id: int
    endpoint_id: str
    user: str
    action_requested: str
    execution_mode: str
    status: str
    reason: Optional[str] = None
    timestamp: datetime
    
    class Config:
        from_attributes = True
