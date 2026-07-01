import pytest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.services.ai.detection_agent import DetectionAgent
from app.services.ai.incident_analyst_agent import IncidentAnalystAgent

@patch('app.services.ai.llm_client.LLMClient.generate')
def test_detection_agent_false_positive(mock_generate):
    # Mock the LLM returning a false positive classification
    mock_generate.return_value = '{"is_false_positive": true, "confidence": 0.95, "reasoning": "Standard IT admin behavior"}'
    
    agent = DetectionAgent()
    alert_context = {"title": "PowerShell Script", "cmdline": "powershell.exe Get-Process"}
    
    result = agent.process(alert_context)
    
    assert result["is_false_positive"] is True
    assert result["confidence"] == 0.95

@patch('app.services.ai.llm_client.LLMClient.generate')
def test_incident_analyst_agent(mock_generate):
    # Mock the LLM investigation output
    mock_generate.return_value = '''{
        "root_cause": "Phishing email execution",
        "mitre_mapping": ["T1566", "T1059.001"],
        "timeline_events": [
            {"timestamp": "12:00", "description": "Word opened", "mitre": "T1566"}
        ],
        "recommended_actions": ["Isolate host"],
        "confidence_score": 0.92
    }'''
    
    agent = IncidentAnalystAgent()
    telemetry_context = [{"pid": 123, "name": "WINWORD.EXE"}]
    
    context = {"alert_id": 1, "telemetry_context": telemetry_context}
    result = agent.process(context)
    
    assert result["root_cause"] == "Phishing email execution"
    assert "T1566" in result["mitre_mapping"]
    assert result["confidence_score"] == 0.92
