"""
SentinelX EDR - Investigation Model
====================================
Stores results from the multi-agent AI investigation pipeline.

Pipeline stages stored in pipeline_results:
    1. Detection Agent: Alert analysis, enrichment, verdict
    2. Threat Hunter Agent: Event correlation, attack chain
    3. Incident Analyst Agent: Root cause, impact, risk score
    4. Report Writer Agent: Professional report content
    5. Response Planner Agent: Containment playbook
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey
from app.database import Base


class Investigation(Base):
    """
    An AI-powered investigation triggered from an alert.
    
    Each investigation runs through the 5-agent pipeline and stores
    the complete results including risk score, MITRE mapping,
    timeline reconstruction, and suggested detection rules.
    """
    __tablename__ = "investigations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    alert_id = Column(Integer, ForeignKey("alerts.id"), nullable=False, index=True)

    # Pipeline results (JSON-serialized output from each AI agent)
    pipeline_results = Column(Text, nullable=True)  # JSON: {agent_name: agent_output}

    # Consolidated findings
    summary = Column(Text, nullable=True)  # Executive summary of the investigation
    root_cause = Column(Text, nullable=True)  # Root cause analysis
    risk_score = Column(Float, nullable=True)  # 0-100 risk score
    risk_level = Column(String(20), nullable=True)  # critical, high, medium, low

    # MITRE ATT&CK mapping (JSON array of mapped techniques)
    mitre_mapping = Column(Text, nullable=True)  # JSON: [{technique_id, name, tactic}]

    # Timeline reconstruction (JSON array of chronological events)
    timeline = Column(Text, nullable=True)  # JSON: [{timestamp, event_type, description}]

    # Recommendations from the Incident Analyst
    recommendations = Column(Text, nullable=True)

    # Response plan from the Response Planner Agent
    response_plan = Column(Text, nullable=True)  # JSON: {actions: [], priority, rationale}

    # AI-suggested detection rules (JSON array of Sigma YAML strings)
    suggested_rules = Column(Text, nullable=True)  # JSON: [{rule_yaml, description}]

    # Metadata
    ai_model = Column(String(100), nullable=True)  # Model used (e.g., "gemini-2.0-flash")
    status = Column(String(20), default="pending")  # pending, running, completed, failed
    error_message = Column(Text, nullable=True)

    # Timestamps
    started_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    completed_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<Investigation {self.id[:8]} alert={self.alert_id} risk={self.risk_score}>"
