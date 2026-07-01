"""
SentinelX EDR - Detection Rule Schemas
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class DetectionRuleBase(BaseModel):
    name: str
    description: Optional[str] = None
    rule_type: str
    content: str
    severity: Optional[str] = "medium"
    mitre_ids: Optional[str] = None
    author: Optional[str] = None

class DetectionRuleCreate(DetectionRuleBase):
    source: Optional[str] = "imported"

class DetectionRuleUpdate(BaseModel):
    is_enabled: Optional[bool] = None
    severity: Optional[str] = None
    content: Optional[str] = None

class DetectionRuleResponse(DetectionRuleBase):
    id: str
    is_enabled: bool
    source: str
    total_matches: int
    false_positive_count: int
    last_matched_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class RuleImport(BaseModel):
    rule_content: str
    rule_type: str
