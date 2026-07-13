"""
SentinelX EDR - Report Model
==============================
Generated investigation/incident reports in Markdown format.

Report Types:
    - incident: Full technical incident report for SOC analysts
    - executive: High-level summary for management
    - hunt: Threat hunting report with methodology and findings
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from app.database import Base


class Report(Base):
    """
    A generated report from an investigation or case.
    Content is stored as Markdown for rendering in the dashboard
    and export to PDF/HTML.
    """
    __tablename__ = "reports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    investigation_id = Column(String(36), ForeignKey("investigations.id"), nullable=True)
    case_id = Column(String(36), ForeignKey("cases.id"), nullable=True)

    title = Column(String(500), nullable=False)
    report_type = Column(String(20), nullable=False)  # incident, executive, hunt
    content_markdown = Column(Text, nullable=False)  # Full report in Markdown

    # Metadata
    generated_by = Column(String(100), nullable=True, default="ai")  # ai, manual
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<Report [{self.report_type}] {self.title[:50]}>"
