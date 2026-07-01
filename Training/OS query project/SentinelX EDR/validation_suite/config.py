import os

BASE_URL = os.getenv("SENTINELX_BASE_URL", "http://localhost:8000/api/v1")
WS_URL = os.getenv("SENTINELX_WS_URL", "ws://localhost:8000/api/v1")

ADMIN_USERNAME = os.getenv("SENTINELX_ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("SENTINELX_ADMIN_PASSWORD", "admin123")

def get_auth_token():
    """Helper to get a fresh auth token"""
    import requests
    response = requests.post(f"{BASE_URL}/auth/token", data={
        "username": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD,
        "grant_type": "password"
    })
    response.raise_for_status()
    return response.json()["access_token"]
