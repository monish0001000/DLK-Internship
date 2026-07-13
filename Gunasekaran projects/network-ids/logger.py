"""
logger.py - Upgraded SIEM & Alerting Dashboard
Attack-type-aware logging with color-coded console output.
"""

import json
import os
import time
from datetime import datetime

ALERTS_PATH = os.path.join("data", "alerts.json")

stats = {
    "total_flows_seen": 0,
    "total_alerts": 0,
    "port_scan": 0,
    "ddos_flood": 0,
    "brute_force": 0,
    "anomaly": 0,
    "start_time": time.time(),
}

# Terminal color codes
COLORS = {
    "PORT_SCAN":   "\033[95m",   # Magenta
    "DDOS_FLOOD":  "\033[91m",   # Red
    "BRUTE_FORCE": "\033[93m",   # Yellow
    "ANOMALY":     "\033[91m",   # Red
    "RESET":       "\033[0m",
    "CYAN":        "\033[96m",
    "GREEN":       "\033[92m",
}


def _ensure_dir():
    os.makedirs(os.path.dirname(ALERTS_PATH), exist_ok=True)


def log_alert(flow, result):
    """Log an attack alert to file and console."""
    _ensure_dir()

    attack_type = result["attack_type"]
    severity    = result["severity"]
    confidence  = result["confidence"]
    reason      = result["reason"]

    alert = {
        "timestamp":   datetime.now().isoformat(),
        "attack_type": attack_type,
        "severity":    severity,
        "confidence":  round(confidence, 4),
        "src_ip":      flow["src_ip"],
        "dst_ip":      flow["dst_ip"],
        "src_port":    flow["src_port"],
        "dst_port":    flow["dst_port"],
        "protocol":    flow["protocol"],
        "packet_rate": flow["packet_rate"],
        "syn_count":   flow["syn_count"],
        "reason":      reason,
    }

    with open(ALERTS_PATH, "a") as f:
        f.write(json.dumps(alert) + "\n")

    stats["total_alerts"] += 1
    key = attack_type.lower()
    if key in stats:
        stats[key] += 1

    color = COLORS.get(attack_type, COLORS["ANOMALY"])
    reset = COLORS["RESET"]

    print(
        f"{color}[{severity}] {attack_type} | "
        f"{flow['src_ip']}:{flow['src_port']} -> "
        f"{flow['dst_ip']}:{flow['dst_port']} ({flow['protocol']}) | "
        f"conf={confidence*100:.1f}% | {reason}{reset}"
    )


def log_normal(flow):
    stats["total_flows_seen"] += 1


def print_dashboard():
    uptime = int(time.time() - stats["start_time"])
    cyan  = COLORS["CYAN"]
    green = COLORS["GREEN"]
    reset = COLORS["RESET"]

    print(
        f"\n{cyan}{'='*65}\n"
        f"  [DASHBOARD] uptime={uptime}s | "
        f"flows={stats['total_flows_seen']} | "
        f"alerts={stats['total_alerts']}\n"
        f"  PORT_SCAN={stats['port_scan']} | "
        f"DDOS={stats['ddos_flood']} | "
        f"BRUTE_FORCE={stats['brute_force']} | "
        f"ANOMALY={stats['anomaly']}\n"
        f"{'='*65}{reset}"
    )
