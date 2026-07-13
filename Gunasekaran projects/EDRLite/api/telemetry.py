import json
import logging
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify, current_app
from functools import wraps

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__)

def require_agent_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        expected_token = current_app.config.get('AGENT_AUTH_TOKEN')
        if not token or token != f"Bearer {expected_token}":
            return jsonify({'error': 'Unauthorized', 'message': 'Invalid or missing Agent Auth Token'}), 401
        return f(*args, **kwargs)
    return decorated

def _ensure_endpoint(hostname, ip_address, os_version):
    """Create or update endpoint record based on agent payload."""
    from database.db import db
    from database.models import Endpoint
    
    ep = Endpoint.query.filter_by(hostname=hostname).first()
    if not ep:
        ep = Endpoint(hostname=hostname, ip_address=ip_address, os_version=os_version)
        db.session.add(ep)
    else:
        ep.ip_address = ip_address
        ep.os_version = os_version
        ep.last_seen = datetime.now(timezone.utc)
    db.session.commit()
    return ep

@api_bp.route('/telemetry/<event_type>', methods=['POST'])
@require_agent_auth
def receive_telemetry(event_type):
    """
    Receives telemetry from an agent.
    Payload format:
    {
        "hostname": "GUNASEKARAN",
        "ip_address": "192.168.1.10",
        "os_version": "Windows 11",
        "events": [ { ...osquery_row... }, ... ]
    }
    """
    from database.db import db
    from database.models import RawEvent
    
    # Import engines for process pipeline
    from detections.sigma_engine import run_sigma_detection
    from detections.ioc_engine import run_ioc_detection
    from detections.ai_engine import run_ai_detection
    from detections.virustotal import check_virustotal
    from detections.mitre_mapper import map_event
    from detections.risk_engine import calculate_risk
    
    data = request.json
    if not data:
        return jsonify({'error': 'Invalid payload'}), 400
        
    hostname = data.get('hostname', 'unknown-host')
    ip_address = data.get('ip_address', '0.0.0.0')
    os_version = data.get('os_version', 'Unknown OS')
    events = data.get('events', [])
    
    _ensure_endpoint(hostname, ip_address, os_version)
    
    if not events:
        return jsonify({'status': 'ok', 'message': 'No events to process.'})
        
    logger.info(f"Received {len(events)} {event_type} events from {hostname}.")

    for item in events:
        # Create RawEvent
        event_record = RawEvent(
            timestamp=datetime.now(timezone.utc),
            event_type=event_type,
            event_data=json.dumps(item),
            hostname=hostname,
        )
        db.session.add(event_record)
        db.session.flush() # Need event ID
        
        # Pipeline execution depending on event_type
        if event_type == 'process':
            run_sigma_detection(event_record, item)
            run_ioc_detection(event_record, item)
            run_ai_detection(event_record, item)
            check_virustotal(event_record, item)
            map_event(event_record, item)
            calculate_risk(event_record)
        elif event_type == 'network':
            run_sigma_detection(event_record, item)
            run_ioc_detection(event_record, item)
            map_event(event_record, item)
            calculate_risk(event_record)
        elif event_type == 'startup':
            run_sigma_detection(event_record, item)
            map_event(event_record, item)
            calculate_risk(event_record)
        elif event_type == 'usb':
            run_sigma_detection(event_record, item)
            calculate_risk(event_record)

    db.session.commit()
    return jsonify({'status': 'success', 'processed': len(events)})
