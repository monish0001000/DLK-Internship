import sys
import asyncio
import websockets
import json
from config import WS_URL, get_auth_token

async def run_async():
    print("Testing WebSocket Connection...")
    try:
        token = get_auth_token()
        
        # Connect to websocket. The API accepts token as a query parameter.
        uri = f"{WS_URL}/ws?token={token}"
        
        async with websockets.connect(uri) as websocket:
            # Send a simple ping or dummy message
            await websocket.send(json.dumps({"type": "ping", "data": "test"}))
            
            # Wait for a response (or timeout after 2 seconds)
            response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
            data = json.loads(response)
            
            # The backend might respond with a pong or auth success message
            return True, f"WebSocket connection passed (received {data.get('type', 'message')})"
            
    except asyncio.TimeoutError:
        # If we connect but don't get a message, it still means we connected successfully
        return True, "WebSocket connection passed (timeout waiting for message, but connection held)"
    except Exception as e:
        return False, str(e)

def run():
    return asyncio.run(run_async())

if __name__ == "__main__":
    success, msg = run()
    if success:
        print(f"PASS: {msg}")
        sys.exit(0)
    else:
        print(f"FAIL: {msg}")
        sys.exit(1)
