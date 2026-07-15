Backend/Frontend integration plan (execution order)

1) app.py (backend)
   - Add LIVE_CAPTURE flag + robust interface selection helper.
   - Implement a background live-sniff thread using sniffer.start_sniffer (LiveCapture fallback) to continuously produce feature DataFrames.
   - Extend RiskEngine to include:
     * Honey-Twin decoy state for IP 192.168.1.250
     * Critical breach override: if honeypot IP appears in live features OR emulator targets it, force risk_score=100 for that event.
     * Threat tier tag "DECEPTION DECOY COMPROMISED" embedded into both:
         - /api/live_traffic response
         - each matching /api/threat_logs event
     * plyer desktop notification throttled (e.g., once per N seconds) for the breach.

   - Add /api/live_traffic payload fields:
       * last_breach (boolean)
       * critical_tier_tag (string|null)
       * last_breach_src_ip

2) templates/index.html (frontend)
   - Add a new widget card: "CYBER DECEPTION SHIELD CORE".
   - Default state: "CORE SECURE - TRAP ARMED" with neon-cyan glowing core indicator.
   - Every 3 seconds (inside existing refresh interval):
       * If API reports critical_tier_tag === "DECEPTION DECOY COMPROMISED" then blink widget violently in neon-red and show:
         "DECEPTION DECOY BREACHED — INVESTIGATION UNLOCKED".
       * Otherwise return to secure state.

3) Verification
   - Ensure JS keeps existing auto-scroll/log update behavior.
   - Smoke test: Flask run, open dashboard, confirm widget changes upon breach simulation.

