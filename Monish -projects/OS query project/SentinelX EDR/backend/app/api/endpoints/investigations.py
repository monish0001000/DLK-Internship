"""
SentinelX EDR - Investigations API
"""

from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models.investigation import Investigation
from app.schemas.investigation import InvestigationTrigger, InvestigationResponse
from app.services.ai.agent_pipeline import AgentPipeline

router = APIRouter()

# Instantiate pipeline singleton
pipeline = AgentPipeline()

@router.post("/trigger", response_model=InvestigationResponse)
def trigger_investigation(data: InvestigationTrigger, background_tasks: BackgroundTasks, db: Session = Depends(get_db)) -> Any:
    """
    Triggers the AI multi-agent investigation pipeline for a specific alert.
    Executes synchronously for now, returning the completed investigation.
    """
    try:
        inv = pipeline.run_investigation(db, data.alert_id)
        return inv
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {str(e)}")

@router.get("/", response_model=List[InvestigationResponse])
def get_all_investigations(limit: int = 50, db: Session = Depends(get_db)) -> Any:
    """Get all investigations."""
    return db.query(Investigation).order_by(desc(Investigation.started_at)).limit(limit).all()

@router.get("/{investigation_id}", response_model=InvestigationResponse)
def get_investigation(investigation_id: str, db: Session = Depends(get_db)) -> Any:
    """Get the results of a specific investigation."""
    inv = db.query(Investigation).filter(Investigation.id == investigation_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")
    return inv

@router.get("/alert/{alert_id}", response_model=List[InvestigationResponse])
def get_investigations_for_alert(alert_id: int, db: Session = Depends(get_db)) -> Any:
    """Get all investigations for a specific alert."""
    return db.query(Investigation).filter(Investigation.alert_id == alert_id).order_by(desc(Investigation.started_at)).all()
