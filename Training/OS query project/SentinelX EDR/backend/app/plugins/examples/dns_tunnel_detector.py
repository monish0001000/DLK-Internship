"""
DNS Tunneling Detector Plugin
Detects potential DNS tunneling by analyzing subdomain length (entropy proxy).
"""

from typing import Dict, Any, List, Optional
from app.plugins.base_plugin import BaseDetectorPlugin

class DNSTunnelDetector(BaseDetectorPlugin):
    @property
    def name(self) -> str:
        return "DNS Tunneling Detector"
        
    @property
    def version(self) -> str:
        return "1.0.0"
        
    @property
    def description(self) -> str:
        return "Detects DNS tunneling via unusually long subdomains."
        
    def detect(self, event: Dict[str, Any], category: str, context: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
        if category != 'network_connection':
            return None
            
        # Simplistic proxy for DNS tunneling check in our limited telemetry:
        # If the remote address is a domain (not IP) and is unusually long
        remote_addr = str(event.get("remote_address", ""))
        
        # Check if it looks like a domain and has a very long subdomain prefix
        if len(remote_addr) > 50 and "." in remote_addr:
            # Assuming format: [long_base32_string].tunnel.com
            subdomain = remote_addr.split(".")[0]
            if len(subdomain) > 40:
                return [{
                    "title": "Potential DNS Tunneling Detected",
                    "severity": "high",
                    "description": f"Unusually long subdomain detected: {subdomain[:20]}...",
                    "tags": ["attack.T1071.004", "attack.command_and_control"],
                    "rule_id": "plugin-dns-tunnel"
                }]
                
        return None
