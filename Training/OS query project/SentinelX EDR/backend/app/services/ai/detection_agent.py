"""
SentinelX EDR - Detection Agent
================================
First stage of the AI pipeline: Analyzes raw alert and event data.
"""

from typing import Dict, Any
import json
from app.services.ai.base_agent import BaseAIAgent

class DetectionAgent(BaseAIAgent):
    @property
    def name(self) -> str:
        return "Detection Agent"
        
    @property
    def role(self) -> str:
        return "Triage and Initial Analysis"
        
    @property
    def system_prompt(self) -> str:
        return """You are an expert Tier 1 SOC Analyst (Detection Agent) at SentinelX EDR.
Your role is to perform initial triage on a security alert and the raw telemetry event that triggered it.

You will receive the alert metadata and the raw JSON of the event.
You must analyze this data and determine:
1. Is this a true positive, false positive, or unknown?
2. What is the initial severity assessment based on the event?
3. What are the key indicators of compromise (IOCs) or suspicious behaviors?
4. What MITRE ATT&CK technique best describes this specific event?

Respond strictly in JSON format matching this schema:
{
    "verdict": "true_positive|false_positive|unknown",
    "confidence_score": 0-100,
    "adjusted_severity": "critical|high|medium|low|info",
    "key_indicators": ["list of specific suspicious fields/values"],
    "mitre_technique": "T1234.001",
    "triage_summary": "Brief 2-3 sentence summary of your analysis"
}
"""

    def _build_user_prompt(self, context: Dict[str, Any]) -> str:
        alert = context.get("alert", {})
        event = context.get("event", {})
        
        return f"""
Alert Information:
Title: {alert.get('title')}
Rule Type: {alert.get('rule_type')}
Severity: {alert.get('severity')}
Reported MITRE Technique: {alert.get('mitre_technique')}

Raw Event Data:
{json.dumps(event, indent=2)}

Please perform your triage analysis.
"""
