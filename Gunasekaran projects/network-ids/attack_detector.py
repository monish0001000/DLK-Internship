"""
attack_detector.py - Multi-Attack Detection Engine
Combines ML model prediction with rule-based heuristics to classify
specific attack types: Port Scan, DDoS/Flood, Brute Force, ARP Spoofing.

Used by predictor.py as the main classification engine.
"""

from collections import defaultdict
import time

# ---- Attack Thresholds (tune these based on your network) ----
PORTSCAN_UNIQUE_PORTS   = 10    # unique dst ports from same src in window = port scan
PORTSCAN_SYN_MIN        = 1     # minimum SYN count to consider scan
DDOS_PACKET_RATE        = 100   # packets/sec threshold for flood
BRUTEFORCE_PORTS        = {22, 21, 3389, 23, 5900, 80, 443}  # common brute-forced ports
BRUTEFORCE_MIN_PACKETS  = 10    # repeated attempts to same port

# Track per-source-IP state across windows for multi-window analysis
_src_port_tracker = defaultdict(set)    # src_ip -> set of dst_ports seen
_src_attempt_tracker = defaultdict(lambda: defaultdict(int))  # src_ip -> dst_port -> count
_last_cleanup = time.time()
CLEANUP_INTERVAL = 30  # seconds


def _cleanup_trackers():
    """Periodically reset trackers to avoid stale state."""
    global _last_cleanup
    now = time.time()
    if now - _last_cleanup > CLEANUP_INTERVAL:
        _src_port_tracker.clear()
        _src_attempt_tracker.clear()
        _last_cleanup = now


def classify_attack(flow, ml_confidence):
    """
    Given a flow dict (from extractor) and ML anomaly confidence (0-1),
    returns a dict:
      {
        "is_anomaly": bool,
        "attack_type": str,   # "PORT_SCAN" | "DDOS" | "BRUTE_FORCE" | "ANOMALY" | "NORMAL"
        "severity":    str,   # "HIGH" | "MEDIUM" | "LOW"
        "confidence":  float,
        "reason":      str,
      }
    """
    _cleanup_trackers()

    src_ip   = flow["src_ip"]
    dst_ip   = flow["dst_ip"]
    dst_port = flow["dst_port"]
    protocol = flow["protocol"]
    syn_count    = flow.get("syn_count", 0)
    packet_rate  = flow.get("packet_rate", 0)
    packet_count = flow.get("packet_count", 0)

    # Update trackers
    _src_port_tracker[src_ip].add(dst_port)
    _src_attempt_tracker[src_ip][dst_port] += packet_count

    # ── Rule 1: Port Scan ──────────────────────────────────────────────
    unique_ports = len(_src_port_tracker[src_ip])
    if unique_ports >= PORTSCAN_UNIQUE_PORTS and syn_count >= PORTSCAN_SYN_MIN:
        return {
            "is_anomaly": True,
            "attack_type": "PORT_SCAN",
            "severity": "HIGH",
            "confidence": max(ml_confidence, 0.90),
            "reason": f"{src_ip} scanned {unique_ports} unique ports (SYN={syn_count})",
        }

    # ── Rule 2: DDoS / Packet Flood ───────────────────────────────────
    if packet_rate >= DDOS_PACKET_RATE:
        return {
            "is_anomaly": True,
            "attack_type": "DDOS_FLOOD",
            "severity": "HIGH",
            "confidence": max(ml_confidence, 0.92),
            "reason": f"{src_ip} -> {dst_ip} packet_rate={packet_rate}/s (threshold={DDOS_PACKET_RATE})",
        }

    # ── Rule 3: Brute Force ───────────────────────────────────────────
    if dst_port in BRUTEFORCE_PORTS:
        attempts = _src_attempt_tracker[src_ip][dst_port]
        if attempts >= BRUTEFORCE_MIN_PACKETS:
            return {
                "is_anomaly": True,
                "attack_type": "BRUTE_FORCE",
                "severity": "HIGH",
                "confidence": max(ml_confidence, 0.88),
                "reason": f"{src_ip} -> {dst_ip}:{dst_port} ({protocol}) repeated {attempts} times",
            }

    # ── Rule 4: ML-only Anomaly (no specific rule matched) ────────────
    if ml_confidence >= 0.60:
        return {
            "is_anomaly": True,
            "attack_type": "ANOMALY",
            "severity": "MEDIUM" if ml_confidence < 0.85 else "HIGH",
            "confidence": ml_confidence,
            "reason": f"ML model flagged {src_ip} -> {dst_ip}:{dst_port} (conf={ml_confidence:.2f})",
        }

    # ── Normal ────────────────────────────────────────────────────────
    return {
        "is_anomaly": False,
        "attack_type": "NORMAL",
        "severity": "LOW",
        "confidence": 1 - ml_confidence,
        "reason": "normal traffic",
    }
