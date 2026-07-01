"""
SentinelX EDR - Endpoints API
"""

from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.database import get_db
from app.models.endpoint import Endpoint
from app.schemas.endpoint import EndpointCreate, EndpointUpdate, EndpointResponse, EndpointHeartbeat

router = APIRouter()

@router.post("/", response_model=EndpointResponse)
def register_endpoint(data: EndpointCreate, db: Session = Depends(get_db)) -> Any:
    """Register a new OSQuery endpoint."""
    endpoint = db.query(Endpoint).filter(Endpoint.id == data.id).first()
    if endpoint:
        endpoint.hostname = data.hostname
        endpoint.ip_address = data.ip_address
        endpoint.os_type = data.os_type
        endpoint.os_version = data.os_version
        endpoint.agent_version = data.agent_version
        endpoint.tags = data.tags
        endpoint.status = "online"
        endpoint.last_seen = datetime.now(timezone.utc)
    else:
        endpoint = Endpoint(
            id=data.id,
            hostname=data.hostname,
            ip_address=data.ip_address,
            os_type=data.os_type,
            os_version=data.os_version,
            agent_version=data.agent_version,
            tags=data.tags,
            status="online"
        )
        db.add(endpoint)
    
    db.commit()
    db.refresh(endpoint)
    return endpoint

@router.get("/", response_model=List[EndpointResponse])
def list_endpoints(db: Session = Depends(get_db)) -> Any:
    """Retrieve all registered endpoints."""
    return db.query(Endpoint).all()

@router.get("/{endpoint_id}", response_model=EndpointResponse)
def get_endpoint(endpoint_id: str, db: Session = Depends(get_db)) -> Any:
    """Get a specific endpoint by ID."""
    endpoint = db.query(Endpoint).filter(Endpoint.id == endpoint_id).first()
    if not endpoint:
        raise HTTPException(status_code=404, detail="Endpoint not found")
    return endpoint

@router.post("/heartbeat")
def endpoint_heartbeat(data: EndpointHeartbeat, db: Session = Depends(get_db)) -> Any:
    """Record a heartbeat from an endpoint to keep it 'online'."""
    endpoint = db.query(Endpoint).filter(Endpoint.id == data.endpoint_id).first()
    if not endpoint:
        raise HTTPException(status_code=404, detail="Endpoint not found")
        
    endpoint.last_seen = data.timestamp or datetime.now(timezone.utc)
    endpoint.status = "online"
    db.commit()
    return {"status": "ok"}
