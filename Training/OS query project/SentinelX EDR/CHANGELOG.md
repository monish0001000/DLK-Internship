# 📝 Changelog

All notable changes to SentinelX EDR will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - Phase 13.2
### Planned
- **Backend Authentication Hardening**: Validating fine-grained UI permissions at the API dependency level (`RequiresPermission("action")`).
- **Data Model Migration**: Preparing SQLite schema for full PostgreSQL migration.

## [Phase 13.1] - Current
### Added
- **Granular RBAC**: UI components are now wrapped in `<HasPermission>` to enforce strict visibility.
- **Session Expiry UI**: Proactive 60-second warning modal before JWT token expiration.
- **Microservice Health Dashboard**: Advanced metrics tracking DB latency, Scheduler jobs, AI load, WebSockets, and OSQuery agents.
- **Live Activity Feed**: Dashboard feed merging historical audit events with real-time WebSocket pushes.
- **Notification Dropdown**: Top bar component categorizing alerts, system events, and agent status changes.

### Changed
- **Audit Logs**: Completely rebuilt with advanced filtering (User, Action, Request ID, Endpoint), server-side pagination, and precise CSV exporting.
- **Logout Flow**: Implemented backend token revocation (`/auth/logout`) prior to local token destruction.
- **Login Flow**: Enhanced error handling to properly catch and display 403/423 account lockouts due to brute force attempts.

## [Phase 12.0] - AI Investigations
### Added
- **LLM Integration**: Integrated LangChain with OpenRouter/Gemini to perform automated alert triage.
- **Context Generation**: AI models automatically map raw OSQuery telemetry to MITRE ATT&CK techniques and provide human-readable summaries.

## [Phase 11.0] - Telemetry & WebSockets
### Added
- **OSQuery Ingestion**: Telemetry collector pipeline for processing agent status and logs.
- **WebSocket Streaming**: Instant push capabilities for critical alerts to the React frontend.
