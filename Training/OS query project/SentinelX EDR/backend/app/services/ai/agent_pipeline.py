"""
SentinelX EDR - Agent Pipeline Orchestrator
============================================
Chains the AI agents together to perform a complete investigation.
"""

import logging
import json
from datetime import datetime, timezone
from typing import Dict, Any
from sqlalchemy.orm import Session

from app.models.alert import Alert
from app.models.investigation import Investigation
from app.services.telemetry_service import query_processes, query_network_connections
from app.services.ai.detection_agent import DetectionAgent
from app.services.ai.threat_hunter_agent import ThreatHunterAgent
from app.services.ai.incident_analyst_agent import IncidentAnalystAgent
from app.services.ai.response_planner_agent import ResponsePlannerAgent
from app.services.ai.rule_suggestion_agent import RuleSuggestionAgent
from app.services.ai.llm_client import llm_client

logger = logging.getLogger(__name__)

class AgentPipeline:
    def __init__(self):
        self.detection_agent = DetectionAgent()
        self.hunter_agent = ThreatHunterAgent()
        self.analyst_agent = IncidentAnalystAgent()
        self.response_agent = ResponsePlannerAgent()
        self.rule_agent = RuleSuggestionAgent()
        
    def run_investigation(self, db: Session, alert_id: int) -> Investigation:
        """Run the full 5-agent investigation pipeline synchronously."""
        logger.info(f"Starting AI Investigation Pipeline for Alert {alert_id}")
        
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            raise ValueError(f"Alert {alert_id} not found")
            
        # Update alert status
        alert.status = "investigating"
        db.commit()
        
        # Create Investigation record
        inv = Investigation(
            alert_id=alert_id,
            status="running",
            ai_model=llm_client.settings.GEMINI_MODEL if llm_client.gemini_model else "mock"
        )
        db.add(inv)
        db.commit()
        db.refresh(inv)
        
        try:
            # 1. Gather Context
            event_data = {}
            if alert.evidence:
                try:
                    event_data = json.loads(alert.evidence)
                except:
                    pass
                    
            # Gather surrounding telemetry (±10 minutes)
            context_telemetry = {
                "processes": [p.__dict__ for p in query_processes(db, endpoint_id=alert.endpoint_id, limit=20)],
                "network": [n.__dict__ for n in query_network_connections(db, endpoint_id=alert.endpoint_id, limit=20)]
            }
            # Clean SQLAlchemy internal state from dicts
            for p in context_telemetry["processes"]: p.pop("_sa_instance_state", None)
            for n in context_telemetry["network"]: n.pop("_sa_instance_state", None)
            
            context = {
                "alert": {
                    "id": alert.id,
                    "title": alert.title,
                    "severity": alert.severity,
                    "rule_type": alert.rule_type,
                    "mitre_technique": alert.mitre_technique,
                    "endpoint_id": alert.endpoint_id
                },
                "event": event_data,
                "context_telemetry": context_telemetry,
                "pipeline_results": {}
            }
            
            # 2. Run Detection Agent
            det_result = self.detection_agent.process(context)
            context["pipeline_results"]["Detection Agent"] = det_result
            
            # 3. Run Threat Hunter Agent
            hunt_result = self.hunter_agent.process(context)
            context["pipeline_results"]["Threat Hunter Agent"] = hunt_result
            
            # 4. Run Incident Analyst Agent
            ana_result = self.analyst_agent.process(context)
            context["pipeline_results"]["Incident Analyst Agent"] = ana_result
            
            # 5. Run Response Planner & Rule Suggestion (can be conceptual parallel, but executed sequentially here)
            resp_result = self.response_agent.process(context)
            context["pipeline_results"]["Response Planner Agent"] = resp_result
            
            rule_result = self.rule_agent.process(context)
            context["pipeline_results"]["Rule Suggestion Agent"] = rule_result
            
            # 6. Update Investigation Record
            inv.pipeline_results = json.dumps(context["pipeline_results"])
            inv.summary = ana_result.get("analyst_summary", "")
            inv.root_cause = ana_result.get("root_cause_analysis", "")
            inv.risk_score = float(ana_result.get("risk_score", 0))
            inv.risk_level = str(ana_result.get("risk_level", "medium")).lower()
            inv.mitre_mapping = json.dumps(ana_result.get("mitre_mapping", []))
            
            # Construct simple timeline from hunt results
            timeline = [{"timestamp": datetime.now(timezone.utc).isoformat(), "event_type": "Attack Step", "description": step} 
                       for step in hunt_result.get("attack_chain_reconstructed", [])]
            inv.timeline = json.dumps(timeline)
            
            inv.recommendations = "\n".join(ana_result.get("recommendations", []))
            inv.response_plan = json.dumps(resp_result)
            inv.suggested_rules = json.dumps([rule_result])
            
            inv.status = "completed"
            inv.completed_at = datetime.now(timezone.utc)
            
            db.commit()
            db.refresh(inv)
            
            # Update alert severity if needed
            if det_result.get("adjusted_severity"):
                alert.severity = det_result.get("adjusted_severity").lower()
                db.commit()
                
            logger.info(f"Pipeline completed successfully for Investigation {inv.id}")
            return inv
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            inv.status = "failed"
            inv.error_message = str(e)
            db.commit()
            raise
