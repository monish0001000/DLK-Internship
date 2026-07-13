"""
SentinelX EDR - Endpoint Model
===============================
Represents a registered endpoint (workstation, server, laptop) in the fleet.
Each endpoint runs the SentinelX agent which reports telemetry to the backend.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Boolean, Text
from app.database import Base


class Endpoint(Base):
    """
    An endpoint is a machine running the SentinelX agent.
    
    Lifecycle:
        1. Agent starts → POST /api/endpoints (register)
        2. Agent sends heartbeat → PATCH /api/endpoints/heartbeat
        3. If no heartbeat for AGENT_HEARTBEAT_TIMEOUT_SECONDS → status = "offline"
        4. If isolated via response simulation → is_isolated = True
    """
    __tablename__ = "endpoints"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    hostname = Column(String(255), nullable=False, index=True)
    ip_address = Column(String(45), nullable=False)  # IPv4 or IPv6
    os_type = Column(String(50), nullable=False)  # windows, linux, darwin
    os_version = Column(String(100), nullable=True)
    agent_version = Column(String(20), nullable=True, default="1.0.0")
    status = Column(String(20), nullable=False, default="online")  # online, offline, error
    is_isolated = Column(Boolean, default=False)  # Response simulation: network isolation
    last_seen = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    registered_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    tags = Column(Text, nullable=True)  # Comma-separated tags (e.g., "server,production,dmz")

    def __repr__(self) -> str:
        return f"<Endpoint {self.hostname} ({self.ip_address}) [{self.status}]>"
