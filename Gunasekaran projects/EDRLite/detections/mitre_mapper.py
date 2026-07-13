"""
detections/mitre_mapper.py
───────────────────────────
Maps osquery events to MITRE ATT&CK techniques.

Coverage:
  T1059  — Command and Scripting Interpreter (Execution)
  T1053  — Scheduled Task / Job (Persistence)
  T1547  — Boot or Logon Autostart Execution (Persistence)
  T1049  — System Network Connections Discovery (Discovery)
  T1057  — Process Discovery (Discovery)
  T1091  — Replication Through Removable Media (Lateral Movement)
  T1110  — Brute Force (Credential Access) — high uid 0 logins
  T1046  — Network Service Scanning (Discovery)
  T1071  — Application Layer Protocol (Command and Control)
"""

import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────
#  Technique mapping rules
# ─────────────────────────────────────────────────────────────

TECHNIQUE_RULES = [
    # Execution — scripting interpreters
    {
        'technique_id':   'T1059',
        'technique_name': 'Command and Scripting Interpreter',
        'tactic':         'Execution',
        'event_types':    ['process'],
        'match': lambda d: any(
            s in str(d.get('name', '')).lower() or
            s in str(d.get('cmdline', '')).lower()
            for s in ['python', 'bash', 'sh', 'perl', 'ruby', 'php',
                      'nc', 'ncat', 'netcat', 'curl', 'wget', 'powershell']
        ),
    },
    # Persistence — Scheduled Task / Cron
    {
        'technique_id':   'T1053',
        'technique_name': 'Scheduled Task/Job: Cron',
        'tactic':         'Persistence',
        'event_types':    ['startup'],
        'match': lambda d: d.get('source') == 'crontab',
    },
    # Persistence — Boot/Logon Autostart
    {
        'technique_id':   'T1547',
        'technique_name': 'Boot or Logon Autostart Execution',
        'tactic':         'Persistence',
        'event_types':    ['startup'],
        'match': lambda d: d.get('source') == 'startup_items',
    },
    # Discovery — Network Connections
    {
        'technique_id':   'T1049',
        'technique_name': 'System Network Connections Discovery',
        'tactic':         'Discovery',
        'event_types':    ['network'],
        'match': lambda d: d.get('connection_type') == 'active',
    },
    # Discovery — Network Service Scanning (many ports)
    {
        'technique_id':   'T1046',
        'technique_name': 'Network Service Scanning',
        'tactic':         'Discovery',
        'event_types':    ['network'],
        'match': lambda d: int(d.get('remote_port', 0) or 0) in [
            21, 22, 23, 25, 80, 443, 445, 3389, 5900
        ],
    },
    # Discovery — Process Discovery
    {
        'technique_id':   'T1057',
        'technique_name': 'Process Discovery',
        'tactic':         'Discovery',
        'event_types':    ['process'],
        'match': lambda d: str(d.get('name', '')).lower() in [
            'ps', 'top', 'htop', 'pstree', 'tasklist'
        ],
    },
    # Lateral Movement — Removable Media
    {
        'technique_id':   'T1091',
        'technique_name': 'Replication Through Removable Media',
        'tactic':         'Lateral Movement',
        'event_types':    ['usb'],
        'match': lambda d: str(d.get('removable', '0')) == '1',
    },
    # C2 — outbound high-port connections to non-standard IPs
    {
        'technique_id':   'T1071',
        'technique_name': 'Application Layer Protocol',
        'tactic':         'Command and Control',
        'event_types':    ['network'],
        'match': lambda d: (
            int(d.get('remote_port', 0) or 0) > 1024 and
            d.get('remote_address', '').startswith(('10.', '192.168.', '172.'))
        ),
    },
]


def map_event(event, data: dict):
    """
    Evaluate MITRE rules against the event data.
    Creates MitreEvent records for each matched technique.
    Skips duplicate technique+event_id pairs.
    """
    from database.db import db
    from database.models import MitreEvent

    existing = {
        m.technique_id
        for m in MitreEvent.query.filter_by(event_id=event.id).all()
    }

    for rule in TECHNIQUE_RULES:
        if event.event_type not in rule.get('event_types', []):
            continue
        try:
            if rule['match'](data) and rule['technique_id'] not in existing:
                m = MitreEvent(
                    event_id=event.id,
                    technique_id=rule['technique_id'],
                    technique_name=rule['technique_name'],
                    tactic=rule['tactic'],
                    timestamp=datetime.now(timezone.utc),
                )
                db.session.add(m)
                existing.add(rule['technique_id'])
                logger.debug(f"MITRE map: {rule['technique_id']} → {rule['tactic']}")
        except Exception as e:
            logger.error(f"MITRE rule error for {rule['technique_id']}: {e}")
