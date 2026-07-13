"""
SentinelX EDR - Threat Intelligence Service
============================================
Handles importing and syncing IOCs from various sources.
"""

import logging
import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.threat_intel import ThreatIntel

logger = logging.getLogger(__name__)

def load_bundled_iocs(db: Session, filepath: str) -> int:
    """Load bundled IOCs from JSON file if not already loaded."""
    # Check if bundled IOCs already exist
    count = db.query(ThreatIntel).filter(ThreatIntel.source == "bundled").count()
    if count > 0:
        logger.info(f"Bundled IOCs already loaded ({count} records). Skipping.")
        return 0
        
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            
        added = 0
        now = datetime.now(timezone.utc)
        
        for h in data.get("hashes", []):
            db.add(ThreatIntel(
                ioc_type=h.get("type", "hash_sha256"),
                value=h.get("value", "").lower(),
                source="bundled",
                severity=h.get("severity", "high"),
                description=h.get("description", ""),
                tags=",".join(h.get("tags", [])),
                first_seen=now,
                last_seen=now
            ))
            added += 1
            
        for ip in data.get("ips", []):
            db.add(ThreatIntel(
                ioc_type="ip",
                value=ip.get("value", ""),
                source="bundled",
                severity=ip.get("severity", "high"),
                description=ip.get("description", ""),
                tags=",".join(ip.get("tags", [])),
                first_seen=now,
                last_seen=now
            ))
            added += 1
            
        for d in data.get("domains", []):
            db.add(ThreatIntel(
                ioc_type="domain",
                value=d.get("value", "").lower(),
                source="bundled",
                severity=d.get("severity", "high"),
                description=d.get("description", ""),
                tags=",".join(d.get("tags", [])),
                first_seen=now,
                last_seen=now
            ))
            added += 1
            
        db.commit()
        logger.info(f"Loaded {added} bundled IOCs.")
        return added
        
    except Exception as e:
        logger.error(f"Failed to load bundled IOCs: {e}")
        db.rollback()
        return 0

def sync_abuseipdb(db: Session, api_key: str) -> Dict[str, Any]:
    """Sync malicious IPs from AbuseIPDB."""
    logger.info("Syncing AbuseIPDB feed...")
    # In a real app, make requests to https://api.abuseipdb.com/api/v2/blacklist
    return {"feed_name": "abuseipdb", "iocs_added": 0, "iocs_updated": 0, "status": "simulated"}

def sync_otx(db: Session, api_key: str) -> Dict[str, Any]:
    """Sync indicators from AlienVault OTX."""
    logger.info("Syncing AlienVault OTX feed...")
    return {"feed_name": "otx", "iocs_added": 0, "iocs_updated": 0, "status": "simulated"}

def sync_malwarebazaar(db: Session) -> Dict[str, Any]:
    """Sync recent malware hashes from Abuse.ch MalwareBazaar."""
    logger.info("Syncing MalwareBazaar feed...")
    return {"feed_name": "malwarebazaar", "iocs_added": 0, "iocs_updated": 0, "status": "simulated"}

def get_ioc_stats(db: Session) -> Dict[str, Any]:
    types = dict(db.query(ThreatIntel.ioc_type, func.count(ThreatIntel.id)).group_by(ThreatIntel.ioc_type).all())
    sources = dict(db.query(ThreatIntel.source, func.count(ThreatIntel.id)).group_by(ThreatIntel.source).all())
    active = db.query(ThreatIntel).filter(ThreatIntel.is_active == True).count()
    
    return {
        "total": sum(types.values()),
        "active": active,
        "by_type": types,
        "by_source": sources
    }

def check_ioc(db: Session, value: str) -> Optional[Dict[str, Any]]:
    ioc = db.query(ThreatIntel).filter(ThreatIntel.value == value.lower(), ThreatIntel.is_active == True).first()
    if not ioc:
        return None
        
    return {
        "id": ioc.id,
        "type": ioc.ioc_type,
        "severity": ioc.severity,
        "source": ioc.source,
        "tags": ioc.tags.split(",") if ioc.tags else []
    }
