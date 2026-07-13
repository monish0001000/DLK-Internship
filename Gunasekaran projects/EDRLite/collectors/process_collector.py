"""
collectors/process_collector.py
────────────────────────────────
Collects running process data via osquery and stores in raw_events.
Triggers detection pipeline (Sigma + IOC + MITRE + Risk).
"""

import json
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

PROCESS_QUERY = """
SELECT
    pid,
    name,
    cmdline,
    path,
    uid,
    gid,
    parent,
    state,
    start_time
FROM processes
LIMIT 500;
"""


def collect_processes(app):
    """Called by APScheduler. Collects processes and runs detection pipeline."""
    with app.app_context():
        from collectors.osquery_runner import run_query
        from database.db import db
        from database.models import RawEvent, Endpoint
        from detections.sigma_engine import run_sigma_detection
        from detections.ioc_engine import run_ioc_detection
        from detections.mitre_mapper import map_event
        from detections.risk_engine import calculate_risk
        from detections.ai_engine import run_ai_detection
        from detections.virustotal import check_virustotal
        import socket

        hostname = _get_hostname()
        _ensure_endpoint(hostname, app)

        rows = run_query(PROCESS_QUERY)
        if not rows:
            logger.info("No process data returned from osquery.")
            return

        logger.info(f"Collected {len(rows)} processes from osquery.")

        for proc in rows:
            event = RawEvent(
                timestamp=datetime.now(timezone.utc),
                event_type='process',
                event_data=json.dumps(proc),
                hostname=hostname,
            )
            db.session.add(event)
            db.session.flush()  # get event.id

            # Run detection pipeline
            run_sigma_detection(event, proc)
            run_ioc_detection(event, proc)
            run_ai_detection(event, proc)
            check_virustotal(event, proc)
            map_event(event, proc)
            calculate_risk(event)

        db.session.commit()
        logger.info("Process collection and detection complete.")


def _get_hostname():
    import socket
    try:
        return socket.gethostname()
    except Exception:
        return 'unknown-host'


def _ensure_endpoint(hostname, app):
    """Create endpoint record if it doesn't exist."""
    from database.db import db
    from database.models import Endpoint
    from datetime import datetime, timezone
    from collectors.osquery_runner import run_query

    ep = Endpoint.query.filter_by(hostname=hostname).first()
    if not ep:
        # Try to get OS info
        os_rows = run_query("SELECT name, version FROM os_version LIMIT 1;")
        os_ver = f"{os_rows[0].get('name','')} {os_rows[0].get('version','')}" if os_rows else 'Unknown'
        ip_rows = run_query("SELECT address FROM interface_addresses WHERE interface != 'lo' LIMIT 1;")
        ip = ip_rows[0].get('address', '127.0.0.1') if ip_rows else '127.0.0.1'
        ep = Endpoint(hostname=hostname, ip_address=ip, os_version=os_ver)
        db.session.add(ep)
    else:
        ep.last_seen = datetime.now(timezone.utc)
    db.session.commit()
