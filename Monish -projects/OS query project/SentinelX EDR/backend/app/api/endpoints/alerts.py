"""
SentinelX EDR - Alerts API
"""

from typing import List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models.alert import Alert
from app.schemas.alert import AlertResponse, AlertUpdate

router = APIRouter()

@router.get("/", response_model=List[AlertResponse])
def list_alerts(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    endpoint_id: Optional[str] = None,
    limit: int = Query(50, le=1000),
    offset: int = 0,
    db: Session = Depends(get_db)
) -> Any:
    """Retrieve alerts with optional filtering."""
    query = db.query(Alert)
    
    if status:
        query = query.filter(Alert.status == status)
    if severity:
        query = query.filter(Alert.severity == severity)
    if endpoint_id:
        query = query.filter(Alert.endpoint_id == endpoint_id)
        
    return query.order_by(desc(Alert.detected_at)).offset(offset).limit(limit).all()

@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert(alert_id: int, db: Session = Depends(get_db)) -> Any:
    """Get a specific alert."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert

@router.patch("/{alert_id}", response_model=AlertResponse)
def update_alert(alert_id: int, data: AlertUpdate, db: Session = Depends(get_db)) -> Any:
    """Update alert status."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
        
    if data.status:
        alert.status = data.status
        from datetime import datetime, timezone
        if data.status == "acknowledged" and not alert.acknowledged_at:
            alert.acknowledged_at = datetime.now(timezone.utc)
        elif data.status in ["resolved", "false_positive"] and not alert.resolved_at:
            alert.resolved_at = datetime.now(timezone.utc)
            
    db.commit()
    db.refresh(alert)
    return alert
