"""
SentinelX EDR - Unified LLM Client
===================================
Handles API requests to Gemini and OpenRouter with automatic fallbacks.
"""

import logging
import json
import httpx
from typing import Dict, Any, Optional

import google.generativeai as genai
from google.generativeai.types import generation_types

from app.config import get_settings

logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self):
        self.settings = get_settings()
        self._setup_gemini()
        
    def _setup_gemini(self) -> None:
        if self.settings.GEMINI_API_KEY:
            genai.configure(api_key=self.settings.GEMINI_API_KEY)
            self.gemini_model = genai.GenerativeModel(self.settings.GEMINI_MODEL)
            logger.info(f"Configured Gemini with model: {self.settings.GEMINI_MODEL}")
        else:
            self.gemini_model = None
            logger.warning("Gemini API key not found.")

    def generate(self, system_prompt: str, user_prompt: str, expect_json: bool = True) -> str:
        """
        Generate text from the LLM. Tries Gemini first, falls back to OpenRouter.
        If no keys are configured, returns a mock response.
        """
        response_text = None
        
        # 1. Try Gemini
        if self.gemini_model:
            try:
                response = self._call_gemini(system_prompt, user_prompt, expect_json)
                if response:
                    return response
            except Exception as e:
                logger.error(f"Gemini API failed: {e}. Falling back to OpenRouter...")
                
        # 2. Try OpenRouter
        if self.settings.OPENROUTER_API_KEY:
            try:
                response = self._call_openrouter(system_prompt, user_prompt, expect_json)
                if response:
                    return response
            except Exception as e:
                logger.error(f"OpenRouter API failed: {e}.")
                
        # 3. Fallback to mock
        logger.warning("All LLM providers failed or none configured. Using mock response.")
        return self._get_mock_response(system_prompt, expect_json)
        
    def _call_gemini(self, system_prompt: str, user_prompt: str, expect_json: bool) -> Optional[str]:
        # We prepend system prompt to user prompt as a simple way to handle instructions
        # for standard GenerativeModel if system_instruction is not supported in the installed version
        full_prompt = f"SYSTEM INSTRUCTIONS:\n{system_prompt}\n\nUSER INPUT:\n{user_prompt}"
        
        # If expecting JSON, ask explicitly
        if expect_json:
             full_prompt += "\n\nIMPORTANT: Return ONLY valid JSON. No markdown formatting blocks."
             
        response = self.gemini_model.generate_content(
            full_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.2,
            )
        )
        return response.text
        
    def _call_openrouter(self, system_prompt: str, user_prompt: str, expect_json: bool) -> Optional[str]:
        headers = {
            "Authorization": f"Bearer {self.settings.OPENROUTER_API_KEY}",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "SentinelX EDR",
        }
        
        payload = {
            "model": self.settings.OPENROUTER_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt + ("\nReturn ONLY valid JSON." if expect_json else "")}
            ],
            "temperature": 0.2
        }
        
        # Using sync httpx for FastAPI sync routes
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                f"{self.settings.OPENROUTER_BASE_URL}/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
            
    def _get_mock_response(self, system_prompt: str, expect_json: bool) -> str:
        """Raises an exception to prevent mock data in production."""
        raise RuntimeError("AI Provider not configured. Live mode requires Gemini or OpenRouter API key.")

# Singleton
llm_client = LLMClient()
