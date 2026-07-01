"""
SentinelX EDR - Metric Schemas
"""

from pydantic import BaseModel
from typing import Dict, List, Any

class MetricDashboard(BaseModel):
    total_alerts: int
    alerts_by_severity: Dict[str, int]
    mttd_seconds: float
    detection_latency_avg_ms: float
    mitre_coverage_pct: float
    alerts_trend: List[Dict[str, Any]]
    top_rules: List[Dict[str, Any]]
    endpoint_coverage: Dict[str, Any]

class MttdResponse(BaseModel):
    mttd_seconds: float
    mttd_formatted: str
    data_points: int
