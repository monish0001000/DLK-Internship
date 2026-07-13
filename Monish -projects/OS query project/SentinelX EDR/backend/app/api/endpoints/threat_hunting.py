"""
SentinelX EDR - Threat Hunting API
"""

from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta

from app.database import get_db
from app.schemas.threat_hunting import ThreatHuntQuery, ThreatHuntSaveRequest, SavedHuntResponse, ThreatHuntHistory
from app.models.threat_hunting import SavedHunt, HuntHistory
from app.services.telemetry_service import (
    query_processes, 
    query_network_connections,
    query_startup_items,
    query_services,
    query_scheduled_tasks,
    query_user_sessions
)

router = APIRouter()

def parse_time_range(time_range: str) -> datetime:
    now = datetime.now(timezone.utc)
    if time_range == "1h":
        return now - timedelta(hours=1)
    elif time_range == "24h":
        return now - timedelta(hours=24)
    elif time_range == "7d":
        return now - timedelta(days=7)
    return now - timedelta(hours=24) # default

@router.post("/query")
def execute_hunt_query(query: ThreatHuntQuery, db: Session = Depends(get_db)) -> Any:
    # Calculate start time
    start_time = parse_time_range(query.time_range)
    
    # Execute query based on table
    results = []
    if query.table == "processes":
        # Apply rudimentary filtering - in a real app we'd build a dynamic SQLAlchemy query
        all_results = query_processes(db, start_time=start_time, limit=query.limit)
        results = all_results
    elif query.table == "network_connections":
        results = query_network_connections(db, start_time=start_time, limit=query.limit)
    elif query.table == "startup_items":
        results = query_startup_items(db, limit=query.limit)
    elif query.table == "services":
        results = query_services(db, limit=query.limit)
    elif query.table == "scheduled_tasks":
        results = query_scheduled_tasks(db, limit=query.limit)
    elif query.table == "user_sessions":
        results = query_user_sessions(db, limit=query.limit)
    else:
        raise HTTPException(status_code=400, detail=f"Unknown table: {query.table}")
        
    # Apply filters in Python memory (simplification for Phase 12.5)
    if query.filters:
        filtered_results = []
        for r in results:
            match = True
            for k, v in query.filters.items():
                if hasattr(r, k):
                    val = getattr(r, k)
                    if val and v.lower() not in str(val).lower():
                        match = False
                        break
            if match:
                filtered_results.append(r)
        results = filtered_results

    # Generate readable query text for history
    filter_text = " AND ".join([f"{k} LIKE '%{v}%'" for k,v in (query.filters or {}).items()])
    query_text = f"SELECT * FROM {query.table} WHERE time >= '{query.time_range}'"
    if filter_text:
        query_text += f" AND {filter_text}"
        
    # Log to history
    history = HuntHistory(
        query_text=query_text,
        query_payload=query.model_dump(),
        user="admin_user",
        timestamp=datetime.now(timezone.utc)
    )
    db.add(history)
    db.commit()

    return {"results": [r.__dict__ for r in results if not str(r.__dict__.keys()).startswith("_")], "query_text": query_text}

@router.get("/history", response_model=List[ThreatHuntHistory])
def get_hunt_history(limit: int = 20, db: Session = Depends(get_db)) -> Any:
    history = db.query(HuntHistory).order_by(HuntHistory.timestamp.desc()).limit(limit).all()
    # Format timestamp to string to match schema
    return [{"id": h.id, "query_text": h.query_text, "timestamp": h.timestamp.isoformat(), "user": h.user} for h in history]

@router.post("/saved", response_model=SavedHuntResponse)
def save_hunt(hunt: ThreatHuntSaveRequest, db: Session = Depends(get_db)) -> Any:
    saved = SavedHunt(
        name=hunt.name,
        description=hunt.description,
        query_payload=hunt.query.model_dump(),
        created_at=datetime.now(timezone.utc)
    )
    db.add(saved)
    db.commit()
    db.refresh(saved)
    return saved

@router.get("/saved", response_model=List[SavedHuntResponse])
def get_saved_hunts(db: Session = Depends(get_db)) -> Any:
    hunts = db.query(SavedHunt).order_by(SavedHunt.created_at.desc()).all()
    # Need to map query_payload back to query structure
    return [{"id": h.id, "name": h.name, "description": h.description, "query": h.query_payload} for h in hunts]
