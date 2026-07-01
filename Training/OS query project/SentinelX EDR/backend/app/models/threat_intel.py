"""
SentinelX EDR - Threat Intelligence Model
==========================================
Stores Indicators of Compromise (IOCs) from multiple sources:
    - Bundled: Static IOCs shipped with the platform
    - AbuseIPDB: Malicious IP addresses with confidence scores
    - AlienVault OTX: Multi-type IOCs (hashes, IPs, domains, URLs)
    - MalwareBazaar: Malware sample hashes and tags
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float
from app.database import Base


class ThreatIntel(Base):
    """
    An Indicator of Compromise (IOC) in the threat intelligence database.
    
    IOC Types:
        - hash_sha256: SHA-256 file hash
        - hash_md5: MD5 file hash
        - ip: IPv4/IPv6 address
        - domain: Domain name
        - url: Full URL
    
    Sources:
        - bundled: Ships with the platform
        - abuseipdb: AbuseIPDB API feed
        - otx: AlienVault OTX feed
        - malwarebazaar: Abuse.ch MalwareBazaar
        - manual: Manually added by analyst
    """
    __tablename__ = "threat_intel"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ioc_type = Column(String(20), nullable=False, index=True)  # hash_sha256, hash_md5, ip, domain, url
    value = Column(String(2048), nullable=False, index=True)  # The actual IOC value
    source = Column(String(50), nullable=False, default="bundled")  # bundled, abuseipdb, otx, etc.
    severity = Column(String(20), nullable=False, default="high")  # critical, high, medium, low
    confidence = Column(Float, nullable=True)  # 0.0 - 1.0 confidence score
    description = Column(Text, nullable=True)  # Context about this IOC
    tags = Column(Text, nullable=True)  # Comma-separated tags (e.g., "malware,cobalt-strike,c2")
    is_active = Column(Boolean, default=True, nullable=False)
    first_seen = Column(DateTime(timezone=True), nullable=True)
    last_seen = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=True,
    )
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<ThreatIntel [{self.ioc_type}] {self.value[:40]} ({self.source})>"
