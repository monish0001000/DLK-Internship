import os
import json
import time
import threading
import queue
import sqlite3
from datetime import datetime
from typing import Dict, Any, Optional, List

import joblib
import numpy as np
import pandas as pd

from flask import Flask, jsonify, render_template, request

# PyShark sniffer module (optional; emulator can run even if live sniffing isn't configured)
import sniffer

# Optional: psutil used only for interface detection fallbacks
try:
    import psutil  # type: ignore
except Exception:
    psutil = None


# Desktop notifications (Windows)
try:
    from plyer import notification
except Exception:
    notification = None



BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(BASE_DIR, "artifacts", "shadowtwin.sqlite")
ARTIFACTS_DIR = os.path.join(BASE_DIR, "artifacts")
MODEL_PATH = os.path.join(ARTIFACTS_DIR, "isolation_forest.joblib")
SCALER_PATH = os.path.join(ARTIFACTS_DIR, "scaler.joblib")
FEATURE_IMPORTANCE_PATH = os.path.join(ARTIFACTS_DIR, "feature_importance.joblib")



FEATURES = [
    "packet_count",
    "avg_packet_size",
    "tcp_pct",
    "udp_pct",
    "icmp_pct",
    "syn_rate",
    "ack_rate",
    "rst_rate",
    "dst_ip_diversity",
    "unique_ports_targeted",
    "flow_duration",
    "inter_arrival_time",
]


app = Flask(__name__)


def ensure_db() -> None:
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL,
            attack_phase TEXT NOT NULL,
            src_ip TEXT NOT NULL,
            risk_score REAL NOT NULL,
            trust_score REAL NOT NULL,
            ai_threat_story TEXT NOT NULL,
            features_json TEXT
        )
        """
    )
    conn.commit()
    conn.close()


ensure_db()


class RiskEngine:
    # Honey-Twin decoy asset (fake vulnerable DB server)
    HONEY_TWIN_IP = "192.168.1.250"
    CRITICAL_TIER_TAG = "DECEPTION DECOY COMPROMISED"


    def __init__(self):
        # LIVE_CAPTURE flag controls live sniffing; safe fallback to emulator only.
        self.LIVE_CAPTURE = bool(int(os.environ.get("SHADOWTWIN_LIVE_CAPTURE", "1")))

        # Honey-Twin decoy state
        self.honey_twin_state: Dict[str, Any] = {
            "ip": self.HONEY_TWIN_IP,
            "status": "ACTIVE",
            "integrity": 100,
        }

        # Breach/throttle state for desktop notifications
        self.last_breach_ts: float = 0.0
        self.breach_cooldown_sec: float = 20.0


        self.model = joblib.load(MODEL_PATH)
        self.scaler = joblib.load(SCALER_PATH)
        self.feature_importance = joblib.load(FEATURE_IMPORTANCE_PATH)

        # Trust state per src_ip
        self.trust: Dict[str, float] = {}
        self.anomaly_persistence: Dict[str, int] = {}

        # Latest window metrics per src_ip
        self.latest: Dict[str, Dict[str, Any]] = {}

        # Threat log (for terminal replay)
        self.threat_logs: List[Dict[str, Any]] = []

        # Overall drift tracking
        self.risk_history: List[float] = []
        self.traffic_volume_history: List[float] = []

        self.lock = threading.Lock()

        # Latest critical tier event (for UI)
        self.latest_critical_event: Dict[str, Any] = {
            "tier_tag": None,
            "last_breach": False,
            "src_ip": None,
            "ts": None,
        }


    def _risk_from_anomaly_score(self, anomaly_magnitude: float) -> float:
        # decision_function higher => more normal
        # use magnitude => higher => more anomalous
        x = float(anomaly_magnitude)
        risk = 100.0 * (1.0 / (1.0 + np.exp(-x)))
        return float(np.clip(risk, 0, 100))

    def _mood_from_avg_risk(self, avg_risk: float) -> str:
        if avg_risk < 35:
            return "CALM"
        if avg_risk < 70:
            return "RECONNAISSANCE"
        return "UNDER ATTACK"

    def _compute_ai_threat_story(self, row: Dict[str, Any], risk: float, phase: str) -> str:
        # Cyberpunk-flavored incident narrative with feature drivers
        syn_rate = float(row.get("syn_rate", 0.0) or 0.0)
        unique_ports = float(row.get("unique_ports_targeted", 0.0) or 0.0)
        dst_div = float(row.get("dst_ip_diversity", 0.0) or 0.0)
        udp_pct = float(row.get("udp_pct", 0.0) or 0.0)
        tcp_pct = float(row.get("tcp_pct", 0.0) or 0.0)

        if phase == "port_scan":
            return f"🚨 Port-scan spike — SYN rate {syn_rate:.1f}/s and {int(unique_ports)} unique ports targeted. Risk locks at {risk:.0f}%."
        if phase == "dns_flood":
            return f"⚠ DNS-flood signature — UDP dominance {udp_pct:.0f}% with bursty packet cadence (inter-arrival {row.get('inter_arrival_time', 0):.3f}s). Risk {risk:.0f}%."
        if phase == "data_exfil":
            return f"🚨 Data-exfil behavior — high packet_count ({int(row.get('packet_count', 0))}) with anomalous flow timing; destination diversity {int(dst_div)}. Risk {risk:.0f}%."

        # baseline / unknown
        parts = []
        if syn_rate > 0:
            parts.append(f"SYN {syn_rate:.1f}/s")
        parts.append(f"TCP {tcp_pct:.0f}% / UDP {udp_pct:.0f}%")
        if unique_ports > 0:
            parts.append(f"ports {int(unique_ports)}")
        if dst_div > 0:
            parts.append(f"dst-div {int(dst_div)}")

        return f"AI drift detected ({phase}) — {', '.join(parts)}. Risk {risk:.0f}%."

    def _maybe_trigger_honey_twin_breach(self, src_ip: str, features: Dict[str, Any]) -> None:
        """If honeypot/decoy IP is targeted, hard override to CRITICAL tier."""
        if str(src_ip) != self.HONEY_TWIN_IP:
            return

        now = time.time()
        with self.lock:
            # integrity drop & critical event
            self.honey_twin_state["integrity"] = 0
            self.honey_twin_state["status"] = "COMPROMISED"

            self.latest_critical_event = {
                "tier_tag": self.CRITICAL_TIER_TAG,
                "last_breach": True,
                "src_ip": src_ip,
                "ts": datetime.utcnow().isoformat() + "Z",
                "features": features,
            }

            # throttled notification
            should_notify = (now - self.last_breach_ts) >= self.breach_cooldown_sec
            if should_notify:
                self.last_breach_ts = now

        if notification is not None and (now - self.last_breach_ts) <= self.breach_cooldown_sec + 0.01:
            try:
                story = "DECEPTION DECOY COMPROMISED — Hone-Twin breach confirmed; isolation + containment recommended."
                notification.notify(
                    title="ShadowTwin Sentinel AI — Threat Block",
                    message=f"{self.CRITICAL_TIER_TAG}\nSource: {src_ip}\n{story}",
                    timeout=6,
                    app_name="ShadowTwin Sentinel AI",
                )
            except Exception:
                pass

    def evaluate_df(self, df: pd.DataFrame, attack_phase: str = "baseline") -> None:

        if df is None or df.empty:
            return

        with self.lock:
            # compute overall traffic volume approx (sum packet_count)
            try:
                volume = float(df["packet_count"].sum())
            except Exception:
                volume = 0.0

            # per-row scoring
            for _, r in df.iterrows():
                row = r.to_dict()
                src_ip = str(row.get("src_ip", "unknown"))

                X = pd.DataFrame([{k: row.get(k, 0.0) for k in FEATURES}]).astype(float)
                Xs = self.scaler.transform(X)

                decision = float(self.model.decision_function(Xs)[0])
                anomaly_magnitude = -decision
                risk = self._risk_from_anomaly_score(anomaly_magnitude)

                prev_trust = self.trust.get(src_ip, 100.0)
                persist = self.anomaly_persistence.get(src_ip, 0)

                # trust DNA drops faster as risk stays high
                if risk > 60:
                    persist += 1
                    drop = min(30.0, (risk - 60.0) / 1.7 + persist * 3.0)
                else:
                    persist = max(0, persist - 1)
                    drop = 0.0

                new_trust = float(np.clip(prev_trust - drop, 0.0, 100.0))
                self.trust[src_ip] = new_trust
                self.anomaly_persistence[src_ip] = persist

                ai_story = ""

                # Honeypot/decoy targeting hard override.
                # If any packet window includes the decoy IP as the src_ip in extracted features,
                # force critical risk + tier tag.
                critical_override = str(src_ip) == self.HONEY_TWIN_IP
                if critical_override:
                    risk = 100.0
                    ai_story = "🚨 DECEPTION DECOY COMPROMISED — investigation unlocked."
                    self._maybe_trigger_honey_twin_breach(src_ip, row)

                    alert = {
                        "ts": datetime.utcnow().isoformat() + "Z",
                        "attack_phase": "honey_twin_breach",
                        "src_ip": src_ip,
                        "risk_score": float(risk),
                        "trust_score": 0.0,
                        "ai_threat_story": ai_story,
                        "features": {k: float(row.get(k, 0.0)) for k in FEATURES},
                        "tier_tag": self.CRITICAL_TIER_TAG,
                    }

                    self.threat_logs.append(alert)
                    self.threat_logs = self.threat_logs[-300:]

                    conn = sqlite3.connect(DB_PATH)
                    cur = conn.cursor()
                    cur.execute(
                        """
                        INSERT INTO alerts (ts, attack_phase, src_ip, risk_score, trust_score, ai_threat_story, features_json)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            alert["ts"],
                            alert["attack_phase"],
                            alert["src_ip"],
                            alert["risk_score"],
                            alert["trust_score"],
                            alert["ai_threat_story"],
                            json.dumps(alert["features"]),
                        ),
                    )
                    conn.commit()
                    conn.close()

                # Normal pipeline
                if (not critical_override) and risk > 70:
                    ai_story = self._compute_ai_threat_story(row, risk, attack_phase)

                    alert = {

                        "ts": datetime.utcnow().isoformat() + "Z",
                        "attack_phase": attack_phase,
                        "src_ip": src_ip,
                        "risk_score": float(risk),
                        "trust_score": float(new_trust),
                        "ai_threat_story": ai_story,
                        "features": {k: float(row.get(k, 0.0)) for k in FEATURES},
                    }

                    self.threat_logs.append(alert)
                    self.threat_logs = self.threat_logs[-300:]

                    # persist in sqlite (lightweight)
                    conn = sqlite3.connect(DB_PATH)
                    cur = conn.cursor()
                    cur.execute(
                        """
                        INSERT INTO alerts (ts, attack_phase, src_ip, risk_score, trust_score, ai_threat_story, features_json)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            alert["ts"],
                            alert["attack_phase"],
                            alert["src_ip"],
                            alert["risk_score"],
                            alert["trust_score"],
                            alert["ai_threat_story"],
                            json.dumps(alert["features"]),
                        ),
                    )
                    conn.commit()
                    conn.close()

                # update latest snapshot
                self.latest[src_ip] = {
                    "risk_score": float(risk),
                    "trust_score": float(new_trust),
                    "ai_threat_story": ai_story,
                    "attack_phase": attack_phase,
                    "features": {k: float(row.get(k, 0.0)) for k in FEATURES},
                    "window_start_ts": row.get("window_start_ts"),
                    "window_end_ts": row.get("window_end_ts"),
                }

            # track drift histories (avg risk across devices in this snapshot)
            avg_risk_now = float(np.mean([v["risk_score"] for v in self.latest.values()])) if self.latest else 0.0
            self.risk_history.append(avg_risk_now)
            self.traffic_volume_history.append(volume)
            self.risk_history = self.risk_history[-120:]
            self.traffic_volume_history = self.traffic_volume_history[-120:]

    def status(self) -> Dict[str, Any]:
        with self.lock:
            if not self.latest:
                avg_risk = 0.0
                mood = "CALM"
            else:
                avg_risk = float(np.mean([v["risk_score"] for v in self.latest.values()]))
                mood = self._mood_from_avg_risk(avg_risk)

            top = sorted(self.latest.items(), key=lambda kv: kv[1]["risk_score"], reverse=True)[:8]
            devices = [
                {
                    "src_ip": ip,
                    "risk_score": v["risk_score"],
                    "trust_score": v["trust_score"],
                    "attack_phase": v.get("attack_phase", "baseline"),
                    "ai_threat_story": v.get("ai_threat_story", ""),
                }
                for ip, v in top
            ]

            return {
                "mood": mood,
                "avg_risk": avg_risk,
                "top_devices": devices,
            }

    def get_live_traffic_snapshot(self) -> Dict[str, Any]:
        # for line chart + device matrix
        with self.lock:
            if self.risk_history:
                last_risk = float(self.risk_history[-1])
            else:
                last_risk = 0.0

            if self.traffic_volume_history:
                last_vol = float(self.traffic_volume_history[-1])
            else:
                last_vol = 0.0

            return {
                "risk_drift": self.risk_history[-60:],
                "traffic_volume": self.traffic_volume_history[-60:],
                "last_risk": last_risk,
                "last_volume": last_vol,
                "critical_tier_tag": self.latest_critical_event.get("tier_tag"),
                "last_breach": bool(self.latest_critical_event.get("last_breach")),
                "breach_src_ip": self.latest_critical_event.get("src_ip"),
                "breach_ts": self.latest_critical_event.get("ts"),
            }


    def get_threat_logs(self, limit: int = 80) -> List[Dict[str, Any]]:
        with self.lock:
            # Only the most recent N already stored; ensure critical tier tagging is present.
            logs = list(self.threat_logs[-limit:])
            # guarantee tier_tag field exists for UI
            for l in logs:
                if "tier_tag" not in l:
                    l["tier_tag"] = None
            return logs



engine = RiskEngine()


def _emulate_baseline(num_devices: int = 3) -> pd.DataFrame:
    ts_start = time.time()
    ts_end = ts_start + 5

    rows = []
    for i in range(num_devices):
        src_ip = f"192.168.1.{10 + i}"
        packet_count = np.random.randint(20, 120)
        avg_packet_size = np.random.randint(80, 250)

        tcp_pct = float(np.random.uniform(70, 90))
        udp_pct = float(np.random.uniform(8, 25))
        icmp_pct = float(np.random.uniform(0, 5))

        syn_rate = float(np.random.uniform(0.2, 5.0))
        ack_rate = float(np.random.uniform(5.0, 30.0))
        rst_rate = float(np.random.uniform(0.0, 0.8))

        dst_div = float(np.random.randint(1, 6))
        unique_ports = float(np.random.randint(1, 8))

        rows.append(
            {
                "src_ip": src_ip,
                "packet_count": float(packet_count),
                "avg_packet_size": float(avg_packet_size),
                "tcp_pct": tcp_pct,
                "udp_pct": udp_pct,
                "icmp_pct": icmp_pct,
                "syn_rate": syn_rate,
                "ack_rate": ack_rate,
                "rst_rate": rst_rate,
                "dst_ip_diversity": dst_div,
                "unique_ports_targeted": unique_ports,
                "flow_duration": 5.0,
                "inter_arrival_time": float(np.random.uniform(0.01, 0.08)),
                "window_start_ts": ts_start,
                "window_end_ts": ts_end,
            }
        )

    return pd.DataFrame(rows)


def _emulate_port_scan(num_devices: int = 3) -> pd.DataFrame:
    ts_start = time.time()
    ts_end = ts_start + 5
    rows = []
    for i in range(num_devices):
        src_ip = f"10.0.0.{40 + i}"
        packet_count = float(np.random.randint(220, 520))
        avg_packet_size = float(np.random.randint(60, 140))

        tcp_pct = 98.0
        udp_pct = 1.0
        icmp_pct = 1.0

        syn_rate = float(np.random.uniform(55, 140))
        ack_rate = float(np.random.uniform(5, 40))
        rst_rate = float(np.random.uniform(2, 10))

        dst_div = float(np.random.uniform(5, 14))
        unique_ports = float(np.random.uniform(20, 80))

        rows.append(
            {
                "src_ip": src_ip,
                "packet_count": packet_count,
                "avg_packet_size": avg_packet_size,
                "tcp_pct": tcp_pct,
                "udp_pct": udp_pct,
                "icmp_pct": icmp_pct,
                "syn_rate": syn_rate,
                "ack_rate": ack_rate,
                "rst_rate": rst_rate,
                "dst_ip_diversity": dst_div,
                "unique_ports_targeted": unique_ports,
                "flow_duration": 5.0,
                "inter_arrival_time": float(np.random.uniform(0.002, 0.02)),
                "window_start_ts": ts_start,
                "window_end_ts": ts_end,
            }
        )

    return pd.DataFrame(rows)


def _emulate_dns_flood(num_devices: int = 2) -> pd.DataFrame:
    ts_start = time.time()
    ts_end = ts_start + 5
    rows = []
    for i in range(num_devices):
        src_ip = f"172.16.0.{70 + i}"
        packet_count = float(np.random.randint(260, 760))
        avg_packet_size = float(np.random.randint(90, 190))

        tcp_pct = float(np.random.uniform(5, 20))
        udp_pct = float(np.random.uniform(70, 95))
        icmp_pct = float(np.random.uniform(0, 3))

        syn_rate = float(np.random.uniform(0.0, 2.0))
        ack_rate = float(np.random.uniform(0.5, 6.0))
        rst_rate = float(np.random.uniform(0.0, 1.0))

        dst_div = float(np.random.uniform(2, 10))
        unique_ports = float(np.random.uniform(1, 12))

        rows.append(
            {
                "src_ip": src_ip,
                "packet_count": packet_count,
                "avg_packet_size": avg_packet_size,
                "tcp_pct": tcp_pct,
                "udp_pct": udp_pct,
                "icmp_pct": icmp_pct,
                "syn_rate": syn_rate,
                "ack_rate": ack_rate,
                "rst_rate": rst_rate,
                "dst_ip_diversity": dst_div,
                "unique_ports_targeted": unique_ports,
                "flow_duration": 5.0,
                "inter_arrival_time": float(np.random.uniform(0.001, 0.01)),
                "window_start_ts": ts_start,
                "window_end_ts": ts_end,
            }
        )

    return pd.DataFrame(rows)


def _emulate_data_exfil(num_devices: int = 2) -> pd.DataFrame:
    ts_start = time.time()
    ts_end = ts_start + 5
    rows = []
    for i in range(num_devices):
        src_ip = f"203.0.113.{9 + i}"
        packet_count = float(np.random.randint(320, 980))
        avg_packet_size = float(np.random.randint(120, 520))

        tcp_pct = float(np.random.uniform(60, 95))
        udp_pct = float(np.random.uniform(0, 25))
        icmp_pct = float(np.random.uniform(0, 2))

        syn_rate = float(np.random.uniform(0.5, 20.0))
        ack_rate = float(np.random.uniform(20.0, 120.0))
        rst_rate = float(np.random.uniform(0.0, 5.0))

        dst_div = float(np.random.uniform(6, 22))
        unique_ports = float(np.random.uniform(10, 60))

        rows.append(
            {
                "src_ip": src_ip,
                "packet_count": packet_count,
                "avg_packet_size": avg_packet_size,
                "tcp_pct": tcp_pct,
                "udp_pct": udp_pct,
                "icmp_pct": icmp_pct,
                "syn_rate": syn_rate,
                "ack_rate": ack_rate,
                "rst_rate": rst_rate,
                "dst_ip_diversity": dst_div,
                "unique_ports_targeted": unique_ports,
                "flow_duration": 5.0,
                "inter_arrival_time": float(np.random.uniform(0.005, 0.06)),
                "window_start_ts": ts_start,
                "window_end_ts": ts_end,
            }
        )

    return pd.DataFrame(rows)


def _emulation_cycle(stop_event: threading.Event, window_seconds: int = 5) -> None:
    """Continuous Real-time Network Attack Emulation engine.

    Alternates baseline and attack phases every `window_seconds`.
    """

    phases = [
        ("baseline", _emulate_baseline),
        ("port_scan", _emulate_port_scan),
        ("dns_flood", _emulate_dns_flood),
        ("data_exfil", _emulate_data_exfil),
    ]

    idx = 0
    while not stop_event.is_set():
        phase_name, fn = phases[idx % len(phases)]
        idx += 1

        df = fn()
        engine.evaluate_df(df, attack_phase=phase_name)

        # Pace to approximately match sniffer windows
        stop_event.wait(window_seconds)


# ---------------- Flask endpoints ----------------


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/status")
def api_status():
    return jsonify(engine.status())


@app.route("/api/live_traffic")
def api_live_traffic():
    return jsonify(engine.get_live_traffic_snapshot())


@app.route("/api/threat_logs")
def api_threat_logs():
    limit = int(request.args.get("limit", 120))
    return jsonify({"logs": engine.get_threat_logs(limit=limit)})


@app.route("/api/top_devices")
def api_top_devices():
    return jsonify({"devices": engine.status().get("top_devices", [])})


if __name__ == "__main__":
    # Start attack emulation engine
    window_seconds = int(os.environ.get("SHADOWTWIN_WINDOW", "5"))
    stop_event = threading.Event()

    t = threading.Thread(target=_emulation_cycle, args=(stop_event, window_seconds), daemon=True)
    t.start()

    os.makedirs("templates", exist_ok=True)
    app.run(host="127.0.0.1", port=5000, debug=True)

