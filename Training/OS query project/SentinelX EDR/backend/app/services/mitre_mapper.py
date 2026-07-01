"""
SentinelX EDR - MITRE ATT&CK Mapper
====================================
Maps alerts and rules to the MITRE ATT&CK framework.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.detection_rule import DetectionRule

logger = logging.getLogger(__name__)

class MitreMapper:
    def __init__(self):
        self.techniques: Dict[str, Dict] = {}
        self.tactics: Dict[str, List[str]] = {}
        
    def load_mitre_data(self, filepath: str) -> int:
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                
            for t in data:
                tid = t.get("technique_id")
                if tid:
                    self.techniques[tid] = t
                    tactic = t.get("tactic", "Unknown")
                    if tactic not in self.tactics:
                        self.tactics[tactic] = []
                    self.tactics[tactic].append(tid)
                    
            logger.info(f"Loaded {len(self.techniques)} MITRE techniques across {len(self.tactics)} tactics.")
            return len(self.techniques)
        except Exception as e:
            logger.error(f"Failed to load MITRE data: {e}")
            return 0
            
    def map_technique(self, technique_id: str) -> Optional[Dict[str, Any]]:
        # Handle subtechniques (e.g. T1059.001) by checking exactly, 
        # or falling back to parent (e.g. T1059)
        if technique_id in self.techniques:
            return self.techniques[technique_id]
            
        parent_id = technique_id.split('.')[0]
        if parent_id in self.techniques:
            return self.techniques[parent_id]
            
        return None
        
    def map_from_tags(self, tags: List[str]) -> List[str]:
        t_codes = []
        for tag in tags:
            tag_upper = tag.upper()
            if tag_upper.startswith("ATTACK.T"):
                t_code = tag_upper.replace("ATTACK.", "")
                t_codes.append(t_code)
        return t_codes
        
    def get_coverage_matrix(self, db: Session) -> Dict[str, Dict[str, bool]]:
        # Find which techniques have enabled rules
        covered = set()
        rules = db.query(DetectionRule.mitre_ids).filter(
            DetectionRule.mitre_ids.isnot(None),
            DetectionRule.is_enabled == True
        ).all()
        
        for r in rules:
            if r[0]:
                for t in r[0].split(','):
                    covered.add(t.strip().upper())
                    
        matrix = {}
        for tactic, techniques in self.tactics.items():
            matrix[tactic] = {}
            for t in techniques:
                matrix[tactic][t] = t in covered or t.split('.')[0] in covered
                
        return matrix
        
    def get_tactic_summary(self) -> List[Dict[str, Any]]:
        return [{"tactic": k, "technique_count": len(v)} for k, v in self.tactics.items()]

# Singleton instance
mitre_mapper = MitreMapper()
