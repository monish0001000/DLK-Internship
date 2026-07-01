# SentinelX EDR Validation Suite

The Validation Suite is a collection of localized, non-destructive test scripts designed to ensure SentinelX EDR's subsystems are running correctly. This is **not** a penetration testing suite. It operates entirely within an authorized lab environment, using benign test data, to ensure the platform behaves exactly as expected.

## 🚀 Purpose

During interviews or live demonstrations, knowing that every component of your architecture works correctly is critical. This suite gives you a professional, automated way to prove your system is fully operational.

It verifies:
- API Connectivity and Latency
- Authentication (JWT issuance and validation)
- Endpoint Registration and Telemetry Ingestion
- Real-time WebSocket Notifications
- Detection Engine / Sigma Rule evaluation
- Audit Logging and Database health
- Threat Hunting / AI APIs

## 📦 Prerequisites

Do not mix these requirements with your primary backend or frontend packages. Use a separate Python environment or simply install them locally.

```bash
cd validation_suite
pip install -r requirements.txt
```

## 🛠 Usage

Ensure the SentinelX Backend is running locally on `http://localhost:8000` (the default). 

### Run the entire suite
To test every subsystem sequentially and generate an HTML/JSON report:

```bash
python run_all.py
```

### Run individual validators
If you're debugging a specific component, run its validator directly:

```bash
python test_auth.py
python test_websockets.py
```

## 📊 Reports

After running `run_all.py`, check the `reports/` directory for the latest output:
- `latest_report.html` - A styled dashboard report showing the system's overall score.
- `latest_report.json` - Raw metrics for external CI/CD integrations.
