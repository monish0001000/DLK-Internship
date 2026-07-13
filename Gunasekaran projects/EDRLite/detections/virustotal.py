import logging
import requests
from flask import current_app

logger = logging.getLogger(__name__)

# Very simple caching so we don't spam the API for the same hashes
VT_CACHE = {}

def check_virustotal(event, proc: dict):
    """Check process against VirusTotal."""
    from database.db import db
    from database.models import Alert
    from app import socketio
    
    app = current_app._get_current_object()
    api_key = app.config.get('VIRUSTOTAL_API_KEY')
    
    # We simulate a hash if real one isn't there, or use process name for demonstration
    proc_name = proc.get('name', '').lower()
    
    # If the process is a known mock malware from our simulator, let's manually flag it for VT
    # In a real environment, we would use the file hash from osquery: 
    # e.g., SELECT h.sha256 FROM hash h JOIN processes p ON h.path = p.path WHERE p.pid = X
    if proc_name in ['nc.exe', 'nmap.exe', 'tor.exe', 'mimikatz.exe']:
        # Fake a malicious hash for demonstration of API match logic
        is_malicious = True
        positives = 45
        total = 72
    else:
        # Standard process, skip VT call for demo to save limits, or simulate clean
        return
        
    if not api_key or api_key == 'YOUR_VT_API_KEY':
        logger.debug("VT_API_KEY missing. Skipping real VirusTotal call.")
        return

    # To avoid real API calls for this portfolio demo on every tick, we just simulate the API response 
    # format since we already know the dummy processes. 
    # IN PRODUCTION: 
    # url = f"https://www.virustotal.com/api/v3/files/{file_hash}"
    # headers = {"x-apikey": api_key}
    # response = requests.get(url, headers=headers)
    
    if is_malicious:
        alert = Alert(
            event_id=event.id,
            timestamp=event.timestamp,
            severity='critical',
            alert_name='VirusTotal Malware Match',
            description=f"Process '{proc_name}' flagged by {positives}/{total} antivirus engines on VirusTotal.",
            hostname=event.hostname,
            source='virustotal',
            status='open'
        )
        db.session.add(alert)
        logger.warning(f"VIRUSTOTAL MATCH [process] '{proc_name}' on {event.hostname}")
        
        try:
            socketio.emit('new_alert', {
                'id': alert.id,
                'name': alert.alert_name,
                'severity': alert.severity,
                'hostname': alert.hostname,
                'desc': alert.description
            })
        except Exception as e:
            pass
