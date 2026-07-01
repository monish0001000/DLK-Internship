"""
SentinelX EDR - WebSocket API
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Any

from app.core.websocket_manager import ws_manager as manager

router = APIRouter()

import uuid

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> Any:
    # Accept without specific endpoint_id for dashboard global view
    client_id = str(uuid.uuid4())
    await manager.connect(websocket, client_id=client_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming messages (e.g., ping/pong or filter updates) if needed
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        await manager.disconnect(client_id)
