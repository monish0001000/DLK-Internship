# 🔒 Security Model

SentinelX EDR is built with a security-first mindset, ensuring that the platform managing your endpoints is itself resilient against attacks.

## 🛡️ Role-Based Access Control (RBAC)

SentinelX employs strict RBAC at both the **Backend API** layer (FastAPI dependencies) and the **Frontend UI** layer (React `<HasPermission>` components).

### Roles
- **Admin**: Full system access, agent deployment, user management.
- **SOC Manager**: Manage detection rules, investigate alerts, isolate endpoints.
- **Analyst**: View dashboards, hunt threats, read alerts (read-only access to critical functions).

### Enforcement
- **Backend**: API routes use `Depends(RequirePermission("action:isolate"))` to cryptographically enforce authorization via the user's validated JWT token.
- **Frontend**: Buttons and sensitive views are wrapped to prevent unauthorized rendering.

## 🔑 Authentication Lifecycle

SentinelX uses a robust **JSON Web Token (JWT)** architecture:
- **Short-lived Access Tokens**: (e.g., 15-30 minutes) Used for all API requests.
- **Long-lived Refresh Tokens**: (e.g., 7 days) Used to obtain new access tokens silently.
- **Proactive Expiration**: The frontend explicitly monitors token expiry, prompting the user 60 seconds before session termination.
- **Backend Revocation**: Logging out invalidates the session explicitly rather than just clearing client-side storage.
- **Lockouts**: After too many failed attempts, accounts are locked (HTTP 403/423) to prevent brute-force attacks.

## 🕵️‍♂️ Audit Logging

Every significant action within the platform is recorded immutably in the Audit Log:
- **Recorded Fields**: Timestamp, User, Action, Target Object, Status (Success/Failed/Denied), IP Address, Request ID.
- **Coverage**: Login attempts, endpoint isolations, rule modifications, and configuration changes.

## 🚨 Threat Modeling Considerations

- **Agent Spoofing**: OSQuery enrollment is secured via node secret validation.
- **Data Exfiltration**: The platform sanitizes telemetry data and strictly limits access to the Evidence Locker.
- **API Abuse**: Rate limiting is applied to authentication endpoints.
