"""
collectors/startup_collector.py
────────────────────────────────
Collects startup items and crontab entries via osquery.
Maps to MITRE T1053 / T1547 (persistence).
"""

import json
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

STARTUP_QUERY = """
SELECT
    name,
    path,
    args,
    type,
    username,
    status
FROM startup_items;
"""

CRON_QUERY = """
SELECT
    event,
    minute,
    hour,
    day_of_month,
    month,
    day_of_week,
    command,
    path,
    username
FROM crontab;
"""


def collect_startup(app):
    """Collect startup items and cron jobs."""
    with app.app_context():
        from collectors.osquery_runner import run_query
        from database.db import db
        from database.models import RawEvent
        from detections.sigma_engine import run_sigma_detection
        from detections.ioc_engine import run_ioc_detection
        from detections.mitre_mapper import map_event
        from detections.risk_engine import calculate_risk

        hostname = _get_hostname()

        startup_rows = run_query(STARTUP_QUERY)
        cron_rows    = run_query(CRON_QUERY)

        rows = [{'source': 'startup_items', **s} for s in startup_rows] + \
               [{'source': 'crontab',       **c} for c in cron_rows]

        if not rows:
            logger.info("No startup/cron data from osquery.")
            return

        logger.info(f"Collected {len(rows)} startup/cron records.")

        for item in rows:
            event = RawEvent(
                timestamp=datetime.now(timezone.utc),
                event_type='startup',
                event_data=json.dumps(item),
                hostname=hostname,
            )
            db.session.add(event)
            db.session.flush()

            run_sigma_detection(event, item)
            run_ioc_detection(event, item)
            map_event(event, item)
            calculate_risk(event)

        db.session.commit()
        logger.info("Startup/cron collection complete.")


def _get_hostname():
    import socket
    try:
        return socket.gethostname()
    except Exception:
        return 'unknown-host'
