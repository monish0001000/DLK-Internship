"""
SentinelX EDR - Response Planner Agent
=======================================
Parallel Stage 4: Generates a containment and remediation playbook.
"""

from typing import Dict, Any
import json
from app.services.ai.base_agent import BaseAIAgent

class ResponsePlannerAgent(BaseAIAgent):
    @property
    def name(self) -> str:
        return "Response Planner Agent"
        
    @property
    def role(self) -> str:
        return "Playbook Generation and Remediation Planning"
        
    @property
    def system_prompt(self) -> str:
        return """You are a Lead Incident Responder at SentinelX EDR.
Based on the Incident Analyst's findings, you must generate a step-by-step response and remediation playbook.

Your playbook should include actionable containment steps (e.g., isolate endpoint, block IP, kill process) and long-term remediation advice.

Respond strictly in JSON format matching this schema:
{
    "priority": "critical|high|medium|low",
    "immediate_containment_actions": [
        {"action": "isolate_endpoint", "target": "endpoint_id", "reason": "..."}
    ],
    "remediation_steps": ["Step 1", "Step 2"],
    "response_rationale": "Explanation of why these steps are necessary"
}
"""

    def _build_user_prompt(self, context: Dict[str, Any]) -> str:
        analyst = context.get("pipeline_results", {}).get("Incident Analyst Agent", {})
        endpoint_id = context.get("alert", {}).get("endpoint_id", "unknown")
        
        return f"""
Endpoint ID: {endpoint_id}
Incident Analyst Assessment:
{json.dumps(analyst, indent=2)}

Please generate the response playbook.
"""
