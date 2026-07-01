import sys
import requests
import uuid
from config import BASE_URL, get_auth_token

def run():
    print("Testing Endpoint Registration...")
    try:
        token = get_auth_token()
        headers = {"Authorization": f"Bearer {token}"}

        # Test: Register endpoint
        endpoint_data = {
            "id": str(uuid.uuid4()),
            "hostname": "test-desktop-01",
            "ip_address": "192.168.1.100",
            "os_type": "windows",
            "os_version": "10.0.22621",
            "agent_version": "1.0.0"
        }
        
        response = requests.post(f"{BASE_URL}/endpoints/", json=endpoint_data, headers=headers)
        if response.status_code != 200:
            raise Exception(f"Failed to register endpoint. Status: {response.status_code}")
        
        endpoint = response.json()
        if not endpoint.get("id"):
            raise Exception("Endpoint ID not returned")
            
        endpoint_id = endpoint["id"]

        # Test: Check-in
        checkin_response = requests.post(f"{BASE_URL}/endpoints/heartbeat", json={"endpoint_id": endpoint_id, "timestamp": None}, headers=headers)
        if checkin_response.status_code != 200:
            raise Exception(f"Failed to check-in endpoint. Status: {checkin_response.status_code}")

        return True, f"Endpoint registration and checkin passed (ID: {endpoint_id})"
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
