"""
collectors/network_collector.py
────────────────────────────────
Collects network socket data via osquery.
"""

import json
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

NETWORK_QUERY = """
SELECT
    pid,
    fd,
    socket,
    family,
    protocol,
    local_address,
    local_port,
    remote_address,
    remote_port,
    state
FROM process_open_sockets
WHERE remote_address != ''
  AND remote_address != '0.0.0.0'
  AND remote_address != '::'
LIMIT 300;
"""

LISTENING_QUERY = """
SELECT
    pid,
    port,
    protocol,
    address,
    socket
FROM listening_ports
WHERE port != 0
LIMIT 100;
"""


def collect_network(app):
    """Collect active network connections and listening ports."""
    with app.app_context():
        from collectors.osquery_runner import run_query
        from database.db import db
        from database.models import RawEvent
        from detections.sigma_engine import run_sigma_detection
        from detections.ioc_engine import run_ioc_detection
        from detections.mitre_mapper import map_event
        from detections.risk_engine import calculate_risk
        import socket

        hostname = _get_hostname()

        connections = run_query(NETWORK_QUERY)
        listening   = run_query(LISTENING_QUERY)

        rows = [{'connection_type': 'active',    **c} for c in connections] + \
               [{'connection_type': 'listening', **l} for l in listening]

        if not rows:
            logger.info("No network data from osquery.")
            return

        logger.info(f"Collected {len(rows)} network records.")

        for conn in rows:
            event = RawEvent(
                timestamp=datetime.now(timezone.utc),
                event_type='network',
                event_data=json.dumps(conn),
                hostname=hostname,
            )
            db.session.add(event)
            db.session.flush()

            run_sigma_detection(event, conn)
            run_ioc_detection(event, conn)
            map_event(event, conn)
            calculate_risk(event)

        db.session.commit()
        logger.info("Network collection complete.")


def _get_hostname():
    import socket
    try:
        return socket.gethostname()
    except Exception:
        return 'unknown-host'
