"""
SentinelX EDR - Telemetry Schemas
"""

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime

class ProcessData(BaseModel):
    pid: int
    name: str
    path: Optional[str] = None
    cmdline: Optional[str] = None
    user: Optional[str] = None
    parent_pid: Optional[int] = None
    parent_name: Optional[str] = None
    hash_sha256: Optional[str] = None
    hash_md5: Optional[str] = None
    state: Optional[str] = None

class NetworkData(BaseModel):
    pid: Optional[int] = None
    process_name: Optional[str] = None
    local_address: Optional[str] = None
    local_port: Optional[int] = None
    remote_address: Optional[str] = None
    remote_port: Optional[int] = None
    protocol: Optional[str] = None
    state: Optional[str] = None

class StartupData(BaseModel):
    name: str
    path: Optional[str] = None
    args: Optional[str] = None
    source: Optional[str] = None
    status: Optional[str] = None
    username: Optional[str] = None

class ServiceData(BaseModel):
    name: str
    display_name: Optional[str] = None
    status: Optional[str] = None
    start_type: Optional[str] = None
    path: Optional[str] = None
    user: Optional[str] = None
    description: Optional[str] = None

class TaskData(BaseModel):
    name: str
    action: Optional[str] = None
    path: Optional[str] = None
    enabled: Optional[bool] = None
    schedule: Optional[str] = None
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    user: Optional[str] = None

class SessionData(BaseModel):
    username: str
    type: Optional[str] = None
    host: Optional[str] = None
    tty: Optional[str] = None
    time: Optional[datetime] = None

class TelemetryIngest(BaseModel):
    endpoint_id: str
    processes: List[ProcessData] = Field(default_factory=list)
    network_connections: List[NetworkData] = Field(default_factory=list)
    startup_items: List[StartupData] = Field(default_factory=list)
    services: List[ServiceData] = Field(default_factory=list)
    scheduled_tasks: List[TaskData] = Field(default_factory=list)
    user_sessions: List[SessionData] = Field(default_factory=list)
    collected_at: Optional[datetime] = None

class TelemetryQuery(BaseModel):
    endpoint_id: Optional[str] = None
    telemetry_type: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    limit: int = 100
