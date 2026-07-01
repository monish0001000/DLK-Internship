import sys
import requests
import uuid
import time
from config import BASE_URL, get_auth_token

def run():
    print("Testing Telemetry Ingestion...")
    try:
        token = get_auth_token()
        headers = {"Authorization": f"Bearer {token}"}

        # Need an endpoint first
        endpoint_data = {
            "id": str(uuid.uuid4()),
            "hostname": "telemetry-test-01",
            "ip_address": "192.168.1.101",
            "os_type": "linux",
            "os_version": "22.04",
            "agent_version": "1.0.0"
        }
        
        ep_response = requests.post(f"{BASE_URL}/endpoints/", json=endpoint_data, headers=headers)
        if ep_response.status_code != 200:
            raise Exception("Failed to register endpoint for telemetry test")
        
        endpoint_id = ep_response.json()["id"]

        # Test: Send Telemetry
        telemetry_payload = {
            "endpoint_id": endpoint_id,
            "osquery_version": "5.10.2",
            "data": {
                "processes": [
                    {"pid": "1234", "name": "test_proc", "path": "/usr/bin/test_proc", "cmdline": "test_proc --args"}
                ],
                "network_connections": [
                    {"local_address": "192.168.1.101", "local_port": "4444", "remote_address": "8.8.8.8", "remote_port": "53", "state": "ESTABLISHED"}
                ]
            }
        }

        tel_response = requests.post(f"{BASE_URL}/telemetry/ingest", json=telemetry_payload, headers=headers)
        if tel_response.status_code != 200:
            raise Exception(f"Failed to ingest telemetry. Status: {tel_response.status_code}")

        return True, "Telemetry ingestion passed"
    except Exception as e:
        return False, str(e)

if __name__ == "__main__":
    success, msg = run()
    if success:
        print(f"PASS: {msg}")
        sys.exit(0)
    else:
        print(f"FAIL: {msg}")
        sys.exit(1)
