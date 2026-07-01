"""
SentinelX EDR - Graph Schemas
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class GraphNode(BaseModel):
    id: str
    node_type: str  # process, file, network, user, registry
    label: str
    metadata: Optional[Dict[str, Any]] = None
    severity: Optional[str] = None
    is_suspicious: bool = False

class GraphEdge(BaseModel):
    source: str
    target: str
    relationship: str  # spawned, connected_to, accessed, modified, executed_as
    metadata: Optional[Dict[str, Any]] = None

class ThreatGraph(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    alert_id: Optional[int] = None
    endpoint_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
