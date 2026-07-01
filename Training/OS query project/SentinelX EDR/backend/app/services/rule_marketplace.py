"""
SentinelX EDR - Rule Marketplace Service
==========================================
Manages detection rules.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import yaml
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.detection_rule import DetectionRule

def import_sigma_rule(db: Session, yaml_content: str) -> DetectionRule:
    try:
        parsed = yaml.safe_load(yaml_content)
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML: {e}")
        
    title = parsed.get("title", "Unknown Sigma Rule")
    description = parsed.get("description", "")
    severity = parsed.get("level", "medium")
    tags = parsed.get("tags", [])
    mitre_ids = ",".join([t.upper().replace('ATTACK.', '') for t in tags if t.startswith('attack.t')])
    author = parsed.get("author", "Unknown")
    
    rule = DetectionRule(
        name=title,
        description=description,
        rule_type="sigma",
        content=yaml_content,
        severity=severity,
        mitre_ids=mitre_ids,
        author=author,
        source="imported",
        is_enabled=True
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule

def import_yara_rule(db: Session, content: str) -> DetectionRule:
    # Simple extraction of rule name for YARA
    name = "Imported YARA Rule"
    for line in content.split('\n'):
        if line.strip().startswith('rule '):
            name = line.strip().split(' ')[1].strip('{')
            break
            
    rule = DetectionRule(
        name=name,
        description="YARA scanning rule",
        rule_type="yara",
        content=content,
        severity="high",
        source="imported",
        is_enabled=True
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule

def import_ioc_list(db: Session, content: str, ioc_type: str) -> int:
    # In a full implementation, this would parse the content and insert into ThreatIntel table
    # For now, we create a rule object to represent the list
    rule = DetectionRule(
        name=f"Imported IOC List ({ioc_type})",
        description=f"List of malicious {ioc_type} indicators",
        rule_type="ioc_list",
        content=content,
        severity="high",
        source="imported",
        is_enabled=True
    )
    db.add(rule)
    db.commit()
    return len(content.split('\n'))

def list_rules(db: Session, rule_type: Optional[str] = None, is_enabled: Optional[bool] = None, 
               search: Optional[str] = None) -> List[DetectionRule]:
    query = db.query(DetectionRule)
    if rule_type:
        query = query.filter(DetectionRule.rule_type == rule_type)
    if is_enabled is not None:
        query = query.filter(DetectionRule.is_enabled == is_enabled)
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(DetectionRule.name.ilike(search_pattern) | DetectionRule.description.ilike(search_pattern))
        
    return query.order_by(desc(DetectionRule.created_at)).all()

def toggle_rule(db: Session, rule_id: str, enabled: bool) -> Optional[DetectionRule]:
    rule = db.query(DetectionRule).filter(DetectionRule.id == rule_id).first()
    if rule:
        rule.is_enabled = enabled
        db.commit()
        db.refresh(rule)
    return rule

def get_rule_stats(db: Session) -> Dict[str, Any]:
    types = dict(db.query(DetectionRule.rule_type, db.func.count(DetectionRule.id)).group_by(DetectionRule.rule_type).all())
    enabled = db.query(DetectionRule).filter(DetectionRule.is_enabled == True).count()
    disabled = db.query(DetectionRule).filter(DetectionRule.is_enabled == False).count()
    
    return {
        "total": enabled + disabled,
        "by_type": types,
        "enabled": enabled,
        "disabled": disabled
    }
