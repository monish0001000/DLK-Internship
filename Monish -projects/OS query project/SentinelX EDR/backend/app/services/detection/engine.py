"""
SentinelX EDR - Detection Engine Orchestrator
===============================================
Coordinates the various detection strategies (Sigma, IOC, Behavioral, Plugins).
"""

import logging
from typing import List, Dict, Any, Callable
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.services.detection.sigma_engine import SigmaEngine
from app.services.detection.ioc_matcher import IOCMatcher
from app.services.detection.behavioral_detector import BehavioralDetector
from app.services.detection.plugin_loader import PluginManager
from app.models.alert import Alert

logger = logging.getLogger(__name__)

class DetectionEngine:
    def __init__(self):
        self.sigma_engine = SigmaEngine()
        self.ioc_matcher = IOCMatcher()
        self.behavioral_detector = BehavioralDetector()
        self.plugin_manager = PluginManager()
        self.alert_callbacks: List[Callable] = []
        
    def initialize(self, db: Session, settings: Any) -> None:
        """Initialize all detection components."""
        logger.info("Initializing Detection Engine...")
        
        # Load Sigma Rules
        self.sigma_engine.load_rules_from_directory(settings.SIGMA_RULES_DIR)
        
        # Load IOCs from DB
        self.ioc_matcher.load_from_db(db)
        
        # Load Plugins
        self.plugin_manager.load_plugins(settings.PLUGIN_DIR)
        
        logger.info("Detection Engine initialized successfully")
        
    def on_alert(self, callback: Callable) -> None:
        """Register a callback for when an alert is generated."""
        self.alert_callbacks.append(callback)
        
    def process_telemetry(self, data: Dict[str, Any]) -> None:
        """Process an entire telemetry ingest batch."""
        from app.database import SessionLocal
        
        db = SessionLocal()
        try:
            endpoint_id = data.get("endpoint_id")
            
            for category in ["processes", "network_connections", "startup_items", "services", "scheduled_tasks", "user_sessions"]:
                items = data.get(category, [])
                for item in items:
                    self.process_event(db, item, endpoint_id, category)
        except Exception as e:
            logger.error(f"Error processing telemetry batch: {e}")
        finally:
            db.close()
        
    def process_event(self, db: Session, event: Dict[str, Any], endpoint_id: str, category: str) -> List[Alert]:
        """Process a single event through all detection mechanisms."""
        alerts = []
        all_matches = []
        
        # 1. Sigma Engine
        sigma_matches = self.sigma_engine.evaluate_event(event, category)
        for match in sigma_matches:
            match["rule_type"] = "sigma"
            all_matches.append(match)
            
        # 2. IOC Matcher
        ioc_matches = self.ioc_matcher.match_event(event, category)
        for match in ioc_matches:
            match["rule_type"] = "ioc"
            all_matches.append(match)
            
        # 3. Behavioral Detector
        behavioral_matches = self.behavioral_detector.evaluate_event(event, category)
        for match in behavioral_matches:
            match["rule_type"] = "behavioral"
            all_matches.append(match)
            
        # 4. Plugins
        context = {"db": db, "endpoint_id": endpoint_id}
        plugin_matches = self.plugin_manager.evaluate_event(event, category, context)
        for match in plugin_matches:
            match["rule_type"] = "plugin"
            all_matches.append(match)
            
        # Create Alert records for all matches
        for match in all_matches:
            alert = self._create_alert(db, match, event, endpoint_id)
            alerts.append(alert)
            
            # Fire callbacks (e.g., for WebSockets or AI investigation trigger)
            for cb in self.alert_callbacks:
                try:
                    cb(alert)
                except Exception as e:
                    logger.error(f"Alert callback failed: {e}")
                    
        return alerts
        
    def _create_alert(self, db: Session, match: Dict[str, Any], event: Dict[str, Any], endpoint_id: str) -> Alert:
        """Create and save an Alert record in the database."""
        import json
        
        tags = match.get("tags", [])
        mitre_tactic = None
        mitre_technique = None
        
        # Extract MITRE technique from tags (e.g., attack.t1059.001)
        for tag in tags:
            tag_lower = tag.lower()
            if tag_lower.startswith("attack.t"):
                mitre_technique = tag.split(".")[1].upper()
                if len(tag.split(".")) > 2:
                    mitre_technique += "." + tag.split(".")[2]
                break
                
        # Simplistic tactic mapping based on technique
        # In a real system, use the MitreMapper service
        if mitre_technique:
            if mitre_technique.startswith("T1059"):
                 mitre_tactic = "Execution"
            elif mitre_technique.startswith("T1003"):
                 mitre_tactic = "Credential Access"
                 
        alert = Alert(
            endpoint_id=endpoint_id,
            title=match.get("title", "Unknown Alert"),
            description=match.get("description", ""),
            severity=match.get("severity", "medium").lower(),
            status="open",
            rule_name=match.get("title", ""),
            rule_type=match.get("rule_type", "unknown"),
            rule_id=match.get("rule_id", ""),
            mitre_tactic=mitre_tactic,
            mitre_technique=mitre_technique,
            evidence=json.dumps(event),
            detected_at=datetime.now(timezone.utc)
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)
        return alert

# Global singleton instance
engine = DetectionEngine()
