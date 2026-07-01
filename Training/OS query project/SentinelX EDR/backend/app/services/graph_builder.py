"""
SentinelX EDR - Threat Graph Builder
======================================
Constructs relationship graphs from telemetry data.
"""

import json
from typing import List, Dict, Any, Optional
from datetime import timedelta, datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.alert import Alert
from app.models.telemetry import Process, NetworkConnection
from app.schemas.graph import ThreatGraph, GraphNode, GraphEdge

def build_alert_graph(db: Session, alert_id: int) -> Optional[ThreatGraph]:
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        return None
        
    nodes = {}
    edges = []
    
    # Add Alert Node
    alert_node_id = f"alert-{alert.id}"
    nodes[alert_node_id] = GraphNode(
        id=alert_node_id,
        node_type="alert",
        label=alert.title[:30],
        severity=alert.severity,
        is_suspicious=True
    )
    
    # Try to extract process PID from evidence
    target_pid = None
    if alert.evidence:
        try:
            ev = json.loads(alert.evidence)
            target_pid = ev.get("pid")
        except:
            pass
            
    # Gather related processes around the alert time
    time_window = timedelta(minutes=5)
    start_time = alert.detected_at - time_window
    end_time = alert.detected_at + time_window
    
    procs = db.query(Process).filter(
        Process.endpoint_id == alert.endpoint_id,
        Process.collected_at >= start_time,
        Process.collected_at <= end_time
    ).all()
    
    # Map processes
    for p in procs:
        p_id = f"proc-{p.pid}"
        is_target = target_pid == p.pid
        
        if p_id not in nodes:
            nodes[p_id] = GraphNode(
                id=p_id,
                node_type="process",
                label=f"{p.name} ({p.pid})",
                is_suspicious=is_target,
                metadata={"cmdline": p.cmdline, "path": p.path}
            )
            
        if is_target:
            edges.append(GraphEdge(source=alert_node_id, target=p_id, relationship="triggered_by"))
            
        # Parent relationship
        if p.parent_pid:
            parent_id = f"proc-{p.parent_pid}"
            if parent_id not in nodes:
                nodes[parent_id] = GraphNode(
                    id=parent_id,
                    node_type="process",
                    label=f"{p.parent_name or 'Unknown'} ({p.parent_pid})",
                    is_suspicious=False
                )
            edges.append(GraphEdge(source=parent_id, target=p_id, relationship="spawned"))
            
    # Gather network connections
    nets = db.query(NetworkConnection).filter(
        NetworkConnection.endpoint_id == alert.endpoint_id,
        NetworkConnection.collected_at >= start_time,
        NetworkConnection.collected_at <= end_time
    ).all()
    
    for n in nets:
        p_id = f"proc-{n.pid}" if n.pid else "proc-unknown"
        net_id = f"net-{n.remote_address}:{n.remote_port}"
        
        if net_id not in nodes:
            nodes[net_id] = GraphNode(
                id=net_id,
                node_type="network",
                label=f"{n.remote_address}:{n.remote_port}",
                metadata={"protocol": n.protocol, "state": n.state}
            )
            
        if p_id in nodes:
            edges.append(GraphEdge(source=p_id, target=net_id, relationship="connected_to"))
            
    return ThreatGraph(
        nodes=list(nodes.values()),
        edges=edges,
        alert_id=alert.id,
        endpoint_id=alert.endpoint_id
    )

def build_endpoint_graph(db: Session, endpoint_id: str, time_range_hours: int = 1) -> ThreatGraph:
    # Build graph of recent activity for an endpoint
    time_window = timedelta(hours=time_range_hours)
    start_time = datetime.now(timezone.utc) - time_window
    
    nodes = {}
    edges = []
    
    # Gather processes
    procs = db.query(Process).filter(
        Process.endpoint_id == endpoint_id,
        Process.collected_at >= start_time
    ).order_by(desc(Process.collected_at)).limit(200).all()
    
    for p in procs:
        p_id = f"proc-{p.pid}"
        if p_id not in nodes:
            nodes[p_id] = GraphNode(
                id=p_id,
                node_type="process",
                label=f"{p.name} ({p.pid})",
                is_suspicious=False,
                metadata={"cmdline": p.cmdline, "path": p.path}
            )
            
        # Parent relationship
        if p.parent_pid:
            parent_id = f"proc-{p.parent_pid}"
            if parent_id not in nodes:
                nodes[parent_id] = GraphNode(
                    id=parent_id,
                    node_type="process",
                    label=f"{p.parent_name or 'Unknown'} ({p.parent_pid})",
                    is_suspicious=False
                )
            edges.append(GraphEdge(source=parent_id, target=p_id, relationship="spawned"))
            
    # Gather network connections
    nets = db.query(NetworkConnection).filter(
        NetworkConnection.endpoint_id == endpoint_id,
        NetworkConnection.collected_at >= start_time
    ).order_by(desc(NetworkConnection.collected_at)).limit(100).all()
    
    for n in nets:
        p_id = f"proc-{n.pid}" if n.pid else "proc-unknown"
        net_id = f"net-{n.remote_address}:{n.remote_port}"
        
        if net_id not in nodes:
            nodes[net_id] = GraphNode(
                id=net_id,
                node_type="network",
                label=f"{n.remote_address}:{n.remote_port}",
                metadata={"protocol": n.protocol, "state": n.state}
            )
            
        if p_id in nodes:
            edges.append(GraphEdge(source=p_id, target=net_id, relationship="connected_to"))
            
    return ThreatGraph(
        nodes=list(nodes.values()),
        edges=edges,
        endpoint_id=endpoint_id
    )
