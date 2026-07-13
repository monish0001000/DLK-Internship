from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.api import deps
from app.models.audit import AuditLog
from app.schemas.audit import AuditLogResponse
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[AuditLogResponse])
def get_audit_logs(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_role(["Administrator", "SOC Analyst"])),
    user: Optional[str] = None,
    action: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    query = db.query(AuditLog)
    
    if user:
        query = query.filter(AuditLog.user == user)
    if action:
        query = query.filter(AuditLog.action.ilike(f"%{action}%"))
    if status:
        query = query.filter(AuditLog.status == status)
    if start_date:
        query = query.filter(AuditLog.timestamp >= start_date)
    if end_date:
        query = query.filter(AuditLog.timestamp <= end_date)
        
    return query.order_by(AuditLog.timestamp.desc()).offset(offset).limit(limit).all()
