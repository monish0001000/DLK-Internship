"""
SentinelX EDR - Investigation Schemas
"""

from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional, Any, Dict, List
from datetime import datetime
import json

class InvestigationTrigger(BaseModel):
    alert_id: int

class InvestigationResponse(BaseModel):
    id: str
    alert_id: int
    pipeline_results: Optional[Dict[str, Any]] = None
    summary: Optional[str] = None
    root_cause: Optional[str] = None
    risk_score: Optional[float] = None
    risk_level: Optional[str] = None
    mitre_mapping: Optional[List[Dict[str, Any]]] = None
    timeline: Optional[List[Dict[str, Any]]] = None
    recommendations: Optional[str] = None
    response_plan: Optional[Dict[str, Any]] = None
    suggested_rules: Optional[List[Dict[str, Any]]] = None
    ai_model: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator('pipeline_results', 'mitre_mapping', 'timeline', 'response_plan', 'suggested_rules', mode='before')
    @classmethod
    def parse_json(cls, value):
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return None
        return value
