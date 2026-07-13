"""
detections/ioc_engine.py
─────────────────────────
IOC (Indicator of Compromise) matching engine.
Loads bad_processes.json, bad_ips.json, bad_hashes.json
and matches incoming event data against them.
"""

import os
import json
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

_ioc_cache: dict = {}
_ioc_loaded = False


def _load_iocs(ioc_dir: str) -> dict:
    global _ioc_cache, _ioc_loaded
    if _ioc_loaded:
        return _ioc_cache

    iocs = {'processes': [], 'ips': [], 'hashes': []}

    files = {
        'processes': 'bad_processes.json',
        'ips':       'bad_ips.json',
        'hashes':    'bad_hashes.json',
    }

    for key, fname in files.items():
        fpath = os.path.join(ioc_dir, fname)
        if os.path.exists(fpath):
            try:
                with open(fpath, 'r') as f:
                    data = json.load(f)
                    iocs[key] = [str(x).lower() for x in data.get('iocs', [])]
                    logger.info(f"Loaded {len(iocs[key])} IOCs from {fname}")
            except Exception as e:
                logger.error(f"Failed to load {fname}: {e}")

    _ioc_cache = iocs
    _ioc_loaded = True
    return iocs


def run_ioc_detection(event, data: dict):
    """
    Check event data against all IOC lists.
    Creates Alert (and MitreEvent for known technique) on match.
    """
    from flask import current_app
    from database.db import db
    from database.models import Alert, MitreEvent

    ioc_dir = current_app.config.get('IOC_DIR', 'iocs')
    iocs = _load_iocs(ioc_dir)

    matched_iocs = []

    # ── Process name check ──────────────────────────────────
    proc_name = str(data.get('name', '')).lower()
    proc_cmd  = str(data.get('cmdline', '')).lower()
    for bad_proc in iocs['processes']:
        if bad_proc in proc_name or bad_proc in proc_cmd:
            matched_iocs.append(('process', bad_proc))

    # ── IP check ────────────────────────────────────────────
    remote_ip = str(data.get('remote_address', '')).lower()
    local_ip  = str(data.get('local_address',  '')).lower()
    for bad_ip in iocs['ips']:
        if bad_ip == remote_ip or bad_ip == local_ip:
            matched_iocs.append(('ip', bad_ip))

    # ── Hash check ──────────────────────────────────────────
    for hash_field in ('sha256', 'md5', 'sha1'):
        file_hash = str(data.get(hash_field, '')).lower()
        if file_hash and file_hash in iocs['hashes']:
            matched_iocs.append(('hash', file_hash))

    for ioc_type, ioc_value in matched_iocs:
        desc = f"IOC Match [{ioc_type.upper()}]: {ioc_value}"
        alert = Alert(
            timestamp=datetime.now(timezone.utc),
            alert_name=f"IOC Detected — {ioc_type.title()}",
            severity='high',
            status='open',
            description=desc,
            hostname=event.hostname,
            event_id=event.id,
            source='ioc',
        )
        db.session.add(alert)

        # Map to MITRE technique based on IOC type
        technique_map = {
            'process': ('T1059', 'Command and Scripting Interpreter', 'Execution'),
            'ip':      ('T1071', 'Application Layer Protocol',        'Command and Control'),
            'hash':    ('T1204', 'User Execution',                    'Execution'),
        }
        tid, tname, tactic = technique_map.get(ioc_type, ('T1000', 'Unknown', 'Unknown'))
        m = MitreEvent(
            event_id=event.id,
            technique_id=tid,
            technique_name=tname,
            tactic=tactic,
            timestamp=datetime.now(timezone.utc),
        )
        db.session.add(m)
        logger.warning(f"IOC MATCH [{ioc_type}] '{ioc_value}' on {event.hostname}")
