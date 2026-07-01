import sys
import requests
from config import BASE_URL, get_auth_token

def run():
    print("Testing Audit Logs API...")
    try:
        token = get_auth_token()
        headers = {"Authorization": f"Bearer {token}"}

        # Test: Get Audit logs
        response = requests.get(f"{BASE_URL}/audit/", headers=headers)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch audit logs. Status: {response.status_code}")
        
        data = response.json()
        
        # Depending on pagination it might return a list or a dict with 'items'
        if isinstance(data, dict) and "items" in data:
            logs = data["items"]
        elif isinstance(data, list):
            logs = data
        else:
            raise Exception("Unexpected audit logs format")

        return True, f"Audit logs API passed (retrieved {len(logs)} logs)"
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
