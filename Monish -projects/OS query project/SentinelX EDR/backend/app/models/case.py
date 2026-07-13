"""
SentinelX EDR - Case Management Models
========================================
Case management for tracking security incidents through their lifecycle.

Models:
    - Case: The incident case with status, priority, assignee
    - CaseNote: Analyst working notes attached to a case
    - CaseEvidence: Evidence artifacts (logs, screenshots, IOCs) attached to a case

Case Lifecycle:
    open → investigating → contained → resolved → closed
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from app.database import Base


class Case(Base):
    """
    A security incident case that groups related alerts and investigation findings.
    
    Cases enable SOC analysts to:
        - Group related alerts into a single incident
        - Track investigation progress
        - Assign to team members
        - Add notes and evidence
        - Track resolution time (for MTTR metrics)
    """
    __tablename__ = "cases"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)

    # Status: open, investigating, contained, resolved, closed
    status = Column(String(20), nullable=False, default="open", index=True)
    # Priority: critical, high, medium, low
    priority = Column(String(20), nullable=False, default="medium", index=True)

    # Assignment
    assignee = Column(String(255), nullable=True)  # Analyst name/username
    created_by = Column(String(255), nullable=True, default="system")

    # Linked alerts (JSON array of alert IDs)
    alert_ids = Column(Text, nullable=True)  # JSON: [1, 2, 3]

    # Linked investigation
    investigation_id = Column(String(36), ForeignKey("investigations.id"), nullable=True)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    closed_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<Case {self.id[:8]} [{self.status}] {self.title[:50]}>"


class CaseNote(Base):
    """
    An analyst note attached to a case.
    Notes track the investigation thought process and findings.
    """
    __tablename__ = "case_notes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(String(36), ForeignKey("cases.id"), nullable=False, index=True)
    author = Column(String(255), nullable=False, default="analyst")
    content = Column(Text, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<CaseNote case={self.case_id[:8]} by={self.author}>"


class CaseEvidence(Base):
    """
    An evidence artifact attached to a case.
    
    Evidence types:
        - process_log: Process execution details
        - network_capture: Network connection details
        - ioc: Indicators of compromise found
        - screenshot: UI screenshot (base64 or URL)
        - file_sample: File metadata and hashes
        - custom: Free-form evidence
    """
    __tablename__ = "case_evidence"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(String(36), ForeignKey("cases.id"), nullable=False, index=True)
    evidence_type = Column(String(50), nullable=False)  # process_log, network_capture, ioc, etc.
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    content = Column(Text, nullable=True)  # JSON-serialized evidence data
    source = Column(String(255), nullable=True)  # Where this evidence came from
    collected_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<CaseEvidence [{self.evidence_type}] {self.title[:40]}>"
