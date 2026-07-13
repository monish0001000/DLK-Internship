"""
SentinelX EDR - Telemetry Service
==================================
Handles ingestion and querying of endpoint telemetry.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.endpoint import Endpoint
from app.models.telemetry import Process, NetworkConnection, StartupItem, Service, ScheduledTask, UserSession
from app.schemas.telemetry import TelemetryIngest

def ingest_telemetry(db: Session, data: TelemetryIngest) -> Dict[str, int]:
    """Ingest bulk telemetry data from an endpoint."""
    
    # Ensure endpoint exists, update last_seen
    endpoint = db.query(Endpoint).filter(Endpoint.id == data.endpoint_id).first()
    if not endpoint:
        # Create minimal endpoint if not exists (should have been registered first ideally)
        endpoint = Endpoint(
            id=data.endpoint_id,
            hostname=f"Unknown-{data.endpoint_id[:8]}",
            ip_address="0.0.0.0",
            os_type="unknown",
            status="online",
            last_seen=datetime.now(timezone.utc)
        )
        db.add(endpoint)
    else:
        endpoint.last_seen = datetime.now(timezone.utc)
        endpoint.status = "online"

    collected_time = data.collected_at or datetime.now(timezone.utc)
    
    counts = {
        "processes": 0,
        "network_connections": 0,
        "startup_items": 0,
        "services": 0,
        "scheduled_tasks": 0,
        "user_sessions": 0
    }

    # Ingest Processes
    for p in data.processes:
        db.add(Process(
            endpoint_id=data.endpoint_id,
            pid=p.pid,
            name=p.name,
            path=p.path,
            cmdline=p.cmdline,
            user=p.user,
            parent_pid=p.parent_pid,
            parent_name=p.parent_name,
            hash_sha256=p.hash_sha256,
            hash_md5=p.hash_md5,
            state=p.state,
            collected_at=collected_time
        ))
        counts["processes"] += 1

    # Ingest Network Connections
    for n in data.network_connections:
        db.add(NetworkConnection(
            endpoint_id=data.endpoint_id,
            pid=n.pid,
            process_name=n.process_name,
            local_address=n.local_address,
            local_port=n.local_port,
            remote_address=n.remote_address,
            remote_port=n.remote_port,
            protocol=n.protocol,
            state=n.state,
            collected_at=collected_time
        ))
        counts["network_connections"] += 1

    # Ingest Startup Items
    for s in data.startup_items:
        db.add(StartupItem(
            endpoint_id=data.endpoint_id,
            name=s.name,
            path=s.path,
            args=s.args,
            source=s.source,
            status=s.status,
            username=s.username,
            collected_at=collected_time
        ))
        counts["startup_items"] += 1

    # Ingest Services
    for s in data.services:
        db.add(Service(
            endpoint_id=data.endpoint_id,
            name=s.name,
            display_name=s.display_name,
            status=s.status,
            start_type=s.start_type,
            path=s.path,
            user=s.user,
            description=s.description,
            collected_at=collected_time
        ))
        counts["services"] += 1

    # Ingest Scheduled Tasks
    for t in data.scheduled_tasks:
        db.add(ScheduledTask(
            endpoint_id=data.endpoint_id,
            name=t.name,
            action=t.action,
            path=t.path,
            enabled=t.enabled,
            schedule=t.schedule,
            last_run=t.last_run,
            next_run=t.next_run,
            user=t.user,
            collected_at=collected_time
        ))
        counts["scheduled_tasks"] += 1

    # Ingest User Sessions
    for u in data.user_sessions:
        db.add(UserSession(
            endpoint_id=data.endpoint_id,
            username=u.username,
            type=u.type,
            host=u.host,
            tty=u.tty,
            time=u.time,
            collected_at=collected_time
        ))
        counts["user_sessions"] += 1

    db.commit()
    return counts

def query_processes(db: Session, endpoint_id: Optional[str] = None, 
                    start_time: Optional[datetime] = None, end_time: Optional[datetime] = None, 
                    limit: int = 100) -> List[Process]:
    query = db.query(Process)
    if endpoint_id:
        query = query.filter(Process.endpoint_id == endpoint_id)
    if start_time:
        query = query.filter(Process.collected_at >= start_time)
    if end_time:
        query = query.filter(Process.collected_at <= end_time)
    return query.order_by(desc(Process.collected_at)).limit(limit).all()

def query_network_connections(db: Session, endpoint_id: Optional[str] = None, 
                              start_time: Optional[datetime] = None, end_time: Optional[datetime] = None, 
                              limit: int = 100) -> List[NetworkConnection]:
    query = db.query(NetworkConnection)
    if endpoint_id:
        query = query.filter(NetworkConnection.endpoint_id == endpoint_id)
    if start_time:
        query = query.filter(NetworkConnection.collected_at >= start_time)
    if end_time:
        query = query.filter(NetworkConnection.collected_at <= end_time)
    return query.order_by(desc(NetworkConnection.collected_at)).limit(limit).all()

def query_startup_items(db: Session, endpoint_id: Optional[str] = None, limit: int = 100) -> List[StartupItem]:
    query = db.query(StartupItem)
    if endpoint_id:
        query = query.filter(StartupItem.endpoint_id == endpoint_id)
    return query.order_by(desc(StartupItem.collected_at)).limit(limit).all()

def query_services(db: Session, endpoint_id: Optional[str] = None, limit: int = 100) -> List[Service]:
    query = db.query(Service)
    if endpoint_id:
        query = query.filter(Service.endpoint_id == endpoint_id)
    return query.order_by(desc(Service.collected_at)).limit(limit).all()

def query_scheduled_tasks(db: Session, endpoint_id: Optional[str] = None, limit: int = 100) -> List[ScheduledTask]:
    query = db.query(ScheduledTask)
    if endpoint_id:
        query = query.filter(ScheduledTask.endpoint_id == endpoint_id)
    return query.order_by(desc(ScheduledTask.collected_at)).limit(limit).all()

def query_user_sessions(db: Session, endpoint_id: Optional[str] = None, limit: int = 100) -> List[UserSession]:
    query = db.query(UserSession)
    if endpoint_id:
        query = query.filter(UserSession.endpoint_id == endpoint_id)
    return query.order_by(desc(UserSession.collected_at)).limit(limit).all()

def get_endpoint_telemetry_summary(db: Session, endpoint_id: str) -> Dict[str, int]:
    return {
        "processes": db.query(Process).filter(Process.endpoint_id == endpoint_id).count(),
        "network_connections": db.query(NetworkConnection).filter(NetworkConnection.endpoint_id == endpoint_id).count(),
        "startup_items": db.query(StartupItem).filter(StartupItem.endpoint_id == endpoint_id).count(),
        "services": db.query(Service).filter(Service.endpoint_id == endpoint_id).count(),
        "scheduled_tasks": db.query(ScheduledTask).filter(ScheduledTask.endpoint_id == endpoint_id).count(),
        "user_sessions": db.query(UserSession).filter(UserSession.endpoint_id == endpoint_id).count()
    }
