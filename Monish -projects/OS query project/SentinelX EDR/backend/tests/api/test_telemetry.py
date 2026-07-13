import pytest
from datetime import datetime, timezone

def test_ingest_telemetry_valid(client):
    payload = {
        "endpoint_id": "HOST-TEST-01",
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "processes": [
            {
                "pid": 1234,
                "name": "powershell.exe",
                "path": "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe",
                "cmdline": "powershell.exe -enc JABz...",
                "user": "jdoe",
                "parent_pid": 1000,
                "parent_name": "cmd.exe",
                "hash_sha256": "abcdef123456"
            }
        ],
        "network_connections": [],
        "startup_items": [],
        "services": [],
        "scheduled_tasks": [],
        "user_sessions": []
    }
    
    response = client.post("/api/v1/telemetry/ingest", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["inserted"]["processes"] == 1

def test_ingest_telemetry_invalid_payload(client):
    # Missing required field 'endpoint_id'
    payload = {
        "processes": []
    }
    response = client.post("/api/v1/telemetry/ingest", json=payload)
    assert response.status_code == 422  # Unprocessable Entity (Validation Error)
