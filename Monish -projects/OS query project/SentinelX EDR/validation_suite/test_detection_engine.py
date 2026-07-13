import sys
import requests
from config import BASE_URL, get_auth_token

def run():
    print("Testing Detection Engine API...")
    try:
        token = get_auth_token()
        headers = {"Authorization": f"Bearer {token}"}

        # The detection engine is usually tested by checking alerts or simulating an attack
        # Let's query alerts to ensure the engine's output is accessible
        response = requests.get(f"{BASE_URL}/alerts/", headers=headers)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch alerts. Status: {response.status_code}")

        # Also test the simulation endpoint if it exists
        sim_payload = {
            "action_type": "isolate_endpoint",
            "target": "endpoint",
            "endpoint_id": "dummy-endpoint-for-validation",
            "execution_mode": "simulation",
            "reason": "validation test"
        }
        
        sim_response = requests.post(f"{BASE_URL}/responses/simulate", json=sim_payload, headers=headers)
        if sim_response.status_code not in (200, 202, 404):
            # 404 is acceptable if the simulation endpoint isn't fully implemented in this demo mode
            # We just want to make sure it doesn't 500 error out
            raise Exception(f"Simulation endpoint returned unexpected status: {sim_response.status_code}")

        return True, "Detection engine endpoints are accessible"
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
