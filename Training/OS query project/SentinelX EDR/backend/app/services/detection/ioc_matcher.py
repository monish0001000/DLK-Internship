"""
SentinelX EDR - IOC Matcher
=============================
Matches telemetry events against known Indicators of Compromise.
"""

from typing import Dict, List, Any
import json
import logging
from sqlalchemy.orm import Session
from app.models.threat_intel import ThreatIntel

logger = logging.getLogger(__name__)

class IOCMatcher:
    def __init__(self):
        self.malicious_hashes: Dict[str, Dict] = {}  # hash → {source, severity, description, tags}
        self.malicious_ips: Dict[str, Dict] = {}
        self.malicious_domains: Dict[str, Dict] = {}
        
    def load_from_file(self, filepath: str) -> int:
        """Load static IOC database from JSON file."""
        count = 0
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                
            for h in data.get("hashes", []):
                val = h.get("value", "").lower()
                if val:
                    self.malicious_hashes[val] = h
                    count += 1
                    
            for ip in data.get("ips", []):
                val = ip.get("value", "")
                if val:
                    self.malicious_ips[val] = ip
                    count += 1
                    
            for domain in data.get("domains", []):
                val = domain.get("value", "").lower()
                if val:
                    self.malicious_domains[val] = domain
                    count += 1
                    
            logger.info(f"Loaded {count} IOCs from {filepath}")
        except Exception as e:
            logger.error(f"Failed to load IOCs from {filepath}: {e}")
            
        return count
        
    def load_from_db(self, db: Session) -> int:
        """Load active IOCs from the database into memory."""
        count = 0
        try:
            iocs = db.query(ThreatIntel).filter(ThreatIntel.is_active == True).all()
            for ioc in iocs:
                info = {
                    "source": ioc.source,
                    "severity": ioc.severity,
                    "description": ioc.description,
                    "tags": [t.strip() for t in ioc.tags.split(",")] if ioc.tags else []
                }
                
                val = ioc.value.lower()
                if ioc.ioc_type in ["hash_sha256", "hash_md5"]:
                    self.malicious_hashes[val] = info
                elif ioc.ioc_type == "ip":
                    self.malicious_ips[val] = info
                elif ioc.ioc_type == "domain":
                    self.malicious_domains[val] = info
                    
                count += 1
            logger.info(f"Loaded {count} active IOCs from database")
        except Exception as e:
            logger.error(f"Failed to load IOCs from database: {e}")
            
        return count
        
    def match_event(self, event: Dict[str, Any], category: str) -> List[Dict[str, Any]]:
        """Match an event against loaded IOCs."""
        matches = []
        
        if category == 'process_creation':
            # Check hashes
            h256 = str(event.get("hash_sha256", "")).lower()
            hmd5 = str(event.get("hash_md5", "")).lower()
            
            if h256 in self.malicious_hashes:
                info = self.malicious_hashes[h256]
                matches.append(self._format_match(h256, "hash_sha256", info))
            elif hmd5 in self.malicious_hashes:
                info = self.malicious_hashes[hmd5]
                matches.append(self._format_match(hmd5, "hash_md5", info))
                
            # Check domains in cmdline (simplistic)
            cmdline = str(event.get("cmdline", "")).lower()
            for domain, info in self.malicious_domains.items():
                if domain in cmdline:
                    matches.append(self._format_match(domain, "domain", info))
                    
        elif category == 'network_connection':
            # Check remote IP
            remote_ip = str(event.get("remote_address", ""))
            if remote_ip in self.malicious_ips:
                info = self.malicious_ips[remote_ip]
                matches.append(self._format_match(remote_ip, "ip", info))
                
        return matches
        
    def _format_match(self, value: str, ioc_type: str, info: Dict) -> Dict[str, Any]:
        return {
            "title": f"Malicious {ioc_type.upper()} Detected: {value}",
            "severity": info.get("severity", "high"),
            "description": info.get("description", f"Known malicious indicator from {info.get('source', 'unknown')}"),
            "tags": info.get("tags", []),
            "rule_id": f"ioc-{value[:10]}",
            "matched_value": value
        }
