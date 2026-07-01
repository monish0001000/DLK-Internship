import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.services.detection.behavioral_detector import BehavioralDetector
from app.services.detection.sigma_engine import SigmaEngine, SigmaRule
from app.services.detection.ioc_matcher import IOCMatcher

def test_behavioral_detector_encoded_powershell():
    detector = BehavioralDetector()
    event = {
        "name": "powershell.exe",
        "cmdline": "powershell.exe -w hidden -enc JABzAGUAYwB1AHIAZQA="
    }
    
    # We should match on '-enc' flag
    alerts = detector.evaluate_event(event, category="process_creation")
    assert len(alerts) == 1
    assert alerts[0]["title"] == "Encoded PowerShell Execution"
    assert "attack.T1059.001" in alerts[0]["tags"]

def test_sigma_engine_basic_match():
    engine = SigmaEngine()
    
    # Create a mock rule
    yaml_content = """
title: Suspicious Cmdline
id: 1234
logsource:
    category: process_creation
    product: windows
detection:
    selection:
        cmdline|contains: 'mimikatz'
    condition: selection
"""
    rule = engine.load_rule_from_yaml(yaml_content)
    engine.rules.append(rule)
    
    event = {
        "cmdline": "c:\\tools\\mimikatz.exe privilege::debug"
    }
    
    matches = engine.evaluate_event(event, category="process_creation")
    assert len(matches) == 1
    assert matches[0]["title"] == "Suspicious Cmdline"

def test_ioc_matcher_hit():
    matcher = IOCMatcher()
    # Mocking threat intel cache locally
    matcher.malicious_ips = {
        "185.20.10.1": {"severity": "critical", "description": "C2 Server"}
    }
    
    event = {
        "remote_address": "185.20.10.1",
        "protocol": "tcp"
    }
    
    matches = matcher.match_event(event, category="network_connection")
    assert len(matches) == 1
    assert matches[0]["matched_value"] == "185.20.10.1"
    assert matches[0]["severity"] == "critical"
