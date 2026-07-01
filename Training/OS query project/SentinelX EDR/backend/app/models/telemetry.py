"""
SentinelX EDR - Telemetry Models
=================================
ORM models for all endpoint telemetry types collected via OSQuery.

Telemetry Types:
    - Process: Running processes with command lines, hashes, parent info
    - NetworkConnection: Active network connections (TCP/UDP)
    - StartupItem: Persistence via startup/Run keys
    - Service: Windows services / systemd units
    - ScheduledTask: Scheduled tasks / cron jobs
    - UserSession: Logged-in users and sessions
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from app.database import Base


class Process(Base):
    """
    A process captured from an endpoint via OSQuery's `processes` table.
    
    Key detection fields:
        - cmdline: Checked for encoded PowerShell, download cradles, LOLBins
        - parent_name: Checked for suspicious parent-child relationships
        - hash_sha256: Matched against IOC database
    """
    __tablename__ = "processes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    endpoint_id = Column(String(36), ForeignKey("endpoints.id"), nullable=False, index=True)
    pid = Column(Integer, nullable=False)
    name = Column(String(255), nullable=False, index=True)
    path = Column(Text, nullable=True)
    cmdline = Column(Text, nullable=True)
    user = Column(String(255), nullable=True)
    parent_pid = Column(Integer, nullable=True)
    parent_name = Column(String(255), nullable=True)
    hash_sha256 = Column(String(64), nullable=True, index=True)
    hash_md5 = Column(String(32), nullable=True)
    state = Column(String(20), nullable=True)  # running, sleeping, stopped
    start_time = Column(DateTime(timezone=True), nullable=True)
    collected_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    def __repr__(self) -> str:
        return f"<Process {self.name} (PID={self.pid}) on {self.endpoint_id}>"


class NetworkConnection(Base):
    """
    An active network connection captured from an endpoint.
    
    Key detection fields:
        - remote_address: Matched against IOC database (malicious IPs)
        - remote_port: Common C2 ports (4444, 8080, etc.)
        - process_name: Process making the connection
    """
    __tablename__ = "network_connections"

    id = Column(Integer, primary_key=True, autoincrement=True)
    endpoint_id = Column(String(36), ForeignKey("endpoints.id"), nullable=False, index=True)
    pid = Column(Integer, nullable=True)
    process_name = Column(String(255), nullable=True)
    local_address = Column(String(45), nullable=True)
    local_port = Column(Integer, nullable=True)
    remote_address = Column(String(45), nullable=True, index=True)
    remote_port = Column(Integer, nullable=True)
    protocol = Column(String(10), nullable=True)  # tcp, udp, tcp6, udp6
    state = Column(String(20), nullable=True)  # ESTABLISHED, LISTEN, TIME_WAIT, etc.
    collected_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    def __repr__(self) -> str:
        return f"<NetworkConnection {self.process_name} → {self.remote_address}:{self.remote_port}>"


class StartupItem(Base):
    """
    A startup/persistence entry from the endpoint.
    Sources include: Registry Run keys, Startup folder, Login items.
    
    Key detection fields:
        - path: Executable path checked for suspicious locations
        - source: Registry key or startup mechanism
    """
    __tablename__ = "startup_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    endpoint_id = Column(String(36), ForeignKey("endpoints.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    path = Column(Text, nullable=True)
    args = Column(Text, nullable=True)
    source = Column(String(255), nullable=True)  # Registry key, startup folder path
    status = Column(String(20), nullable=True, default="enabled")  # enabled, disabled
    username = Column(String(255), nullable=True)
    collected_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<StartupItem {self.name} [{self.source}]>"


class Service(Base):
    """
    A system service (Windows service or systemd unit) from the endpoint.
    
    Key detection fields:
        - path: Service binary path checked for suspicious locations
        - start_type: New auto-start services are suspicious
        - user: Services running as SYSTEM with unusual paths
    """
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, autoincrement=True)
    endpoint_id = Column(String(36), ForeignKey("endpoints.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    display_name = Column(String(500), nullable=True)
    status = Column(String(20), nullable=True)  # running, stopped, start_pending
    start_type = Column(String(20), nullable=True)  # auto, manual, disabled, boot
    path = Column(Text, nullable=True)
    user = Column(String(255), nullable=True)  # LocalSystem, NetworkService, custom
    description = Column(Text, nullable=True)
    collected_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<Service {self.name} [{self.status}]>"


class ScheduledTask(Base):
    """
    A scheduled task (Windows Task Scheduler or cron) from the endpoint.
    
    Key detection fields:
        - action: Command being executed
        - name: New tasks with suspicious names
    """
    __tablename__ = "scheduled_tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    endpoint_id = Column(String(36), ForeignKey("endpoints.id"), nullable=False, index=True)
    name = Column(String(500), nullable=False)
    action = Column(Text, nullable=True)
    path = Column(Text, nullable=True)
    enabled = Column(Boolean, default=True)
    schedule = Column(String(255), nullable=True)  # Trigger description
    last_run = Column(DateTime(timezone=True), nullable=True)
    next_run = Column(DateTime(timezone=True), nullable=True)
    user = Column(String(255), nullable=True)
    collected_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<ScheduledTask {self.name} [{'enabled' if self.enabled else 'disabled'}]>"


class UserSession(Base):
    """
    An active user session (logged-in user) on the endpoint.
    
    Key detection fields:
        - type: RDP sessions from unexpected sources
        - host: Remote login source addresses
    """
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    endpoint_id = Column(String(36), ForeignKey("endpoints.id"), nullable=False, index=True)
    username = Column(String(255), nullable=False, index=True)
    type = Column(String(50), nullable=True)  # console, rdp, ssh, local
    host = Column(String(255), nullable=True)  # Source IP for remote sessions
    tty = Column(String(50), nullable=True)
    time = Column(DateTime(timezone=True), nullable=True)
    collected_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<UserSession {self.username} [{self.type}]>"
