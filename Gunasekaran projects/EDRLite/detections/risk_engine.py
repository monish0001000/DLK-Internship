"""
detections/risk_engine.py
──────────────────────────
Computes a risk score (0–100) for each raw event.

Scoring factors:
  - Base score by event_type
  - Alert severity bonus
  - MITRE technique weight (tactic criticality)
  - IOC match bonus
  - Frequency penalty (repeated events from same host)
"""

import json
import logging
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)

# Base scores per event type
BASE_SCORES = {
    'process': 10,
    'network': 15,
    'usb':     20,
    'startup': 25,
}

# Severity multipliers for alerts linked to this event
SEVERITY_BONUS = {
    'critical': 40,
    'high':     25,
    'medium':   15,
    'low':       8,
    'info':      2,
}

# MITRE tactic risk weights
TACTIC_WEIGHTS = {
    'Execution':            20,
    'Persistence':          25,
    'Privilege Escalation': 30,
    'Defense Evasion':      25,
    'Credential Access':    30,
    'Discovery':            10,
    'Lateral Movement':     30,
    'Collection':           20,
    'Command and Control':  35,
    'Exfiltration':         35,
    'Impact':               40,
}


def calculate_risk(event):
    """
    Calculate and persist a RiskScore for the given RawEvent.
    Called after sigma/ioc/mitre processing (within the same db session).
    """
    from database.db import db
    from database.models import RiskScore, Alert, MitreEvent

    factors = {}
    score   = 0.0

    # 1. Base score
    base = BASE_SCORES.get(event.event_type, 10)
    factors['base'] = base
    score += base

    # 2. Alert severity bonus (sum of all alerts for this event)
    alerts = Alert.query.filter_by(event_id=event.id).all()
    alert_bonus = sum(SEVERITY_BONUS.get(a.severity, 0) for a in alerts)
    factors['alert_bonus'] = alert_bonus
    score += alert_bonus

    # 3. MITRE tactic weight
    mitres = MitreEvent.query.filter_by(event_id=event.id).all()
    tactic_bonus = sum(TACTIC_WEIGHTS.get(m.tactic, 5) for m in mitres)
    factors['tactic_bonus'] = tactic_bonus
    score += tactic_bonus

    # 4. IOC match bonus (alerts from ioc source get extra weight)
    ioc_alerts = [a for a in alerts if a.source == 'ioc']
    ioc_bonus  = len(ioc_alerts) * 20
    factors['ioc_bonus'] = ioc_bonus
    score += ioc_bonus

    # 5. Frequency penalty — if host generated > 50 events in last 5 minutes
    from database.models import RawEvent
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=5)
    recent_count = RawEvent.query.filter(
        RawEvent.hostname  == event.hostname,
        RawEvent.timestamp >= cutoff,
    ).count()
    if recent_count > 50:
        freq_bonus = min(15, (recent_count - 50) // 5)
        factors['frequency_bonus'] = freq_bonus
        score += freq_bonus

    # Clamp to 0–100
    score = min(100.0, max(0.0, score))

    # Determine risk level
    from flask import current_app
    cfg = current_app.config
    if score >= cfg.get('CRITICAL_SCORE', 80):
        risk_level = 'critical'
    elif score >= cfg.get('HIGH_SCORE', 60):
        risk_level = 'high'
    elif score >= cfg.get('MEDIUM_SCORE', 40):
        risk_level = 'medium'
    elif score >= cfg.get('LOW_SCORE', 20):
        risk_level = 'low'
    else:
        risk_level = 'info'

    rs = RiskScore(
        event_id=event.id,
        score=round(score, 2),
        risk_level=risk_level,
        factors=json.dumps(factors),
        calculated_at=datetime.now(timezone.utc),
    )
    db.session.add(rs)
    logger.debug(f"RiskScore for event #{event.id}: {score:.1f} ({risk_level})")
