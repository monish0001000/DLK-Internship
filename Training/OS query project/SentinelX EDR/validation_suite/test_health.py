import sys
import requests
from config import BASE_URL

def run():
    print("Testing Health API...")
    try:
        response = requests.get(f"{BASE_URL}/health/")
        if response.status_code != 200:
            raise Exception(f"Health endpoint returned {response.status_code}")
        
        data = response.json()
        if data.get("status") != "healthy":
            raise Exception("System is not healthy")

        return True, "Health check passed"
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
