import os
from datetime import timedelta

class Config:
    # ── Flask ──────────────────────────────────────────────────
    SECRET_KEY = os.environ.get('SECRET_KEY', 'EDRLite-Ultra-Secure-Key-2024!')

    # ── Database (SQLite — zero setup) ────────────────────────
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f'sqlite:///{os.path.join(BASE_DIR, "edrlite.db")}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ── osquery ────────────────────────────────────────────────
    # On Kali Linux, osqueryi is usually at /usr/bin/osqueryi
    # Socket path for osqueryd daemon
    OSQUERY_SOCKET  = os.environ.get('OSQUERY_SOCKET',  '/var/osquery/osquery.em')
    OSQUERY_BINARY  = os.environ.get('OSQUERY_BINARY',  r'C:\Program Files\osquery\osqueryi.exe')

    # Set OSQUERY_SIMULATE=true to use built-in event simulator
    # (useful when running on Windows or when osquery is not installed)
    OSQUERY_SIMULATE = os.environ.get('OSQUERY_SIMULATE', 'false').lower() == 'true'

    # ── VirusTotal ─────────────────────────────────────────────
    VIRUSTOTAL_API_KEY = os.environ.get('VT_API_KEY', '62e5877a98eff76d838fd3eb68950698ece514113c88006be69193d69f5a3342')

    # ── Collection Intervals (seconds) ───────────────────────
    PROCESS_COLLECTION_INTERVAL  = int(os.environ.get('PROCESS_INTERVAL',  60))
    NETWORK_COLLECTION_INTERVAL  = int(os.environ.get('NETWORK_INTERVAL',  30))
    USB_COLLECTION_INTERVAL      = int(os.environ.get('USB_INTERVAL',      120))
    STARTUP_COLLECTION_INTERVAL  = int(os.environ.get('STARTUP_INTERVAL',  300))

    # ── Paths ────────────────────────────────────────────────
    IOC_DIR      = os.path.join(BASE_DIR, 'iocs')
    RULES_DIR    = os.path.join(BASE_DIR, 'rules')
    REPORTS_DIR  = os.path.join(BASE_DIR, 'reports_output')

    # ── Risk Score Thresholds ────────────────────────────────
    CRITICAL_SCORE = 80
    HIGH_SCORE     = 60
    MEDIUM_SCORE   = 40
    LOW_SCORE      = 20

    # ── Agent Authentication ─────────────────────────────────
    AGENT_AUTH_TOKEN = os.environ.get('AGENT_AUTH_TOKEN', 'edrlite-secret-token-123')

    # ── Session ──────────────────────────────────────────────
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    SESSION_COOKIE_HTTPONLY    = True

    # ── Admin Credentials (change in production!) ────────────
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'EDRLite@2024')
