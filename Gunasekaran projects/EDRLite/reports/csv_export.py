"""
reports/csv_export.py
──────────────────────
Exports events, alerts, MITRE mappings, risk scores to CSV files
and packages them into a ZIP archive.
"""

import os
import io
import zipfile
from datetime import datetime, timezone
import pandas as pd


def generate_csv_zip() -> str:
    """Generate ZIP of CSV files and return path."""
    from flask import current_app
    from database.models import RawEvent, Alert, MitreEvent, RiskScore

    reports_dir = current_app.config.get('REPORTS_DIR', 'reports_output')
    os.makedirs(reports_dir, exist_ok=True)

    ts       = datetime.now().strftime('%Y%m%d_%H%M%S')
    filepath = os.path.join(reports_dir, f'EDRLite_CSV_{ts}.zip')

    with zipfile.ZipFile(filepath, 'w', zipfile.ZIP_DEFLATED) as zf:

        # Events
        events = RawEvent.query.order_by(RawEvent.timestamp.desc()).limit(5000).all()
        events_data = [
            {'id': e.id, 'timestamp': e.timestamp, 'event_type': e.event_type,
             'hostname': e.hostname, 'event_data': str(e.get_data())}
            for e in events
        ]
        if events_data:
            df = pd.DataFrame(events_data)
            zf.writestr('events.csv', df.to_csv(index=False))

        # Alerts
        alerts = Alert.query.order_by(Alert.timestamp.desc()).all()
        alerts_data = [a.to_dict() for a in alerts]
        if alerts_data:
            df = pd.DataFrame(alerts_data)
            zf.writestr('alerts.csv', df.to_csv(index=False))

        # MITRE Events
        mitres = MitreEvent.query.all()
        mitre_data = [m.to_dict() for m in mitres]
        if mitre_data:
            df = pd.DataFrame(mitre_data)
            zf.writestr('mitre_events.csv', df.to_csv(index=False))

        # Risk Scores
        risks = RiskScore.query.order_by(RiskScore.calculated_at.desc()).limit(5000).all()
        risk_data = [r.to_dict() for r in risks]
        if risk_data:
            df = pd.DataFrame(risk_data)
            zf.writestr('risk_scores.csv', df.to_csv(index=False))

    return filepath
