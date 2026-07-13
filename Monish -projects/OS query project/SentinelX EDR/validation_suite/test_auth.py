import sys
import requests
from config import BASE_URL, ADMIN_USERNAME, ADMIN_PASSWORD

def run():
    print("Testing Authentication...")
    try:
        # Test 1: Get Token
        response = requests.post(f"{BASE_URL}/auth/token", data={
            "username": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD,
            "grant_type": "password"
        })
        if response.status_code != 200:
            raise Exception(f"Token endpoint returned {response.status_code}")
        
        token = response.json().get("access_token")
        if not token:
            raise Exception("No access token returned")

        # Test 2: Verify Token (Auth Me)
        me_response = requests.get(f"{BASE_URL}/auth/me", headers={
            "Authorization": f"Bearer {token}"
        })
        if me_response.status_code != 200:
            raise Exception(f"/auth/me returned {me_response.status_code}")
        
        user_data = me_response.json()
        if user_data.get("username") != ADMIN_USERNAME:
            raise Exception("Returned user does not match admin")

        return True, "Auth successful"
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
