from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class ThreatHuntQuery(BaseModel):
    table: str
    filters: Optional[Dict[str, str]] = None
    time_range: str = "24h" # 1h, 24h, 7d
    limit: int = 100

class ThreatHuntSaveRequest(BaseModel):
    name: str
    description: Optional[str] = None
    query: ThreatHuntQuery

class SavedHuntResponse(ThreatHuntSaveRequest):
    id: int
    
    class Config:
        from_attributes = True

class ThreatHuntHistory(BaseModel):
    id: int
    query_text: str # A readable string of the query
    timestamp: str
    user: str
    
    class Config:
        from_attributes = True
