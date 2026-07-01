"""
SentinelX EDR - Base Plugin Definition
========================================
All custom detection plugins must inherit from this class.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class BaseDetectorPlugin(ABC):
    """
    Abstract base class for SentinelX detection plugins.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name."""
        pass
        
    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin version."""
        pass
        
    @property
    @abstractmethod
    def description(self) -> str:
        """Plugin description."""
        pass
        
    @abstractmethod
    def detect(self, event: Dict[str, Any], category: str, context: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
        """
        Evaluate an event.
        
        Args:
            event: The telemetry event dictionary.
            category: The event category (e.g., 'process_creation', 'network_connection').
            context: Additional context dict (contains 'db' and 'endpoint_id').
            
        Returns:
            A list of alert dictionaries if a threat is detected, None otherwise.
            Alert dict format: {"title": str, "severity": str, "description": str, "tags": List[str]}
        """
        pass
