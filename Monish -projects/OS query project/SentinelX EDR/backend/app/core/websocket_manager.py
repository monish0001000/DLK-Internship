"""
SentinelX EDR - WebSocket Connection Manager
=============================================
Manages WebSocket connections for real-time alert streaming to the SOC dashboard.

Features:
    - Connection tracking with client IDs
    - Subscription-based filtering (severity, endpoint, case)
    - Broadcast to all or targeted clients
    - Automatic cleanup on disconnect
    - Thread-safe connection management

Usage:
    # In startup:
    manager = ConnectionManager()

    # In WebSocket endpoint:
    await manager.connect(websocket, client_id="analyst-1")
    await manager.broadcast({"type": "new_alert", "data": {...}})
"""

import logging
import json
from typing import Dict, Set, Any, Optional
from dataclasses import dataclass, field

from fastapi import WebSocket

logger = logging.getLogger(__name__)


@dataclass
class WebSocketClient:
    """Represents a connected WebSocket client with subscription preferences."""
    websocket: WebSocket
    client_id: str
    subscriptions: Set[str] = field(default_factory=lambda: {"all"})
    connected_at: str = ""


class ConnectionManager:
    """
    Manages all active WebSocket connections and handles message routing.
    
    Subscription types:
        - "all": Receive all alerts (default)
        - "critical", "high", "medium", "low": Filter by severity
        - "endpoint:<id>": Only alerts from specific endpoint
        - "case:<id>": Only alerts related to specific case
    """

    def __init__(self):
        self.active_connections: Dict[str, WebSocketClient] = {}

    async def connect(self, websocket: WebSocket, client_id: str) -> None:
        """
        Accept a new WebSocket connection and register the client.
        
        Args:
            websocket: The FastAPI WebSocket instance.
            client_id: Unique identifier for this client (e.g., session ID).
        """
        await websocket.accept()
        from datetime import datetime, timezone
        client = WebSocketClient(
            websocket=websocket,
            client_id=client_id,
            connected_at=datetime.now(timezone.utc).isoformat(),
        )
        self.active_connections[client_id] = client
        logger.info(f"WebSocket connected: {client_id} | Total: {len(self.active_connections)}")

    async def disconnect(self, client_id: str) -> None:
        """
        Remove a client from active connections.
        
        Args:
            client_id: The client to disconnect.
        """
        self.active_connections.pop(client_id, None)
        logger.info(f"WebSocket disconnected: {client_id} | Total: {len(self.active_connections)}")

    async def update_subscriptions(self, client_id: str, subscriptions: list[str]) -> None:
        """
        Update a client's subscription filters.
        
        Args:
            client_id: The client to update.
            subscriptions: List of subscription filter strings.
        """
        if client_id in self.active_connections:
            self.active_connections[client_id].subscriptions = set(subscriptions)
            logger.debug(f"Updated subscriptions for {client_id}: {subscriptions}")

    async def send_personal(self, client_id: str, message: dict) -> None:
        """
        Send a message to a specific client.
        
        Args:
            client_id: Target client ID.
            message: JSON-serializable message dict.
        """
        client = self.active_connections.get(client_id)
        if client:
            try:
                await client.websocket.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to send to {client_id}: {e}")
                await self.disconnect(client_id)

    async def broadcast(self, message: dict) -> None:
        """
        Broadcast a message to all connected clients that match subscription filters.
        
        For alert messages, checks if the client's subscriptions match the alert's
        severity or endpoint. Clients subscribed to "all" receive everything.
        
        Args:
            message: JSON-serializable message dict. Expected keys for filtering:
                     - type: "new_alert", "alert_update", "endpoint_update"
                     - severity: "critical", "high", "medium", "low"
                     - endpoint_id: UUID of the source endpoint
        """
        disconnected = []
        for client_id, client in self.active_connections.items():
            # Check if client should receive this message based on subscriptions
            if not self._should_receive(client, message):
                continue

            try:
                await client.websocket.send_json(message)
            except Exception as e:
                logger.warning(f"Broadcast failed for {client_id}: {e}")
                disconnected.append(client_id)

        # Clean up failed connections
        for client_id in disconnected:
            await self.disconnect(client_id)

    def _should_receive(self, client: WebSocketClient, message: dict) -> bool:
        """
        Check if a client's subscriptions match the message.
        
        Args:
            client: The WebSocket client to check.
            message: The message being broadcast.
        
        Returns:
            True if the client should receive this message.
        """
        subs = client.subscriptions

        # "all" subscription matches everything
        if "all" in subs:
            return True

        # Check severity filter
        severity = message.get("severity", "")
        if severity and severity in subs:
            return True

        # Check endpoint filter
        endpoint_id = message.get("endpoint_id", "")
        if endpoint_id and f"endpoint:{endpoint_id}" in subs:
            return True

        # Check case filter
        case_id = message.get("case_id", "")
        if case_id and f"case:{case_id}" in subs:
            return True

        return False

    @property
    def connection_count(self) -> int:
        """Number of currently connected clients."""
        return len(self.active_connections)

    def get_connection_info(self) -> list[dict]:
        """
        Get information about all active connections.
        Useful for the Settings/Admin page.
        """
        return [
            {
                "client_id": c.client_id,
                "subscriptions": list(c.subscriptions),
                "connected_at": c.connected_at,
            }
            for c in self.active_connections.values()
        ]


# ── Global Singleton ────────────────────────────────────────────
# Used across the application for broadcasting alerts
ws_manager = ConnectionManager()
