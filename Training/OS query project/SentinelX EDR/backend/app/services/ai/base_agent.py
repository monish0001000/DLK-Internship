"""
SentinelX EDR - Base AI Agent
==============================
Abstract base class for all specialized AI agents in the pipeline.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import json
import logging

from app.services.ai.llm_client import llm_client

logger = logging.getLogger(__name__)

class BaseAIAgent(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the agent."""
        pass
        
    @property
    @abstractmethod
    def role(self) -> str:
        """Description of the agent's role."""
        pass
        
    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """The detailed instruction prompt for the LLM."""
        pass
        
    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent's logic.
        Synchronous execution (as requested for FastAPI sync db).
        """
        logger.info(f"Agent '{self.name}' starting processing...")
        user_prompt = self._build_user_prompt(context)
        
        try:
            raw_response = llm_client.generate(self.system_prompt, user_prompt, expect_json=True)
            parsed_result = self._parse_json(raw_response)
            logger.info(f"Agent '{self.name}' completed successfully.")
            return parsed_result
        except Exception as e:
            logger.error(f"Agent '{self.name}' failed: {e}")
            return {"error": str(e), "agent": self.name}
            
    @abstractmethod
    def _build_user_prompt(self, context: Dict[str, Any]) -> str:
        """Construct the prompt using the investigation context."""
        pass
        
    def _parse_json(self, raw_text: str) -> Dict[str, Any]:
        """Clean and parse JSON from LLM response."""
        # Strip markdown formatting blocks if the LLM ignored instructions
        clean_text = raw_text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]
        if clean_text.startswith("```"):
            clean_text = clean_text[3:]
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]
            
        return json.loads(clean_text.strip())
