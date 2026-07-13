"""
collectors/usb_collector.py
────────────────────────────
Collects USB device insertions via osquery.
"""

import json
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

USB_QUERY = """
SELECT
    usb_address,
    usb_port,
    vendor,
    version,
    model,
    serial,
    removable
FROM usb_devices;
"""

BLOCK_QUERY = """
SELECT
    name,
    model,
    vendor,
    size,
    removable,
    type
FROM block_devices
WHERE removable = '1';
"""


def collect_usb(app):
    """Collect USB and removable block device events."""
    with app.app_context():
        from collectors.osquery_runner import run_query
        from database.db import db
        from database.models import RawEvent
        from detections.sigma_engine import run_sigma_detection
        from detections.ioc_engine import run_ioc_detection
        from detections.mitre_mapper import map_event
        from detections.risk_engine import calculate_risk

        hostname = _get_hostname()

        usb_rows   = run_query(USB_QUERY)
        block_rows = run_query(BLOCK_QUERY)

        rows = [{'source': 'usb_devices',  **u} for u in usb_rows] + \
               [{'source': 'block_devices', **b} for b in block_rows]

        if not rows:
            logger.info("No USB data from osquery.")
            return

        logger.info(f"Collected {len(rows)} USB/removable records.")

        for device in rows:
            event = RawEvent(
                timestamp=datetime.now(timezone.utc),
                event_type='usb',
                event_data=json.dumps(device),
                hostname=hostname,
            )
            db.session.add(event)
            db.session.flush()

            run_sigma_detection(event, device)
            run_ioc_detection(event, device)
            map_event(event, device)
            calculate_risk(event)

        db.session.commit()
        logger.info("USB collection complete.")


def _get_hostname():
    import socket
    try:
        return socket.gethostname()
    except Exception:
        return 'unknown-host'
