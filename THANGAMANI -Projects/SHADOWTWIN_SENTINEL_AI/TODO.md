# ShadowTwin Sentinel AI - Upgrade Plan (Honey-Twin Deception + Live Switch + Desktop Alerts)

## Step 1 — Repo understanding
- [x] Read current `app.py`
- [x] Read current `templates/index.html`
- [x] Read `sniffer.py`
- [ ] Search for existing alert/anomaly modules

## Step 2 — Implement BACKEND REGULATORY ENGINE (`app.py`)
- [ ] Add `LIVE_CAPTURE` flag and dynamic live interface switching via PyShark
- [ ] Maintain background emulation thread (~5s)
- [ ] Add Honey-Twin asset state for fake DB server at `192.168.1.250`
- [ ] Detect traffic targeted to honeypot IP; on breach force `risk_score=100` and tag `DECEPTION DECOY COMPROMISED`
- [ ] Expose the critical tag in `/api/live_traffic` and `/api/threat_logs`
- [ ] Integrate `plyer` desktop notification on breach

## Step 3 — Premium FRONTEND widget (`templates/index.html`)
- [ ] Add widget titled `CYBER DECEPTION SHIELD CORE`
- [ ] Show "CORE SECURE - TRAP ARMED" when safe
- [ ] On critical tag event blink violently in neon-crimson with message "DECEPTION DECOY BREACHED — INVESTIGATION UNLOCKED"
- [ ] Keep telemetry refresh every 3 seconds and auto-scroll threat logs

## Step 4 — Dependencies & run verification
- [x] Add `plyer` to `requirements.txt`
- [ ] Run `pip install -r requirements.txt`
- [ ] Smoke test Flask + UI update loop

