"""
SentinelX EDR - Rule Suggestion Agent
======================================
Generates new Sigma rules based on novel attacks discovered during investigation.
"""

from typing import Dict, Any
import json
from app.services.ai.base_agent import BaseAIAgent

class RuleSuggestionAgent(BaseAIAgent):
    @property
    def name(self) -> str:
        return "Rule Suggestion Agent"
        
    @property
    def role(self) -> str:
        return "Detection Engineering"
        
    @property
    def system_prompt(self) -> str:
        return """You are an expert Detection Engineer at SentinelX EDR.
Your task is to write a highly specific, low-false-positive Sigma rule based on an incident investigation.

Review the incident details, focusing on the specific processes, command lines, or network indicators used by the attacker.
Write a valid Sigma YAML rule that would catch this specific behavior in the future.
The rule MUST follow the official Sigma format.

Respond strictly in JSON format matching this schema:
{
    "rule_name": "Name of the rule",
    "description": "What this rule detects and why it was created",
    "sigma_yaml": "The complete, valid YAML string of the Sigma rule",
    "expected_false_positives": "Potential FP scenarios"
}
"""

    def _build_user_prompt(self, context: Dict[str, Any]) -> str:
        pipeline = context.get("pipeline_results", {})
        hunter = pipeline.get("Threat Hunter Agent", {})
        analyst = pipeline.get("Incident Analyst Agent", {})
        
        return f"""
Threat Hunter Findings:
{json.dumps(hunter, indent=2)}

Incident Analyst Findings:
{json.dumps(analyst, indent=2)}

Write a Sigma rule to detect this specific behavior. Ensure the yaml is a valid string.
"""
