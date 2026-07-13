"""
SentinelX EDR - Simulation Schemas
"""

from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import json

class SimulationScenario(BaseModel):
    name: str
    description: str
    attack_type: str
    mitre_techniques: List[str]
    estimated_events: int

class SimulationStart(BaseModel):
    scenario_name: str
    endpoint_id: Optional[str] = None

class SimulationResponse(BaseModel):
    id: str
    scenario_name: str
    scenario_description: Optional[str] = None
    status: str
    endpoint_id: Optional[str] = None
    events_generated: int
    alerts_triggered: int
    rules_matched: Optional[List[str]] = None
    detection_coverage_pct: Optional[int] = None
    results_summary: Optional[Dict[str, Any]] = None
    started_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator('rules_matched', 'results_summary', mode='before')
    @classmethod
    def parse_json(cls, value):
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return None
        return value
