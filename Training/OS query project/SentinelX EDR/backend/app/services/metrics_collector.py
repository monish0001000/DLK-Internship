"""
SentinelX EDR - Metrics Collector Service
===========================================
Collects and aggregates detection metrics.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.models.metric import DetectionMetric
from app.models.alert import Alert
from app.models.endpoint import Endpoint
from app.models.detection_rule import DetectionRule
from app.schemas.metric import MetricDashboard, MttdResponse

def record_detection_metric(db: Session, rule_id: Optional[str], rule_name: Optional[str], 
                            rule_type: Optional[str], alert_id: Optional[int], endpoint_id: Optional[str], 
                            event_timestamp: Optional[datetime], detection_timestamp: Optional[datetime], 
                            mitre_tactic: Optional[str] = None, mitre_technique: Optional[str] = None, 
                            severity: Optional[str] = None) -> DetectionMetric:
    
    latency = None
    if event_timestamp and detection_timestamp:
        latency = (detection_timestamp - event_timestamp).total_seconds() * 1000.0
        
    metric = DetectionMetric(
        rule_id=rule_id,
        rule_name=rule_name,
        rule_type=rule_type,
        alert_id=alert_id,
        endpoint_id=endpoint_id,
        event_timestamp=event_timestamp,
        detection_timestamp=detection_timestamp,
        detection_latency_ms=latency,
        mitre_tactic=mitre_tactic,
        mitre_technique=mitre_technique,
        severity=severity
    )
    db.add(metric)
    db.commit()
    db.refresh(metric)
    return metric

def get_dashboard_metrics(db: Session) -> MetricDashboard:
    now = datetime.now(timezone.utc)
    week_ago = now - timedelta(days=7)
    
    # Alert stats
    total_alerts = db.query(Alert).count()
    severity_counts = dict(db.query(Alert.severity, func.count(Alert.id)).group_by(Alert.severity).all())
    
    # MTTD (Mean Time To Detect = Avg Latency)
    avg_latency = db.query(func.avg(DetectionMetric.detection_latency_ms)).scalar() or 0.0
    mttd_seconds = avg_latency / 1000.0
    
    # MITRE Coverage
    total_rules = db.query(DetectionRule).count()
    # Simple estimation for now: rules with mitre_ids / total rules * 100
    rules_with_mitre = db.query(DetectionRule).filter(DetectionRule.mitre_ids.isnot(None)).count()
    mitre_coverage_pct = (rules_with_mitre / total_rules * 100) if total_rules > 0 else 0.0
    
    # Trend
    trend_data = get_alerts_trend(db, days=7)
    
    # Top Rules
    top_rules = get_top_performing_rules(db, limit=5)
    
    # Endpoint Coverage
    total_endpoints = db.query(Endpoint).count()
    online_endpoints = db.query(Endpoint).filter(Endpoint.status == "online").count()
    
    return MetricDashboard(
        total_alerts=total_alerts,
        alerts_by_severity=severity_counts,
        mttd_seconds=mttd_seconds,
        detection_latency_avg_ms=avg_latency,
        mitre_coverage_pct=mitre_coverage_pct,
        alerts_trend=trend_data,
        top_rules=top_rules,
        endpoint_coverage={"total": total_endpoints, "online": online_endpoints}
    )

def get_mttd(db: Session, time_range_hours: int = 24) -> MttdResponse:
    since = datetime.now(timezone.utc) - timedelta(hours=time_range_hours)
    metrics = db.query(DetectionMetric.detection_latency_ms).filter(
        DetectionMetric.recorded_at >= since,
        DetectionMetric.detection_latency_ms.isnot(None)
    ).all()
    
    if not metrics:
        return MttdResponse(mttd_seconds=0.0, mttd_formatted="0s", data_points=0)
        
    avg_ms = sum(m[0] for m in metrics) / len(metrics)
    mttd_seconds = avg_ms / 1000.0
    
    return MttdResponse(
        mttd_seconds=mttd_seconds,
        mttd_formatted=f"{mttd_seconds:.2f}s",
        data_points=len(metrics)
    )

def get_detection_latency_distribution(db: Session) -> List[Dict[str, Any]]:
    metrics = db.query(DetectionMetric.detection_latency_ms).filter(
        DetectionMetric.detection_latency_ms.isnot(None)
    ).order_by(desc(DetectionMetric.recorded_at)).limit(100).all()
    
    return [{"index": i, "latency_ms": m[0]} for i, m in enumerate(metrics)]

def get_alerts_trend(db: Session, days: int = 7) -> List[Dict[str, Any]]:
    since = datetime.now(timezone.utc) - timedelta(days=days)
    
    # SQLite friendly date truncation
    results = db.query(
        func.date(Alert.detected_at).label('date'),
        Alert.severity,
        func.count(Alert.id)
    ).filter(Alert.detected_at >= since).group_by(
        func.date(Alert.detected_at),
        Alert.severity
    ).all()
    
    # Format into daily buckets
    days_data = {}
    for i in range(days):
        d = (datetime.now(timezone.utc) - timedelta(days=i)).date().isoformat()
        days_data[d] = {"date": d, "critical": 0, "high": 0, "medium": 0, "low": 0}
        
    for r in results:
        date_str, severity, count = r
        if date_str in days_data:
            days_data[date_str][severity] = count
            
    # Return sorted by date
    return sorted(list(days_data.values()), key=lambda x: x["date"])

def get_top_performing_rules(db: Session, limit: int = 10) -> List[Dict[str, Any]]:
    results = db.query(
        DetectionMetric.rule_name,
        func.count(DetectionMetric.id).label('match_count'),
        func.avg(DetectionMetric.detection_latency_ms).label('avg_latency')
    ).filter(DetectionMetric.rule_name.isnot(None)).group_by(
        DetectionMetric.rule_name
    ).order_by(desc('match_count')).limit(limit).all()
    
    return [
        {"rule_name": r[0], "match_count": r[1], "avg_latency": r[2] or 0.0}
        for r in results
    ]

def get_mitre_coverage(db: Session) -> Dict[str, bool]:
    # Simplified mock for API structure
    covered_techniques = set()
    rules = db.query(DetectionRule.mitre_ids).filter(DetectionRule.mitre_ids.isnot(None)).all()
    for r in rules:
        if r[0]:
            covered_techniques.update([t.strip() for t in r[0].split(',')])
            
    # Mock full matrix structure
    matrix = {}
    for t in ["T1059.001", "T1566.001", "T1204.002", "T1078"]:
        matrix[t] = t in covered_techniques
    return matrix
