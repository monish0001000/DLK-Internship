import os
import json
import time
import socket
import logging
import requests
import threading
import subprocess

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] AGENT: %(message)s')
logger = logging.getLogger(__name__)

# Load config relative to script location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE_DIR, 'agent_config.json'), 'r') as f:
    config = json.load(f)

SERVER_URL = config.get('server_url', 'http://127.0.0.1:5000')
AUTH_TOKEN = config.get('auth_token', '')
OSQUERY_BIN = config.get('osquery_path', r'C:\Program Files\osquery\osqueryi.exe')

HEADERS = {'Authorization': f'Bearer {AUTH_TOKEN}', 'Content-Type': 'application/json'}

def get_os_version():
    try:
        res = subprocess.run([OSQUERY_BIN, '--json', 'SELECT name, version FROM os_version;'], capture_output=True, text=True)
        data = json.loads(res.stdout)
        if data:
            return f"{data[0].get('name')} {data[0].get('version')}"
    except:
        pass
    return "Windows (Unknown)"

# Collect host info once
hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)
os_version = get_os_version()

def run_osquery(query):
    try:
        # Fallback for systems without osqueryi in PATH, use absolute path if available
        result = subprocess.run([OSQUERY_BIN, '--json', query], capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except Exception as e:
        logger.error(f"osquery error: {e}")
        return []

def send_telemetry(event_type, query, interval):
    while True:
        logger.info(f"Collecting {event_type}...")
        data = run_osquery(query)
        if data:
            payload = {
                "hostname": hostname,
                "ip_address": ip_address,
                "os_version": os_version,
                "events": data
            }
            try:
                res = requests.post(f"{SERVER_URL}/api/v1/telemetry/{event_type}", json=payload, headers=HEADERS)
                logger.info(f"Sent {len(data)} {event_type} events. Status: {res.status_code}")
            except Exception as e:
                logger.error(f"Failed to connect to server: {e}")
        time.sleep(interval)

QUERIES = {
    'process': "SELECT pid, name, cmdline, path, uid, gid, parent, state, start_time FROM processes LIMIT 200;",
    'network': "SELECT p.name, s.pid, s.fd, s.family, s.protocol, s.local_address, s.local_port, s.remote_address, s.remote_port, s.state FROM process_open_sockets s JOIN processes p ON s.pid = p.pid WHERE s.remote_address != '' AND s.remote_address != '127.0.0.1' AND s.remote_address != '0.0.0.0' LIMIT 100;",
    'startup': "SELECT name, path, args, type, status FROM startup_items;",
    'usb': "SELECT vendor, model, serial, removable FROM usb_devices;"
}

if __name__ == "__main__":
    logger.info("="*50)
    logger.info(f" EDRLite Cloud Agent (v3.0) starting on {hostname}")
    logger.info(f" Connecting to Server: {SERVER_URL}")
    logger.info("="*50)
    
    threads = []
    for event_type, query in QUERIES.items():
        interval = config['intervals'].get(event_type, 60)
        t = threading.Thread(target=send_telemetry, args=(event_type, query, interval), daemon=True)
        t.start()
        threads.append(t)
        
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Agent shutting down.")
