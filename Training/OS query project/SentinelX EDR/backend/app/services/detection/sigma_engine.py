"""
SentinelX EDR - Custom Sigma Rule Evaluator
=============================================
Evaluates telemetry events against loaded Sigma YAML rules.
"""

import os
import yaml
import re
import base64
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class SigmaRule:
    """Parsed representation of a Sigma detection rule."""
    title: str
    rule_id: str
    description: str
    severity: str
    logsource_category: str
    logsource_product: str
    detection: Dict[str, Any]
    condition: str
    tags: List[str] = field(default_factory=list)
    falsepositives: List[str] = field(default_factory=list)
    raw_yaml: str = ""

class SigmaEngine:
    def __init__(self):
        self.rules: List[SigmaRule] = []
        
    def load_rules_from_directory(self, rules_dir: str) -> int:
        """Load all .yml Sigma rules from directory recursively."""
        count = 0
        if not os.path.exists(rules_dir):
            logger.warning(f"Sigma rules directory not found: {rules_dir}")
            return 0
            
        for root, _, files in os.walk(rules_dir):
            for file in files:
                if file.endswith((".yml", ".yaml")):
                    try:
                        filepath = os.path.join(root, file)
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                            rule = self.load_rule_from_yaml(content)
                            if rule:
                                self.rules.append(rule)
                                count += 1
                    except Exception as e:
                        logger.error(f"Failed to load rule {file}: {e}")
        
        logger.info(f"Loaded {count} Sigma rules from {rules_dir}")
        return count
        
    def load_rule_from_yaml(self, yaml_content: str) -> Optional[SigmaRule]:
        """Parse a single Sigma YAML rule string."""
        try:
            parsed = yaml.safe_load(yaml_content)
            if not parsed or not isinstance(parsed, dict):
                return None
                
            logsource = parsed.get("logsource", {})
            detection = parsed.get("detection", {})
            condition = detection.pop("condition", "") if detection else ""
            
            # Remove condition from detection block for easier processing
            
            return SigmaRule(
                title=parsed.get("title", "Unknown Rule"),
                rule_id=parsed.get("id", ""),
                description=parsed.get("description", ""),
                severity=parsed.get("level", "medium"),
                logsource_category=logsource.get("category", ""),
                logsource_product=logsource.get("product", ""),
                detection=detection,
                condition=condition,
                tags=parsed.get("tags", []),
                falsepositives=parsed.get("falsepositives", []),
                raw_yaml=yaml_content
            )
        except Exception as e:
            logger.error(f"Error parsing YAML rule: {e}")
            return None

    def evaluate_event(self, event: Dict[str, Any], category: str = 'process_creation') -> List[Dict[str, Any]]:
        """Evaluate an event against all loaded rules matching the category."""
        matches = []
        
        for rule in self.rules:
            # Filter by category
            if rule.logsource_category and rule.logsource_category != category:
                continue
                
            if self._evaluate_rule(rule, event):
                matches.append({
                    "rule_id": rule.rule_id,
                    "title": rule.title,
                    "severity": rule.severity,
                    "tags": rule.tags,
                    "description": rule.description
                })
                
        return matches

    def _evaluate_rule(self, rule: SigmaRule, event: Dict[str, Any]) -> bool:
        """Evaluate a single rule's condition against an event."""
        if not rule.condition:
            return False
            
        # Simplified condition evaluator
        # In a full implementation, this needs a proper parser for Boolean logic
        condition = rule.condition.lower().strip()
        
        # Determine results for each selection block
        selection_results = {}
        for sel_name, sel_dict in rule.detection.items():
            if sel_name == "condition":
                continue
            selection_results[sel_name] = self._evaluate_selection(sel_dict, event)
            
        # Basic condition matching (handles simple cases)
        if condition in selection_results:
            return selection_results[condition]
            
        if condition.startswith("1 of selection"):
            # If any selection block is True
            prefix = "selection"
            if condition.startswith("1 of selection_"):
                 prefix = condition.split("*")[0].replace("1 of ", "")
            return any(res for name, res in selection_results.items() if name.startswith(prefix))
            
        if condition.startswith("all of selection"):
            # If all selection blocks are True
            prefix = "selection"
            if condition.startswith("all of selection_"):
                 prefix = condition.split("*")[0].replace("all of ", "")
            relevant_results = [res for name, res in selection_results.items() if name.startswith(prefix)]
            return all(relevant_results) if relevant_results else False
            
        # Handle "A and B", "A or B" (very simplistic parsing)
        if " and " in condition and " not " not in condition:
            parts = condition.split(" and ")
            return all(selection_results.get(p.strip(), False) for p in parts)
            
        if " or " in condition:
             parts = condition.split(" or ")
             return any(selection_results.get(p.strip(), False) for p in parts)

        # Fallback for complex unhandled conditions: if 'selection' block exists and is true
        if "selection" in selection_results:
             return selection_results["selection"]
             
        return False
        
    def _evaluate_selection(self, selection: Dict[str, Any], event: Dict[str, Any]) -> bool:
        """
        Evaluate a single selection block (dict of field matches).
        By default, all fields in a selection block are AND'ed together.
        If a field contains a list, those are OR'ed together.
        """
        if not isinstance(selection, dict):
            return False
            
        for key, value in selection.items():
            # Parse field name and modifiers (e.g. "cmdline|contains")
            parts = key.split("|")
            field_name = parts[0]
            modifiers = parts[1:] if len(parts) > 1 else []
            
            # Standardize field name for our telemetry model vs standard Sigma
            mapped_field = self._map_field_name(field_name)
            
            if mapped_field not in event or event[mapped_field] is None:
                 return False
                 
            event_val = str(event[mapped_field])
            
            # Handle lists (OR condition for values)
            if isinstance(value, list):
                field_match = any(self._check_value(event_val, str(v), modifiers) for v in value)
            else:
                field_match = self._check_value(event_val, str(value), modifiers)
                
            if not field_match:
                return False  # AND condition across fields failed
                
        return True
        
    def _check_value(self, event_val: str, rule_val: str, modifiers: List[str]) -> bool:
        """Check if event value matches rule value considering modifiers."""
        event_val_lower = event_val.lower()
        rule_val_lower = rule_val.lower()
        
        # Apply modifiers sequentially
        # For simplicity, we implement the most common ones
        
        if "contains" in modifiers:
            return rule_val_lower in event_val_lower
            
        if "startswith" in modifiers:
            return event_val_lower.startswith(rule_val_lower)
            
        if "endswith" in modifiers:
            return event_val_lower.endswith(rule_val_lower)
            
        if "re" in modifiers:
            try:
                return bool(re.search(rule_val, event_val))
            except re.error:
                return False
                
        if "base64" in modifiers:
            # Check if base64 encoded version of rule_val is in event_val
            try:
                 encoded = base64.b64encode(rule_val.encode()).decode()
                 return encoded in event_val or encoded.lower() in event_val_lower
            except Exception:
                 pass
                 
        # Default exact match (case insensitive typically for Windows)
        # Sigma usually assumes wildcards (* and ?) if no modifier
        if "*" in rule_val_lower or "?" in rule_val_lower:
            pattern = rule_val_lower.replace(".", r"\.").replace("*", ".*").replace("?", ".")
            try:
                 return bool(re.fullmatch(pattern, event_val_lower))
            except re.error:
                 pass

        return event_val_lower == rule_val_lower
        
    def _map_field_name(self, field_name: str) -> str:
        """Map standard Sigma field names to our internal telemetry model field names."""
        mapping = {
            "Image": "path",
            "CommandLine": "cmdline",
            "ParentImage": "parent_path",
            "ParentCommandLine": "parent_cmdline",
            "DestinationIp": "remote_address",
            "DestinationPort": "remote_port",
            "SourceIp": "local_address",
            "User": "user",
            "Hashes": "hash_sha256", # Simplification
        }
        return mapping.get(field_name, field_name.lower())
