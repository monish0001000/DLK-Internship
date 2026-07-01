"""
SentinelX EDR - Timeline Builder
==================================
Constructs chronological timelines from alerts and telemetry.
"""

from typing import List, Dict, Any
from datetime import timedelta
import json
from sqlalchemy.orm import Session

from app.models.alert import Alert
from app.models.telemetry import Process, NetworkConnection

def build_alert_timeline(db: Session, alert_id: int) -> List[Dict[str, Any]]:
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        return []
        
    timeline = []
    
    # 1. Add the alert itself
    timeline.append({
        "timestamp": alert.detected_at.isoformat(),
        "event_type": "Alert",
        "title": alert.title,
        "description": f"Rule triggered: {alert.rule_name}",
        "severity": alert.severity,
        "icon": "alert",
        "details": json.loads(alert.evidence) if alert.evidence else {}
    })
    
    # 2. Gather surrounding telemetry (±5 mins)
    time_window = timedelta(minutes=5)
    start_time = alert.detected_at - time_window
    end_time = alert.detected_at + time_window
    
    procs = db.query(Process).filter(
        Process.endpoint_id == alert.endpoint_id,
        Process.collected_at >= start_time,
        Process.collected_at <= end_time
    ).all()
    
    for p in procs:
        timeline.append({
            "timestamp": p.collected_at.isoformat() if p.collected_at else "",
            "event_type": "Process Creation",
            "title": f"Process Started: {p.name}",
            "description": p.cmdline or p.path or "No details",
            "severity": "info",
            "icon": "process",
            "details": {"pid": p.pid, "parent": p.parent_name, "user": p.user}
        })
        
    nets = db.query(NetworkConnection).filter(
        NetworkConnection.endpoint_id == alert.endpoint_id,
        NetworkConnection.collected_at >= start_time,
        NetworkConnection.collected_at <= end_time
    ).all()
    
    for n in nets:
        timeline.append({
            "timestamp": n.collected_at.isoformat() if n.collected_at else "",
            "event_type": "Network Connection",
            "title": f"Connection to {n.remote_address}:{n.remote_port}",
            "description": f"Process {n.process_name or n.pid} over {n.protocol}",
            "severity": "info",
            "icon": "network",
            "details": {"local": f"{n.local_address}:{n.local_port}", "state": n.state}
        })
        
    # Sort chronologically
    timeline.sort(key=lambda x: x["timestamp"])
    return timeline
