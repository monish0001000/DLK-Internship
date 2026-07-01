"""
SentinelX EDR - Simulation Run Model
======================================
Tracks attack simulation runs and their results.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Text
from app.database import Base


class SimulationRun(Base):
    """
    A record of an attack simulation execution.
    
    Simulations generate realistic telemetry that flows through
    the detection pipeline, measuring detection coverage.
    
    Scenarios include:
        - phishing_macro: Word macro → cmd → PowerShell → C2
        - credential_theft: mimikatz, lsass access
        - ransomware: Mass file encryption, shadow deletion
        - lateral_movement: PsExec, WMI, RDP brute force
        - persistence: Registry, scheduled tasks, services
    """
    __tablename__ = "simulation_runs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    scenario_name = Column(String(255), nullable=False)
    scenario_description = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default="pending")  # pending, running, completed, failed
    endpoint_id = Column(String(36), nullable=True)  # Target endpoint for simulation

    # Results
    events_generated = Column(Integer, default=0)
    alerts_triggered = Column(Integer, default=0)
    rules_matched = Column(Text, nullable=True)  # JSON: [rule_name, ...]
    detection_coverage_pct = Column(Integer, nullable=True)  # 0-100%
    results_summary = Column(Text, nullable=True)  # JSON: detailed results

    # Timestamps
    started_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    completed_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<SimulationRun [{self.scenario_name}] {self.status} coverage={self.detection_coverage_pct}%>"
