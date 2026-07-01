"""
SentinelX EDR - Threat Graph API
"""

from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.graph import ThreatGraph
from app.services.graph_builder import build_alert_graph, build_endpoint_graph

router = APIRouter()

@router.get("/alert/{alert_id}", response_model=ThreatGraph)
def api_build_alert_graph(alert_id: int, db: Session = Depends(get_db)) -> Any:
    graph = build_alert_graph(db, alert_id)
    if not graph:
        raise HTTPException(status_code=404, detail="Graph could not be generated for this alert")
    
    # Enrich with metadata
    graph.metadata = {
        "alert_count": 1,
        "process_count": len([n for n in graph.nodes if n.node_type == "process"]),
        "network_count": len([n for n in graph.nodes if n.node_type == "network"]),
        "endpoint": graph.endpoint_id
    }
    return graph

@router.get("/endpoint/{endpoint_id}", response_model=ThreatGraph)
def api_build_endpoint_graph(endpoint_id: str, hours: int = 1, db: Session = Depends(get_db)) -> Any:
    graph = build_endpoint_graph(db, endpoint_id, hours)
    if not graph:
        raise HTTPException(status_code=404, detail="Graph could not be generated for this endpoint")
        
    # Enrich with metadata
    graph.metadata = {
        "alert_count": 0, # Could query alerts for this endpoint in time window
        "process_count": len([n for n in graph.nodes if n.node_type == "process"]),
        "network_count": len([n for n in graph.nodes if n.node_type == "network"]),
        "endpoint": endpoint_id
    }
    return graph
