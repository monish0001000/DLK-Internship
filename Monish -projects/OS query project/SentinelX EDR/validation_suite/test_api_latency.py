import sys
import time
import requests
from config import BASE_URL, get_auth_token

def run():
    print("Testing API Latency...")
    try:
        token = get_auth_token()
        headers = {"Authorization": f"Bearer {token}"}

        endpoints_to_test = [
            "/health/",
            "/auth/me",
            "/endpoints/",
            "/alerts/"
        ]

        max_latency_ms = 3000
        total_latency = 0

        for ep in endpoints_to_test:
            start_time = time.time()
            res = requests.get(f"{BASE_URL}{ep}", headers=headers)
            end_time = time.time()
            
            latency_ms = (end_time - start_time) * 1000
            total_latency += latency_ms
            
            if res.status_code not in (200, 404):
                raise Exception(f"Endpoint {ep} returned {res.status_code}")
                
            if latency_ms > max_latency_ms:
                raise Exception(f"Endpoint {ep} latency too high: {latency_ms:.2f}ms")

        avg_latency = total_latency / len(endpoints_to_test)
        return True, f"API Latency passed (Avg: {avg_latency:.2f}ms)"
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
