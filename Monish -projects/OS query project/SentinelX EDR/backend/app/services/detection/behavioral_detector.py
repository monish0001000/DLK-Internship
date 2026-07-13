"""
SentinelX EDR - Behavioral Detector
====================================
Hardcoded heuristics for catching sophisticated attacks that bypass signatures.
"""

from typing import List, Dict, Any
import re

class BehavioralDetector:
    def evaluate_event(self, event: Dict[str, Any], category: str) -> List[Dict[str, Any]]:
        matches = []
        
        if category == 'processes' or category == 'process_creation':
            matches.extend(self._check_process(event))
        elif category == 'network_connections' or category == 'network_connection':
            matches.extend(self._check_network(event))
        elif category == 'startup_items' or category == 'startup_item':
            matches.extend(self._check_persistence(event))
            
        return matches
        
    def _check_process(self, event: Dict[str, Any]) -> List[Dict[str, Any]]:
        matches = []
        cmdline = str(event.get('cmdline', '')).lower()
        path = str(event.get('path', '')).lower()
        name = str(event.get('name', '')).lower()
        parent_name = str(event.get('parent_name', '')).lower()
        
        # 1. Encoded PowerShell
        if "powershell" in name or "pwsh" in name:
            if re.search(r'-(enc|encodedcommand|ec|en)\s+[A-Za-z0-9+/=]{20,}', cmdline):
                matches.append(self._alert("Encoded PowerShell Execution", "high", "T1059.001"))
                
        # 2. Download Cradles
        if ("invoke-webrequest" in cmdline or "iwr " in cmdline or 
            "downloadstring" in cmdline or "webclient" in cmdline or
            "certutil -urlcache" in cmdline):
            matches.append(self._alert("Command-Line Download Cradle", "high", "T1105"))
            
        # 3. Suspicious Parent-Child
        office_apps = ["winword.exe", "excel.exe", "powerpnt.exe", "outlook.exe"]
        suspicious_children = ["cmd.exe", "powershell.exe", "wscript.exe", "cscript.exe", "regsvr32.exe"]
        if parent_name in office_apps and name in suspicious_children:
             matches.append(self._alert("Suspicious Office Child Process", "critical", "T1566.001"))
             
        # 4. Credential Dumping
        if "mimikatz" in name or "mimikatz" in cmdline:
             matches.append(self._alert("Mimikatz Execution Detected", "critical", "T1003.001"))
        if "procdump" in name and "lsass" in cmdline:
             matches.append(self._alert("LSASS Process Memory Dump", "critical", "T1003.001"))
             
        # 5. Reverse Shells
        if ("nc " in cmdline or "ncat " in cmdline or "netcat " in cmdline) and "-e " in cmdline:
             matches.append(self._alert("Netcat Reverse Shell", "critical", "T1059.004"))
        if "/dev/tcp/" in cmdline:
             matches.append(self._alert("Bash Reverse Shell via /dev/tcp", "critical", "T1059.004"))
             
        # 6. LOLBins
        if name == "regsvr32.exe" and ("/i:http" in cmdline or "/i:ftp" in cmdline):
             matches.append(self._alert("Regsvr32 Remote Payload Execution", "high", "T1218.010"))
        if name == "mshta.exe" and ("http://" in cmdline or "https://" in cmdline):
             matches.append(self._alert("Mshta Remote Payload Execution", "high", "T1218.005"))
             
        # 8. Lateral Movement
        if name == "wmic.exe" and "process call create" in cmdline and "/node:" in cmdline:
             matches.append(self._alert("WMI Lateral Movement", "high", "T1047"))
             
        # 9. Test Rule: Suspicious Calculator Launch
        if name == "calc.exe" or name == "calculatorapp.exe":
             matches.append(self._alert("Suspicious Calculator Launch (E2E Test)", "critical", "T1059"))
             
        return matches
        
    def _check_network(self, event: Dict[str, Any]) -> List[Dict[str, Any]]:
        matches = []
        # 9. DNS Tunneling & High Entropy is complex, simplistic check for C2 ports
        remote_port = event.get('remote_port')
        if remote_port in [4444, 8888, 1337, 31337]:
             matches.append(self._alert("Connection to Suspicious Port", "high", "T1071"))
        return matches
        
    def _check_persistence(self, event: Dict[str, Any]) -> List[Dict[str, Any]]:
        matches = []
        path = str(event.get('path', '')).lower()
        # 7. Persistence - suspicious paths
        if "appdata\\local\\temp" in path or "windows\\temp" in path:
             matches.append(self._alert("Startup Item from Temp Directory", "high", "T1547.001"))
        return matches

    def _alert(self, title: str, severity: str, technique: str) -> Dict[str, Any]:
        return {
            "title": title,
            "severity": severity,
            "description": f"Behavioral detection heuristic fired for {technique}",
            "tags": [f"attack.{technique}"],
            "rule_id": f"behavioral-{technique}"
        }
