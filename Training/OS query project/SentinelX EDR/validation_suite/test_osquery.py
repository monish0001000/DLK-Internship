import sys
import requests
import uuid
from config import BASE_URL, get_auth_token

def run():
    print("Testing OSQuery Agent Endpoint Handling...")
    try:
        token = get_auth_token()
        headers = {"Authorization": f"Bearer {token}"}

        # Simulate an OSQuery scheduled query result
        osquery_payload = {
            "endpoint_id": "osquery-test-node",
            "osquery_version": "5.11.0",
            "data": {
                "processes": [
                    {"name": "osqueryd", "pid": "5555", "path": "/opt/osquery/osqueryd"}
                ]
            }
        }

        # Register the dummy endpoint first so the foreign key constraint is satisfied
        reg_resp = requests.post(f"{BASE_URL}/endpoints/", json={
            "id": str(uuid.uuid4()),
            "hostname": "osquery-test-node",
            "ip_address": "10.0.0.10",
            "os_type": "linux",
            "os_version": "8",
            "agent_version": "1.0"
        }, headers=headers)

        if reg_resp.status_code != 200:
            raise Exception("Failed to register endpoint for OSQuery testing")

        endpoint_id = reg_resp.json()["id"]
        osquery_payload["endpoint_id"] = endpoint_id

        tel_resp = requests.post(f"{BASE_URL}/telemetry/ingest", json=osquery_payload, headers=headers)
        if tel_resp.status_code != 200:
            raise Exception(f"Failed to process OSQuery JSON payload. Status: {tel_resp.status_code}")

        return True, "OSQuery payload parsing and ingestion passed"
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
