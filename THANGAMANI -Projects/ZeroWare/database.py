import sqlite3
import os
import json
import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'history.db')


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT,
            file_size INTEGER,
            md5 TEXT,
            sha256 TEXT,
            prediction TEXT,
            confidence REAL,
            trust_score INTEGER,
            risk_score INTEGER,
            zeroday_prob INTEGER,
            zerodna_id TEXT,
            reasons TEXT,
            behaviors TEXT,
            recommendations TEXT,
            scan_date TEXT,
            scan_duration REAL,
            quarantined INTEGER DEFAULT 0
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS quarantine (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_id INTEGER,
            original_path TEXT,
            quarantine_path TEXT,
            quarantine_date TEXT
        )
    ''')
    conn.commit()
    conn.close()


def save_scan(result: dict, duration: float) -> int:
    conn = get_conn()
    c = conn.cursor()
    features = result.get('features', {})
    pred = result.get('prediction', {})
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('''
        INSERT INTO scans (file_name, file_size, md5, sha256, prediction, confidence,
            trust_score, risk_score, zeroday_prob, zerodna_id, reasons, behaviors,
            recommendations, scan_date, scan_duration)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    ''', (
        result.get('file_name'),
        features.get('file_size', 0),
        features.get('md5', ''),
        features.get('sha256', ''),
        pred.get('label', ''),
        pred.get('confidence', 0),
        result.get('trust', {}).get('score', 0),
        result.get('risk_score', 0),
        result.get('zeroday_prob', 0),
        result.get('zerodna', {}).get('dna_id', ''),
        json.dumps(result.get('reasons', [])),
        json.dumps(result.get('behaviors', {})),
        json.dumps(result.get('recommendations', [])),
        now,
        duration
    ))
    scan_id = c.lastrowid
    conn.commit()
    conn.close()
    return scan_id


def get_all_scans(limit=100):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT * FROM scans ORDER BY id DESC LIMIT ?', (limit,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def get_scan_by_id(scan_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT * FROM scans WHERE id=?', (scan_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def get_stats():
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT COUNT(*) as total FROM scans')
    total = c.fetchone()['total']
    c.execute("SELECT COUNT(*) as cnt FROM scans WHERE prediction='Malware'")
    malware = c.fetchone()['cnt']
    c.execute("SELECT COUNT(*) as cnt FROM scans WHERE prediction='Safe'")
    safe = c.fetchone()['cnt']
    c.execute("SELECT COUNT(*) as cnt FROM scans WHERE prediction='Suspicious'")
    suspicious = c.fetchone()['cnt']
    c.execute('SELECT AVG(trust_score) as avg_trust FROM scans')
    avg_trust_row = c.fetchone()
    avg_trust = round(avg_trust_row['avg_trust'] or 0, 1)
    conn.close()
    return {
        'total': total,
        'malware': malware,
        'safe': safe,
        'suspicious': suspicious,
        'avg_trust': avg_trust
    }


def delete_scan(scan_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute('DELETE FROM scans WHERE id=?', (scan_id,))
    conn.commit()
    conn.close()
