"""
SentinelX EDR - Incident Analyst Agent
=======================================
Third stage: Determines root cause and overall risk score.
"""

from typing import Dict, Any
import json
from app.services.ai.base_agent import BaseAIAgent

class IncidentAnalystAgent(BaseAIAgent):
    @property
    def name(self) -> str:
        return "Incident Analyst Agent"
        
    @property
    def role(self) -> str:
        return "Root Cause Analysis and Risk Scoring"
        
    @property
    def system_prompt(self) -> str:
        return """You are a Senior Incident Analyst at SentinelX EDR.
You receive findings from the Detection Agent (triage) and Threat Hunter Agent (correlation).
Your job is to synthesize these findings into a final authoritative incident assessment.

You must determine:
1. The exact root cause (how the attacker got in or initiated the action).
2. A calculated risk score (0-100) based on impact, lateral movement potential, and data exfiltration risk.
3. The overall MITRE ATT&CK mapping for the entire incident.
4. Immediate recommendations for the SOC team.

Respond strictly in JSON format matching this schema:
{
    "root_cause_analysis": "Detailed explanation of the root cause",
    "risk_score": 85,
    "risk_level": "critical|high|medium|low",
    "mitre_mapping": [
        {"tactic": "Initial Access", "technique_id": "T1190", "name": "Exploit Public-Facing Application"}
    ],
    "analyst_summary": "Executive summary of the incident",
    "recommendations": ["Recommendation 1", "Recommendation 2"]
}
"""

    def _build_user_prompt(self, context: Dict[str, Any]) -> str:
        pipeline = context.get("pipeline_results", {})
        detection = pipeline.get("Detection Agent", {})
        hunter = pipeline.get("Threat Hunter Agent", {})
        
        return f"""
Detection Agent Findings:
{json.dumps(detection, indent=2)}

Threat Hunter Agent Findings:
{json.dumps(hunter, indent=2)}

Please synthesize this information, determine the root cause, assign a risk score, and map the full MITRE attack chain.
"""
