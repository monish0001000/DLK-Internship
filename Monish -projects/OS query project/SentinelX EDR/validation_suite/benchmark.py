import sys
import time
import uuid
import requests
from config import BASE_URL, get_auth_token

def run():
    print("Running Telemetry Benchmark...")
    try:
        token = get_auth_token()
        headers = {"Authorization": f"Bearer {token}"}

        # Register endpoint
        reg_resp = requests.post(f"{BASE_URL}/endpoints/", json={
            "id": str(uuid.uuid4()),
            "hostname": "benchmark-node",
            "ip_address": "10.0.0.99",
            "os_type": "windows",
            "os_version": "2022",
            "agent_version": "1.0"
        }, headers=headers)
        
        if reg_resp.status_code != 200:
            raise Exception("Failed to register benchmark endpoint")

        endpoint_id = reg_resp.json()["id"]
        
        telemetry_payload = {
            "endpoint_id": endpoint_id,
            "osquery_version": "5.10.0",
            "data": {
                "processes": [{"name": "bench.exe", "pid": "1000", "path": "C:\\bench.exe"}]
            }
        }

        iterations = 10
        start_time = time.time()
        for _ in range(iterations):
            resp = requests.post(f"{BASE_URL}/telemetry/ingest", json=telemetry_payload, headers=headers)
            if resp.status_code != 200:
                raise Exception(f"Benchmark failed on iteration. Status: {resp.status_code}")
                
        end_time = time.time()
        duration = end_time - start_time
        ops = iterations / duration

        return True, f"Benchmark passed ({iterations} payloads in {duration:.2f}s, {ops:.2f} req/sec)"
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
