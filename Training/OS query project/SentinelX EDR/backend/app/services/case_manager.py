"""
SentinelX EDR - Case Manager Service
======================================
Handles CRUD operations for Cases, Notes, and Evidence.
"""

from typing import List, Dict, Optional, Any
from datetime import datetime, timezone
import json
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.models.case import Case, CaseNote, CaseEvidence
from app.models.alert import Alert
from app.schemas.case import CaseCreate, CaseUpdate, CaseNoteCreate, CaseEvidenceCreate

def create_case(db: Session, data: CaseCreate) -> Case:
    case = Case(
        title=data.title,
        description=data.description,
        priority=data.priority,
        assignee=data.assignee,
        alert_ids=json.dumps(data.alert_ids) if data.alert_ids else "[]"
    )
    db.add(case)
    db.commit()
    db.refresh(case)
    
    # Update linked alerts
    if data.alert_ids:
        db.query(Alert).filter(Alert.id.in_(data.alert_ids)).update({"status": "investigating"}, synchronize_session=False)
        db.commit()
        
    return case

def update_case(db: Session, case_id: str, data: CaseUpdate) -> Optional[Case]:
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        return None
        
    if data.status:
        case.status = data.status
        if data.status in ["resolved", "closed", "false_positive"] and not case.resolved_at:
            case.resolved_at = datetime.now(timezone.utc)
        if data.status == "closed" and not case.closed_at:
            case.closed_at = datetime.now(timezone.utc)
            
    if data.priority:
        case.priority = data.priority
    if data.assignee is not None:  # Allow unassigning
        case.assignee = data.assignee
    if data.description is not None:
        case.description = data.description
        
    db.commit()
    db.refresh(case)
    return case

def get_case(db: Session, case_id: str) -> Optional[Case]:
    return db.query(Case).filter(Case.id == case_id).first()

def list_cases(db: Session, status: Optional[str] = None, priority: Optional[str] = None, 
               assignee: Optional[str] = None, limit: int = 50, offset: int = 0) -> List[Case]:
    query = db.query(Case)
    if status:
        query = query.filter(Case.status == status)
    if priority:
        query = query.filter(Case.priority == priority)
    if assignee:
        query = query.filter(Case.assignee == assignee)
    return query.order_by(desc(Case.created_at)).offset(offset).limit(limit).all()

def add_note(db: Session, case_id: str, note: CaseNoteCreate) -> CaseNote:
    new_note = CaseNote(
        case_id=case_id,
        content=note.content,
        author=note.author
    )
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    return new_note

def get_notes(db: Session, case_id: str) -> List[CaseNote]:
    return db.query(CaseNote).filter(CaseNote.case_id == case_id).order_by(desc(CaseNote.created_at)).all()

def add_evidence(db: Session, case_id: str, evidence: CaseEvidenceCreate) -> CaseEvidence:
    new_evidence = CaseEvidence(
        case_id=case_id,
        evidence_type=evidence.evidence_type,
        title=evidence.title,
        description=evidence.description,
        content=evidence.content,
        source=evidence.source
    )
    db.add(new_evidence)
    db.commit()
    db.refresh(new_evidence)
    return new_evidence

def get_evidence(db: Session, case_id: str) -> List[CaseEvidence]:
    return db.query(CaseEvidence).filter(CaseEvidence.case_id == case_id).order_by(desc(CaseEvidence.collected_at)).all()

def get_case_metrics(db: Session) -> Dict[str, Any]:
    counts = db.query(Case.status, func.count(Case.id)).group_by(Case.status).all()
    status_counts = {status: count for status, count in counts}
    
    # Calculate avg resolution time
    resolved_cases = db.query(Case).filter(Case.resolved_at.isnot(None)).all()
    avg_resolution_seconds = 0
    if resolved_cases:
        total_seconds = sum((c.resolved_at - c.created_at).total_seconds() for c in resolved_cases)
        avg_resolution_seconds = total_seconds / len(resolved_cases)
        
    return {
        "status_counts": status_counts,
        "total_cases": sum(status_counts.values()),
        "avg_resolution_time_seconds": avg_resolution_seconds
    }
