"""
SentinelX EDR - Attack Simulator Service
==========================================
Simulates attacks by injecting mock telemetry, used for testing rules and the AI pipeline.
"""

import logging
import json
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.simulation import SimulationRun
from app.models.endpoint import Endpoint
from app.schemas.simulation import SimulationStart
from app.schemas.telemetry import TelemetryIngest, ProcessData, NetworkData
from app.services.telemetry_service import ingest_telemetry

logger = logging.getLogger(__name__)

# Predefined scenarios
SCENARIOS = {
    "ransomware_wannacry": {
        "name": "WannaCry Ransomware Simulation",
        "description": "Simulates the process and network behavior of WannaCry ransomware.",
        "attack_type": "ransomware",
        "mitre_techniques": ["T1486", "T1059.003", "T1105"],
        "estimated_events": 5,
        "events": [
            {
                "type": "process",
                "data": {"pid": 1001, "name": "cmd.exe", "path": "C:\\Windows\\System32\\cmd.exe", "cmdline": "cmd.exe /c vssadmin.exe Delete Shadows /All /Quiet", "parent_pid": 1000, "parent_name": "tasksche.exe"}
            },
            {
                "type": "process",
                "data": {"pid": 1002, "name": "vssadmin.exe", "path": "C:\\Windows\\System32\\vssadmin.exe", "cmdline": "vssadmin.exe Delete Shadows /All /Quiet", "parent_pid": 1001, "parent_name": "cmd.exe"}
            },
            {
                "type": "network",
                "data": {"pid": 1000, "process_name": "tasksche.exe", "local_address": "192.168.1.100", "local_port": 49152, "remote_address": "188.166.23.127", "remote_port": 443, "protocol": "tcp", "state": "ESTABLISHED"}
            }
        ]
    },
    "lateral_movement_psexec": {
        "name": "PsExec Lateral Movement",
        "description": "Simulates lateral movement via PsExec service creation and execution.",
        "attack_type": "lateral_movement",
        "mitre_techniques": ["T1569.002", "T1047"],
        "estimated_events": 3,
        "events": [
            {
                "type": "process",
                "data": {"pid": 2001, "name": "PSEXESVC.exe", "path": "C:\\Windows\\PSEXESVC.exe", "cmdline": "PSEXESVC.exe", "parent_pid": 4, "parent_name": "System"}
            },
            {
                "type": "process",
                "data": {"pid": 2002, "name": "cmd.exe", "path": "C:\\Windows\\System32\\cmd.exe", "cmdline": "cmd.exe /c whoami", "parent_pid": 2001, "parent_name": "PSEXESVC.exe"}
            }
        ]
    }
}

def start_simulation(db: Session, request: SimulationStart) -> SimulationRun:
    """Inject mock telemetry based on a scenario."""
    scenario = SCENARIOS.get(request.scenario_name)
    if not scenario:
        raise ValueError(f"Unknown scenario: {request.scenario_name}")
        
    endpoint_id = request.endpoint_id
    if not endpoint_id:
        # Create or use a dummy endpoint for simulations
        endpoint_id = "sim-target-01"
        ep = db.query(Endpoint).filter(Endpoint.id == endpoint_id).first()
        if not ep:
            ep = Endpoint(id=endpoint_id, hostname="SIM-WIN10-01", ip_address="192.168.1.50", os_type="windows", status="online", tags="simulation")
            db.add(ep)
            db.commit()
            
    # Create the SimulationRun record
    sim_id = str(uuid.uuid4())
    run = SimulationRun(
        id=sim_id,
        scenario_name=scenario["name"],
        status="running",
        endpoint_id=endpoint_id,
        events_generated=0,
        alerts_triggered=0,
        started_at=datetime.now(timezone.utc)
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    
    # Generate Telemetry
    processes = []
    networks = []
    
    for ev in scenario.get("events", []):
        if ev["type"] == "process":
            processes.append(ProcessData(**ev["data"]))
        elif ev["type"] == "network":
            networks.append(NetworkData(**ev["data"]))
            
    telemetry = TelemetryIngest(
        endpoint_id=endpoint_id,
        processes=processes,
        network_connections=networks,
        startup_items=[],
        services=[],
        scheduled_tasks=[],
        user_sessions=[],
        collected_at=datetime.now(timezone.utc)
    )
    
    # Ingest telemetry (this won't directly trigger alerts yet in this flow without engine, 
    # but in a real app, ingest_telemetry might call engine.process_event or a celery task)
    counts = ingest_telemetry(db, telemetry)
    
    # In our simplified sync flow, we'd manually process these through the DetectionEngine if we wanted immediate alerts
    # We will simulate the engine processing here for the sake of the scenario
    from app.services.detection.engine import engine
    alerts_triggered = 0
    rules_matched = []
    
    for p in processes:
        p_dict = p.model_dump(exclude_none=True)
        new_alerts = engine.process_event(db, p_dict, endpoint_id, "process_creation")
        alerts_triggered += len(new_alerts)
        rules_matched.extend([a.rule_name for a in new_alerts])
        
    for n in networks:
        n_dict = n.model_dump(exclude_none=True)
        new_alerts = engine.process_event(db, n_dict, endpoint_id, "network_connection")
        alerts_triggered += len(new_alerts)
        rules_matched.extend([a.rule_name for a in new_alerts])
    
    # Complete simulation
    run.status = "completed"
    run.events_generated = counts["processes"] + counts["network_connections"]
    run.alerts_triggered = alerts_triggered
    run.rules_matched = json.dumps(list(set(rules_matched)))
    run.completed_at = datetime.now(timezone.utc)
    
    # Calculate simplistic coverage
    expected_techniques = set(scenario.get("mitre_techniques", []))
    covered = min(len(set(rules_matched)), len(expected_techniques)) # Mocked stat
    run.detection_coverage_pct = int((covered / max(len(expected_techniques), 1)) * 100)
    
    db.commit()
    db.refresh(run)
    
    return run

def list_scenarios() -> List[Dict[str, Any]]:
    result = []
    for k, v in SCENARIOS.items():
        result.append({
            "id": k,
            "name": v["name"],
            "description": v["description"],
            "attack_type": v["attack_type"],
            "mitre_techniques": v["mitre_techniques"],
            "estimated_events": v["estimated_events"]
        })
    return result

def get_simulation(db: Session, sim_id: str) -> Optional[SimulationRun]:
    return db.query(SimulationRun).filter(SimulationRun.id == sim_id).first()
