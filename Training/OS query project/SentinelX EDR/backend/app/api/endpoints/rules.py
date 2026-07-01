"""
SentinelX EDR - Rules API
"""

from typing import List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.detection_rule import DetectionRuleResponse, DetectionRuleUpdate, RuleImport
from app.services.rule_marketplace import list_rules, toggle_rule, import_sigma_rule, import_yara_rule, get_rule_stats

router = APIRouter()

@router.get("/", response_model=List[DetectionRuleResponse])
def api_list_rules(rule_type: Optional[str] = None, is_enabled: Optional[bool] = None, db: Session = Depends(get_db)) -> Any:
    return list_rules(db, rule_type=rule_type, is_enabled=is_enabled)

@router.get("/stats")
def api_get_rule_stats(db: Session = Depends(get_db)) -> Any:
    return get_rule_stats(db)

@router.post("/import", response_model=DetectionRuleResponse)
def api_import_rule(data: RuleImport, db: Session = Depends(get_db)) -> Any:
    try:
        if data.rule_type.lower() == "sigma":
            return import_sigma_rule(db, data.rule_content)
        elif data.rule_type.lower() == "yara":
            return import_yara_rule(db, data.rule_content)
        else:
            raise HTTPException(status_code=400, detail="Unsupported rule type")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{rule_id}/toggle", response_model=DetectionRuleResponse)
def api_toggle_rule(rule_id: str, enabled: bool, db: Session = Depends(get_db)) -> Any:
    rule = toggle_rule(db, rule_id, enabled)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule
