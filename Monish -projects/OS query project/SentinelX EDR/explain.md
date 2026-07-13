# SentinelX EDR: Deep Dive & Technical Explanation

## 1. Introduction

**SentinelX EDR** is an advanced, AI-powered Endpoint Detection and Response (EDR) platform built to address the challenges of modern Security Operations Centers (SOCs). As adversaries become more sophisticated, traditional SIEM (Security Information and Event Management) solutions struggle with high latency and alert fatigue. SentinelX bridges the gap by providing instantaneous visibility into endpoint activities, automating threat detection, and leveraging Artificial Intelligence to provide immediate, actionable context to security analysts.

By treating the operating system as a high-performance relational database (via OSQuery), SentinelX collects rich telemetry, runs it through a robust detection engine supporting industry-standard Sigma rules, and streams alerts directly to a modern React dashboard via WebSockets.

---

## 2. Architectural Overview

SentinelX follows an event-driven, decoupled microservices architecture designed for speed and extensibility.

### The Triad of SentinelX:
1. **The Agent Layer (OSQuery):** Instead of writing a custom, potentially unstable kernel driver, SentinelX leverages OSQuery. OSQuery allows the platform to query process trees, network sockets, file modifications, and registry keys using standard SQL. This ensures cross-platform compatibility and minimal performance impact on the host.
2. **The Backend Engine (FastAPI):** Written in Python using FastAPI, the backend handles high-throughput asynchronous requests. It acts as the central brain—processing incoming telemetry, matching it against threat signatures, interacting with external AI APIs, and persisting state to the database via SQLAlchemy.
3. **The Presentation Layer (React + Vite):** A responsive, dark-mode-first SPA (Single Page Application) that gives SOC analysts a real-time command center to hunt threats, view dashboards, and isolate compromised machines.

---

## 3. Core Subsystems

### 3.1 Telemetry Ingestion Pipeline
When an endpoint checks in, it sends a batch of telemetry data (e.g., process creations, network connections). 
- The data hits the `POST /telemetry/ingest` endpoint.
- It is immediately written to the database to ensure no data loss (acting as a forensic evidence locker).
- The payload is concurrently passed to the **Background Scheduler**, allowing the HTTP request to close quickly while the heavy lifting (threat detection) happens asynchronously.

### 3.2 Detection Engine & Sigma Rules
The heart of SentinelX is its detection engine. It evaluates incoming telemetry against two sets of logic:
- **Heuristics:** Hardcoded logic to detect generic anomalies (e.g., `cmd.exe` spawning PowerShell with hidden window arguments).
- **Sigma Rules Engine:** Sigma is the open-source standard for SIEM signatures. SentinelX dynamically parses Sigma YAML files, translating their logic into Python evaluation rules. If a telemetry event matches a Sigma condition, a High or Critical alert is instantly generated.

### 3.3 AI Investigation Engine
To combat alert fatigue, SentinelX integrates with Large Language Models (via OpenRouter/Gemini). 
When a complex alert is generated (for example, a suspicious PowerShell script execution), the SOC analyst can click "Investigate with AI."
- The backend aggregates the alert context, the endpoint's recent telemetry, and the triggered rule.
- A highly engineered prompt is sent to the LLM, asking it to act as a Tier 3 Incident Responder.
- The AI returns a human-readable summary, an assessment of malicious intent, and recommended remediation steps.

### 3.4 Real-Time Communications (WebSockets)
SOC analysts cannot afford to refresh a webpage to see if an attack is happening. SentinelX utilizes FastAPI's WebSocket capabilities to maintain persistent connections with the React frontend.
- When the Detection Engine flags an event, it triggers the `ConnectionManager`.
- The manager broadcasts the alert payload instantly to all subscribed analyst dashboards.
- This creates a true "live" command center experience.

### 3.5 Response Simulator
SentinelX includes an Active Response module capable of taking decisive action against threats. Currently implemented as a simulator (for safety in testing), it supports:
- **Isolating Endpoints:** Dropping all network traffic except to the EDR management server.
- **Killing Processes:** Terminating malicious PIDs.
- **Quarantining Files:** Encrypting and moving malware to a secure locker.
Every action is rigorously logged in the Audit Trail.

---

## 4. Security & Role-Based Access Control (RBAC)

Security software must be inherently secure. SentinelX enforces strict access controls:
- **JWT Architecture:** Uses short-lived Access Tokens and long-lived Refresh Tokens. 
- **Endpoint Security:** Every API route is protected by `Depends(RequirePermission("specific_action"))`. An analyst can view alerts, but only a SOC Manager or Admin can trigger an endpoint isolation.
- **Audit Logging:** Every configuration change, login attempt, or response action is immutably logged to the `audit_logs` table. This ensures compliance and non-repudiation.

---

## 5. The Validation Suite

To guarantee system stability, SentinelX includes a bespoke **Validation Suite** (`validation_suite/`). 
This is an integration testing framework that sequentially tests every API boundary and internal service without relying on external mocks.
It runs a 15-step validation encompassing:
1. Authentication & Token generation.
2. Database Schema health.
3. Endpoint Registration workflows.
4. Raw OSQuery JSON ingestion.
5. Detection Engine execution.
6. WebSocket connectivity timeouts.
7. End-to-end API latency benchmarking.

Achieving a **15/15 Pass Rate** on this suite proves that the entire microservice architecture is correctly aligned and production-ready.

---

## 6. Conclusion and Future Roadmap

SentinelX EDR represents a modern approach to endpoint security—prioritizing speed, open standards (OSQuery/Sigma), and AI automation. 

**Next Steps on the Roadmap:**
- Migrating the primary data store from SQLite to PostgreSQL for horizontal scalability.
- Integrating external Threat Intelligence feeds (MISP, OTX) for automated IOC enrichment.
- Expanding the AI engine to proactively hunt for threats across the entire endpoint fleet based on natural language queries from analysts.
