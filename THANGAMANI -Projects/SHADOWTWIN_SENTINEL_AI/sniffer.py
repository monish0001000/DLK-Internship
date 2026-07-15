import time
import queue
from dataclasses import dataclass
from typing import Optional, Dict, Any, List

import pandas as pd


@dataclass
class SniffWindowResult:
    window_start_ts: float
    window_end_ts: float
    features_df: pd.DataFrame


def _safe_int(x, default=0):
    try:
        return int(x)
    except Exception:
        return default


def _protocol_percent(counts: Dict[str, int], proto: str, total: int) -> float:
    if total <= 0:
        return 0.0
    return float(counts.get(proto, 0)) / float(total) * 100.0


def _compute_inter_arrival(times: List[float]) -> float:
    if len(times) < 2:
        return 0.0
    times_sorted = sorted(times)
    diffs = [t2 - t1 for t1, t2 in zip(times_sorted[:-1], times_sorted[1:])]
    diffs = [d for d in diffs if d >= 0]
    if not diffs:
        return 0.0
    return float(sum(diffs) / len(diffs))


def extract_features_from_packets(packet_iter, window_start_ts: float, window_end_ts: float) -> pd.DataFrame:
    """Convert an iterable of PyShark-like packets into a per-source-IP feature DataFrame."""

    agg: Dict[str, Dict[str, Any]] = {}

    for pkt in packet_iter:
        try:
            # Timestamp
            ts = None
            sniff_time = getattr(pkt, "sniff_time", None)
            if sniff_time is not None:
                try:
                    ts = float(sniff_time.timestamp())
                except Exception:
                    ts = None
            if ts is None:
                ts = float(getattr(getattr(pkt, "frame_info", None), "time_epoch", 0.0) or 0.0)

            if ts is not None and (ts < window_start_ts or ts > window_end_ts):
                continue

            # IPs
            src_ip = None
            dst_ip = None
            if hasattr(pkt, "ip"):
                src_ip = getattr(pkt.ip, "src", None)
                dst_ip = getattr(pkt.ip, "dst", None)
            elif hasattr(pkt, "ipv6"):
                src_ip = getattr(pkt.ipv6, "src", None)
                dst_ip = getattr(pkt.ipv6, "dst", None)

            if not src_ip:
                continue

            # Packet length
            pkt_len = 0
            try:
                pkt_len = _safe_int(getattr(getattr(pkt, "length", None), "__str__", lambda: 0)())
            except Exception:
                try:
                    pkt_len = _safe_int(getattr(pkt, "length", 0))
                except Exception:
                    pkt_len = 0

            if src_ip not in agg:
                agg[src_ip] = {
                    "packet_count": 0,
                    "total_size": 0,
                    "proto_counts": {"TCP": 0, "UDP": 0, "ICMP": 0},
                    "syn": 0,
                    "ack": 0,
                    "rst": 0,
                    "dst_ips": set(),
                    "ports": set(),
                    "first_ts": ts if ts else None,
                    "last_ts": ts if ts else None,
                    "timestamps": [],
                }

            a = agg[src_ip]
            a["packet_count"] += 1
            a["total_size"] += int(pkt_len or 0)
            a["timestamps"].append(float(ts or 0.0))
            if dst_ip:
                a["dst_ips"].add(dst_ip)

            # Protocol parsing
            if hasattr(pkt, "tcp"):
                a["proto_counts"]["TCP"] += 1
                flags_str = str(getattr(getattr(pkt.tcp, "flags", ""), "__str__", lambda: str(pkt.tcp.flags))())

                if getattr(pkt.tcp, "flags_syn", False):
                    a["syn"] += 1
                elif "syn" in flags_str.lower():
                    a["syn"] += 1

                if getattr(pkt.tcp, "flags_ack", False):
                    a["ack"] += 1
                elif "ack" in flags_str.lower():
                    a["ack"] += 1

                if getattr(pkt.tcp, "flags_rst", False):
                    a["rst"] += 1
                elif "rst" in flags_str.lower():
                    a["rst"] += 1

                dport = getattr(pkt.tcp, "dstport", None)
                sport = getattr(pkt.tcp, "srcport", None)
                if dport is not None:
                    a["ports"].add(str(dport))
                elif sport is not None:
                    a["ports"].add(str(sport))

            elif hasattr(pkt, "udp"):
                a["proto_counts"]["UDP"] += 1
                dport = getattr(pkt.udp, "dstport", None)
                sport = getattr(pkt.udp, "srcport", None)
                if dport is not None:
                    a["ports"].add(str(dport))
                elif sport is not None:
                    a["ports"].add(str(sport))

            elif hasattr(pkt, "icmp") or hasattr(pkt, "icmpv6"):
                a["proto_counts"]["ICMP"] += 1

            if ts:
                if a["first_ts"] is None:
                    a["first_ts"] = float(ts)
                a["last_ts"] = float(ts)

        except Exception:
            continue

    rows = []
    for src_ip, a in agg.items():
        packet_count = a["packet_count"]
        avg_pkt_size = float(a["total_size"]) / float(packet_count) if packet_count else 0.0

        tcp_pct = _protocol_percent(a["proto_counts"], "TCP", packet_count)
        udp_pct = _protocol_percent(a["proto_counts"], "UDP", packet_count)
        icmp_pct = _protocol_percent(a["proto_counts"], "ICMP", packet_count)

        duration = 0.0
        if a["first_ts"] is not None and a["last_ts"] is not None:
            duration = max(0.0, float(a["last_ts"]) - float(a["first_ts"]))
        if duration <= 0:
            duration = max(0.0001, window_end_ts - window_start_ts)

        syn_rate = float(a["syn"]) / duration
        ack_rate = float(a["ack"]) / duration
        rst_rate = float(a["rst"]) / duration

        rows.append(
            {
                "src_ip": src_ip,
                "packet_count": packet_count,
                "avg_packet_size": avg_pkt_size,
                "tcp_pct": tcp_pct,
                "udp_pct": udp_pct,
                "icmp_pct": icmp_pct,
                "syn_rate": syn_rate,
                "ack_rate": ack_rate,
                "rst_rate": rst_rate,
                "dst_ip_diversity": float(len(a["dst_ips"])),
                "unique_ports_targeted": float(len(a["ports"])),
                "flow_duration": float(duration),
                "inter_arrival_time": float(_compute_inter_arrival(a["timestamps"])),
                "window_start_ts": window_start_ts,
                "window_end_ts": window_end_ts,
            }
        )

    return pd.DataFrame(rows)


def start_sniffer(
    window_seconds: int = 5,
    interface: Optional[str] = None,
    pcap_path: Optional[str] = None,
    out_queue: Optional[queue.Queue] = None,
):
    """Run sniffing loop; push per-window extracted features into out_queue."""

    if out_queue is None:
        out_queue = queue.Queue()

    import pyshark

    if not interface and not pcap_path:
        raise ValueError("Either interface or pcap_path must be provided")

    cap = pyshark.FileCapture(pcap_path, keep_packets=False) if pcap_path else pyshark.LiveCapture(interface=interface, keep_packets=False)
    pkt_iter = iter(cap)

    while True:
        window_start_ts = time.time()
        window_end_ts = window_start_ts + window_seconds

        packets = []
        while True:
            try:
                pkt = next(pkt_iter)
                packets.append(pkt)
            except StopIteration:
                break
            except Exception:
                continue

            if time.time() >= window_end_ts:
                break

        features_df = extract_features_from_packets(packets, window_start_ts, window_end_ts)
        out_queue.put(SniffWindowResult(window_start_ts, window_end_ts, features_df))


if __name__ == "__main__":
    print("sniffer.py loaded. Use via app.py or start_sniffer().")

