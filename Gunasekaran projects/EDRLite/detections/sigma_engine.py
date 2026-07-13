"""
detections/sigma_engine.py
───────────────────────────
Lightweight Sigma-style rule engine.
Rules are YAML files in the rules/ directory.
Each rule specifies field conditions and maps to a MITRE technique.
"""

import os
import yaml
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

_rules_cache: list[dict] = []
_rules_loaded = False


def _load_rules(rules_dir: str) -> list[dict]:
    global _rules_cache, _rules_loaded
    if _rules_loaded:
        return _rules_cache

    rules = []
    if not os.path.isdir(rules_dir):
        logger.warning(f"Rules directory not found: {rules_dir}")
        _rules_loaded = True
        return rules

    for fname in os.listdir(rules_dir):
        if fname.endswith('.yml') or fname.endswith('.yaml'):
            fpath = os.path.join(rules_dir, fname)
            try:
                with open(fpath, 'r') as f:
                    rule = yaml.safe_load(f)
                    if rule and isinstance(rule, dict):
                        rules.append(rule)
                        logger.info(f"Loaded Sigma rule: {rule.get('title', fname)}")
            except Exception as e:
                logger.error(f"Failed to load rule {fname}: {e}")

    _rules_cache = rules
    _rules_loaded = True
    logger.info(f"Total Sigma rules loaded: {len(rules)}")
    return rules


def _match_condition(condition: dict, data: dict) -> bool:
    """
    Evaluate a condition block against event data.
    Condition fields support: equals, contains, startswith, endswith, regex
    Multiple fields are AND-combined; list values are OR-combined.
    """
    import re
    for field, pattern in condition.items():
        value = str(data.get(field, '')).lower()

        if isinstance(pattern, list):
            # OR-match: any pattern in list must match
            matched = False
            for p in pattern:
                p_str = str(p).lower()
                if p_str in value:
                    matched = True
                    break
            if not matched:
                return False

        elif isinstance(pattern, dict):
            op  = list(pattern.keys())[0]
            val = str(list(pattern.values())[0]).lower()
            if op == 'contains'    and val not in value:
                return False
            elif op == 'startswith' and not value.startswith(val):
                return False
            elif op == 'endswith'   and not value.endswith(val):
                return False
            elif op == 'equals'     and value != val:
                return False
            elif op == 'regex':
                if not re.search(val, value, re.IGNORECASE):
                    return False

        else:
            if str(pattern).lower() not in value:
                return False

    return True


def run_sigma_detection(event, data: dict):
    """
    Run all loaded Sigma rules against an event.
    Creates Alert and MitreEvent records for matches.
    """
    from flask import current_app
    from database.db import db
    from database.models import Alert, MitreEvent

    rules_dir = current_app.config.get('RULES_DIR', 'rules')
    rules = _load_rules(rules_dir)

    for rule in rules:
        # Check event_type filter
        rule_types = rule.get('event_types', [])
        if rule_types and event.event_type not in rule_types:
            continue

        condition = rule.get('detection', {}).get('condition', {})
        if not condition:
            continue

        if _match_condition(condition, data):
            # Create alert
            alert = Alert(
                timestamp=datetime.now(timezone.utc),
                alert_name=rule.get('title', 'Sigma Alert'),
                severity=rule.get('level', 'medium'),
                status='open',
                description=rule.get('description', ''),
                hostname=event.hostname,
                event_id=event.id,
                source='sigma',
            )
            db.session.add(alert)

            # Create MITRE mapping
            mitre = rule.get('mitre', {})
            if mitre:
                m = MitreEvent(
                    event_id=event.id,
                    technique_id=mitre.get('technique_id', ''),
                    technique_name=mitre.get('technique_name', ''),
                    tactic=mitre.get('tactic', ''),
                    timestamp=datetime.now(timezone.utc),
                )
                db.session.add(m)

            logger.info(f"Sigma alert: [{rule.get('level','?').upper()}] "
                        f"{rule.get('title')} on {event.hostname}")
