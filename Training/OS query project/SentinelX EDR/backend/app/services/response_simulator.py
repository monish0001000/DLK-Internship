"""
SentinelX EDR - Response Simulator Service
===========================================
Simulates incident response actions without affecting real endpoints, logs to DB.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.endpoint import Endpoint
from app.models.response_log import ResponseLog

def simulate_response(db: Session, action_type: str, target: str, endpoint_id: str, user: str = "system", execution_mode: str = "simulation", reason: str = "") -> Dict[str, Any]:
    """
    Simulate an incident response action and log it.
    
    Valid action_types:
    - isolate_endpoint
    - kill_process
    - block_ip
    - disable_user
    - quarantine_file
    """
    
    endpoint = db.query(Endpoint).filter(Endpoint.id == endpoint_id).first()
    
    status = "simulated" if execution_mode == "simulation" else "success"
    outcome = ""
    
    if action_type == "isolate_endpoint":
        if endpoint:
            endpoint.is_isolated = True
            db.commit()
            outcome = f"Endpoint {endpoint.hostname} network connections blocked except to EDR management."
        else:
            status = "failed"
            outcome = "Endpoint not found."
            
    elif action_type == "kill_process":
        outcome = f"Sent SIGKILL to process {target} on {endpoint.hostname if endpoint else endpoint_id}."
        
    elif action_type == "block_ip":
        outcome = f"Added Windows Firewall block rule for IP {target}."
        
    elif action_type == "disable_user":
        outcome = f"Disabled local user account {target}."
        
    elif action_type == "quarantine_file":
        outcome = f"Moved file {target} to quarantine encrypted archive."
        
    else:
        status = "failed"
        outcome = f"Unknown action type: {action_type}"
        
    # Log the action
    log_entry = ResponseLog(
        endpoint_id=endpoint_id,
        user=user,
        action_requested=action_type,
        execution_mode=execution_mode,
        status=status,
        reason=reason or outcome,
        timestamp=datetime.now(timezone.utc)
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
        
    return log_entry

def get_response_log(db: Session, endpoint_id: Optional[str] = None) -> List[ResponseLog]:
    query = db.query(ResponseLog)
    if endpoint_id:
        query = query.filter(ResponseLog.endpoint_id == endpoint_id)
    return query.order_by(desc(ResponseLog.timestamp)).all()
