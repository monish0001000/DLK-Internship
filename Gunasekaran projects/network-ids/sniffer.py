"""
sniffer.py - Packet Ingestion Layer
"""
import pyshark
import threading
import queue
import sys

INTERFACE = "eth0"
BPF_FILTER = "tcp or udp"
QUEUE_MAXSIZE = 5000

packet_queue = queue.Queue(maxsize=QUEUE_MAXSIZE)

def _safe_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default

def parse_packet(pkt):
    try:
        ts = float(pkt.sniff_timestamp)
        length = _safe_int(getattr(pkt, "length", 0))
        if "IP" in pkt:
            src_ip = pkt.ip.src
            dst_ip = pkt.ip.dst
        else:
            return None
        proto = pkt.transport_layer
        if proto is None:
            return None
        src_port = _safe_int(getattr(pkt[proto.lower()], "srcport", 0))
        dst_port = _safe_int(getattr(pkt[proto.lower()], "dstport", 0))
        flags = None
        if proto == "TCP" and hasattr(pkt.tcp, "flags"):
            flags = pkt.tcp.flags
        return {
            "timestamp": ts, "src_ip": src_ip, "dst_ip": dst_ip,
            "src_port": src_port, "dst_port": dst_port,
            "protocol": proto, "length": length, "tcp_flags": flags,
        }
    except AttributeError:
        return None

def start_sniffer(interface=INTERFACE, bpf_filter=BPF_FILTER, stop_event=None):
    print(f"[sniffer] Starting capture on '{interface}' with filter '{bpf_filter}'")
    capture = pyshark.LiveCapture(interface=interface, bpf_filter=bpf_filter)
    try:
        for pkt in capture.sniff_continuously():
            if stop_event is not None and stop_event.is_set():
                break
            parsed = parse_packet(pkt)
            if parsed is None:
                continue
            try:
                packet_queue.put_nowait(parsed)
            except queue.Full:
                try:
                    packet_queue.get_nowait()
                except queue.Empty:
                    pass
                packet_queue.put_nowait(parsed)
    except KeyboardInterrupt:
        pass
    finally:
        capture.close()
        print("[sniffer] Capture stopped.")

def run_in_background(interface=INTERFACE, bpf_filter=BPF_FILTER):
    stop_event = threading.Event()
    t = threading.Thread(
        target=start_sniffer,
        kwargs={"interface": interface, "bpf_filter": bpf_filter, "stop_event": stop_event},
        daemon=True,
    )
    t.start()
    return t, stop_event

if __name__ == "__main__":
    iface = sys.argv[1] if len(sys.argv) > 1 else INTERFACE
    thread, stop_evt = run_in_background(interface=iface)
    try:
        while True:
            item = packet_queue.get()
            print(item)
    except KeyboardInterrupt:
        print("\n[main] Stopping...")
        stop_evt.set()
        thread.join(timeout=2)
