"""
SentinelX EDR - Threat Hunter Agent
====================================
Second stage: Correlates the alert with surrounding endpoint telemetry.
"""

from typing import Dict, Any
import json
from app.services.ai.base_agent import BaseAIAgent

class ThreatHunterAgent(BaseAIAgent):
    @property
    def name(self) -> str:
        return "Threat Hunter Agent"
        
    @property
    def role(self) -> str:
        return "Event Correlation and Attack Chain Reconstruction"
        
    @property
    def system_prompt(self) -> str:
        return """You are an expert Threat Hunter at SentinelX EDR.
Your role is to analyze a localized alert alongside contextual telemetry (processes, network connections) from the same endpoint around the same time.

Your objective is to reconstruct the attack chain and identify if this alert is part of a larger, coordinated attack.
Look for:
- Suspicious parent processes spawning the alerted process.
- Subsequent network connections made by suspicious processes.
- Any persistence mechanisms created around the same time.
- File drops or encoded command executions.

Respond strictly in JSON format matching this schema:
{
    "attack_chain_reconstructed": ["Step 1: ...", "Step 2: ..."],
    "related_suspicious_pids": [1234, 5678],
    "related_suspicious_ips": ["1.2.3.4"],
    "expanded_mitre_tactics": ["Execution", "Lateral Movement"],
    "hunter_notes": "Detailed paragraph explaining the correlation findings"
}
"""

    def _build_user_prompt(self, context: Dict[str, Any]) -> str:
        alert = context.get("alert", {})
        detection_output = context.get("pipeline_results", {}).get("Detection Agent", {})
        context_telemetry = context.get("context_telemetry", {})
        
        return f"""
Alert Information: {alert.get('title')}
Detection Agent Verdict: {detection_output.get('verdict')}

Contextual Telemetry (Last 10 minutes on Endpoint):
Processes:
{json.dumps(context_telemetry.get('processes', [])[:10], indent=2)}

Network Connections:
{json.dumps(context_telemetry.get('network', [])[:10], indent=2)}

Please analyze the contextual data and reconstruct the attack chain.
"""
