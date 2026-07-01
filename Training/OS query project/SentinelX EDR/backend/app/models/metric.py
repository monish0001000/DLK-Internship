"""
SentinelX EDR - Detection Metric Model
========================================
Tracks detection performance metrics for SOC analytics.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from app.database import Base


class DetectionMetric(Base):
    """
    A metric data point recorded when a detection fires.
    Used to compute MTTD, detection latency, rule performance, and MITRE coverage.
    """
    __tablename__ = "detection_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    rule_id = Column(String(100), nullable=True, index=True)
    rule_name = Column(String(500), nullable=True)
    rule_type = Column(String(50), nullable=True)  # sigma, ioc, behavioral, plugin
    alert_id = Column(Integer, ForeignKey("alerts.id"), nullable=True)
    endpoint_id = Column(String(36), ForeignKey("endpoints.id"), nullable=True)

    # Timing metrics
    event_timestamp = Column(DateTime(timezone=True), nullable=True)  # When the event occurred
    detection_timestamp = Column(DateTime(timezone=True), nullable=True)  # When detection fired
    detection_latency_ms = Column(Float, nullable=True)  # Milliseconds from event to detection

    # MITRE mapping
    mitre_tactic = Column(String(100), nullable=True)
    mitre_technique = Column(String(20), nullable=True)

    # Result
    severity = Column(String(20), nullable=True)
    is_true_positive = Column(Integer, nullable=True)  # 1=TP, 0=FP, NULL=unreviewed

    recorded_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<DetectionMetric rule={self.rule_name} latency={self.detection_latency_ms}ms>"
