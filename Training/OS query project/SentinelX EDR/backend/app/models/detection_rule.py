"""
SentinelX EDR - Detection Rule Model
======================================
Stores detection rules from the rule marketplace.
Supports Sigma, YARA, and custom IOC list imports.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from app.database import Base


class DetectionRule(Base):
    """
    A detection rule that can be imported, enabled/disabled, and managed.
    
    Rule Types:
        - sigma: Sigma YAML detection rules
        - yara: YARA rules for file/memory scanning
        - ioc_list: IOC lists (CSV/JSON) for matching
        - custom: Custom Python plugin detectors
    
    Sources:
        - bundled: Ships with the platform
        - imported: Manually imported by analyst
        - ai_suggested: Suggested by the AI Rule Suggestion Agent
        - community: From shared rule repositories
    """
    __tablename__ = "detection_rules"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(500), nullable=False, index=True)
    description = Column(Text, nullable=True)
    rule_type = Column(String(20), nullable=False, index=True)  # sigma, yara, ioc_list, custom
    content = Column(Text, nullable=False)  # The actual rule content (YAML, YARA, JSON, etc.)
    severity = Column(String(20), nullable=False, default="medium")  # critical, high, medium, low
    is_enabled = Column(Boolean, default=True, nullable=False)
    source = Column(String(50), nullable=False, default="bundled")  # bundled, imported, ai_suggested
    author = Column(String(255), nullable=True)

    # MITRE ATT&CK tags (comma-separated technique IDs)
    mitre_ids = Column(Text, nullable=True)  # e.g., "T1059.001,T1547.001"

    # Metrics
    total_matches = Column(Integer, default=0)
    false_positive_count = Column(Integer, default=0)
    last_matched_at = Column(DateTime(timezone=True), nullable=True)

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

    def __repr__(self) -> str:
        return f"<DetectionRule [{self.rule_type}] {self.name[:50]} ({'enabled' if self.is_enabled else 'disabled'})>"
