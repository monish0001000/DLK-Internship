import logging
import psutil
from sklearn.ensemble import IsolationForest
import numpy as np

logger = logging.getLogger(__name__)

class AIEngine:
    def __init__(self):
        self.model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
        self.is_trained = False
        
    def train_baseline(self):
        """Train on dummy baseline normal processes to simulate anomaly detection."""
        # Features: [cmdline_length, has_args, is_system_path]
        normal_data = [
            [12, 0, 1], # explorer.exe
            [25, 1, 1], # chrome.exe --type=renderer
            [15, 0, 1], # svchost.exe
            [18, 1, 1], # services.exe
            [10, 0, 1], # csrss.exe
            [20, 1, 1], # winlogon.exe
            [14, 0, 1], # lsass.exe
            [12, 0, 1], # smss.exe
            [22, 1, 1], # taskhostw.exe
            [16, 0, 1]  # dwm.exe
        ]
        self.model.fit(normal_data)
        self.is_trained = True
        logger.info("AI Engine (IsolationForest) trained on baseline processes.")

    def analyze_process(self, proc: dict) -> bool:
        """Returns True if process is an ANOMALY, False if NORMAL."""
        if not self.is_trained:
            self.train_baseline()
            
        cmdline = proc.get('cmdline', '')
        path = proc.get('path', '')
        
        # Feature Extraction
        cmdline_len = len(cmdline)
        has_args = 1 if ' ' in str(cmdline).strip() else 0
        is_system_path = 1 if 'windows' in str(path).lower() or 'program files' in str(path).lower() else 0
        
        # Malicious characteristics often have very long cmdlines or run from weird paths (temp, appdata)
        features = np.array([[cmdline_len, has_args, is_system_path]])
        
        prediction = self.model.predict(features)
        return prediction[0] == -1  # -1 means anomaly in IsolationForest

ai_instance = AIEngine()

def run_ai_detection(event, proc: dict):
    """Run process through AI Anomaly detection."""
    from database.db import db
    from database.models import Alert
    from app import socketio
    
    is_anomaly = ai_instance.analyze_process(proc)
    
    if is_anomaly:
        alert = Alert(
            event_id=event.id,
            timestamp=event.timestamp,
            severity='high',
            alert_name='AI Anomaly Detected',
            description=f"AI model flagged process '{proc.get('name')}' as anomalous based on behavior/path.",
            hostname=event.hostname,
            source='ai_anomaly',
            status='open'
        )
        db.session.add(alert)
        logger.warning(f"AI ANOMALY MATCH [process] '{proc.get('name')}' on {event.hostname}")
        
        # Push real-time alert via WebSockets
        try:
            socketio.emit('new_alert', {
                'id': alert.id,
                'name': alert.alert_name,
                'severity': alert.severity,
                'hostname': alert.hostname,
                'desc': alert.description
            })
        except Exception as e:
            logger.error(f"WebSocket emit failed: {e}")
