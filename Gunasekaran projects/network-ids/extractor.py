"""
extractor.py - Stateful Feature Extraction Pipeline
"""
import time
import threading
import csv
import os
from collections import defaultdict, deque
from sniffer import run_in_background, packet_queue

WINDOW_SECONDS = 2.0
EXPORT_INTERVAL = 1.0
CSV_PATH = os.path.join("data", "flow_features.csv")

CSV_FIELDS = [
    "window_end", "src_ip", "dst_ip", "src_port", "dst_port", "protocol",
    "packet_count", "byte_count", "packet_rate", "byte_rate",
    "syn_count", "avg_packet_size",
]

flows = defaultdict(deque)
flows_lock = threading.Lock()

def flow_key(pkt):
    return (pkt["src_ip"], pkt["dst_ip"], pkt["src_port"], pkt["dst_port"], pkt["protocol"])

def ingest_loop(stop_event):
    while not stop_event.is_set():
        try:
            pkt = packet_queue.get(timeout=1)
        except Exception:
            continue
        key = flow_key(pkt)
        with flows_lock:
            flows[key].append(pkt)

def _is_syn(pkt):
    flags = pkt.get("tcp_flags")
    if not flags:
        return False
    try:
        val = int(flags, 16)
        return bool(val & 0x02) and not bool(val & 0x10)
    except (TypeError, ValueError):
        return False

def compute_features(now):
    results = []
    cutoff = now - WINDOW_SECONDS
    with flows_lock:
        dead_keys = []
        for key, dq in flows.items():
            while dq and dq[0]["timestamp"] < cutoff:
                dq.popleft()
            if not dq:
                dead_keys.append(key)
                continue
            packet_count = len(dq)
            byte_count = sum(p["length"] for p in dq)
            syn_count = sum(1 for p in dq if _is_syn(p))
            span = max(now - dq[0]["timestamp"], 0.001)
            src_ip, dst_ip, src_port, dst_port, proto = key
            results.append({
                "window_end": round(now, 3),
                "src_ip": src_ip,
                "dst_ip": dst_ip,
                "src_port": src_port,
                "dst_port": dst_port,
                "protocol": proto,
                "packet_count": packet_count,
                "byte_count": byte_count,
                "packet_rate": round(packet_count / span, 2),
                "byte_rate": round(byte_count / span, 2),
                "syn_count": syn_count,
                "avg_packet_size": round(byte_count / packet_count, 2),
            })
        for k in dead_keys:
            del flows[k]
    return results

def _ensure_csv():
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    new_file = not os.path.exists(CSV_PATH)
    f = open(CSV_PATH, "a", newline="")
    writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
    if new_file:
        writer.writeheader()
    return f, writer

def export_loop(stop_event, on_features=None):
    f, writer = _ensure_csv()
    try:
        while not stop_event.is_set():
            time.sleep(EXPORT_INTERVAL)
            now = time.time()
            rows = compute_features(now)
            for row in rows:
                print(f"[extractor] {row}")
                writer.writerow(row)
            if rows:
                f.flush()
            if on_features:
                on_features(rows)
    finally:
        f.close()

def start_extractor(interface="eth0", on_features=None):
    stop_event = threading.Event()
    sniff_thread, sniff_stop = run_in_background(interface=interface)
    ingest_thread = threading.Thread(target=ingest_loop, args=(stop_event,), daemon=True)
    ingest_thread.start()
    export_thread = threading.Thread(
        target=export_loop, args=(stop_event, on_features), daemon=True
    )
    export_thread.start()
    return stop_event, sniff_stop

if __name__ == "__main__":
    import sys
    iface = sys.argv[1] if len(sys.argv) > 1 else "eth0"
    print(f"[extractor] Writing features to {CSV_PATH}")
    stop_event, sniff_stop = start_extractor(interface=iface)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[main] Stopping extractor...")
        stop_event.set()
        sniff_stop.set()
        time.sleep(1)
