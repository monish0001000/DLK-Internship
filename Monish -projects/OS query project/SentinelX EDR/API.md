# 🔌 API Reference

SentinelX EDR provides a comprehensive RESTful API via FastAPI, alongside real-time WebSocket endpoints for instantaneous SOC updates.

## 📡 Base URL
```text
http://<server-ip>:8000/api/v1
```

## 🔐 Authentication
The API uses **OAuth2 with Password (and hashing), Bearer with JWT tokens**.
- Obtain a token via `POST /auth/token`
- Include the token in subsequent requests as an `Authorization` header:
  `Authorization: Bearer <your_access_token>`

## 📌 Core Endpoints

### Auth & Users
- `POST /auth/token` - Login and receive JWT access/refresh tokens.
- `POST /auth/refresh` - Refresh access token.
- `POST /auth/logout` - Revoke tokens server-side.
- `GET /auth/me` - Retrieve current user profile and permissions.

### Telemetry & OSQuery
- `POST /osquery/enroll` - Agent enrollment endpoint.
- `POST /osquery/log` - Ingest distributed OSQuery logs (results/status).
- `POST /osquery/config` - Retrieve dynamic OSQuery configuration for an agent.

### Endpoints
- `GET /endpoints` - List all monitored endpoints with status.
- `GET /endpoints/{id}` - Get details of a specific endpoint.
- `POST /endpoints/{id}/isolate` - Trigger network isolation.

### Alerts
- `GET /alerts` - Retrieve paginated security alerts.
- `GET /alerts/{id}` - Get detailed alert info and MITRE mapping.
- `POST /alerts/{id}/investigate` - Trigger an AI-driven investigation on an alert.

### System
- `GET /health` - Detailed microservice health metrics (DB, Scheduler, AI).
- `GET /audit` - Retrieve paginated historical audit logs.

## 🔌 WebSocket Endpoints

Real-time communications are pushed over WebSockets. Authentication is passed via a token query parameter or initial handshake message depending on the client.

- `ws://<server-ip>:8000/api/v1/ws/notifications`
  - **Payload Types:** `new_alert`, `agent_status`, `system`
  - Used by the SOC dashboard to power the Activity Feed and TopBar notifications.
