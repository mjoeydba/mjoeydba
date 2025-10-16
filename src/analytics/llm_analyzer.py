"""LLM-powered analysis helpers using Ollama."""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import requests

from src.common.config import OllamaSettings

LOGGER = logging.getLogger(__name__)


class LLMAnalyzer:
    def __init__(self, settings: OllamaSettings):
        self._settings = settings

    def _build_prompt(self, title: str, metrics: List[Dict[str, Any]], issues: Optional[str] = None) -> str:
        lines = [f"# {title}"]
        lines.append("Provide a concise summary with actionable remediation steps.")
        if issues:
            lines.append("Known issues or context: " + issues)
        lines.append("Metrics:")
        for metric in metrics:
            lines.append(f"- {metric}")
        return "\n".join(lines)

    def analyze(self, title: str, metrics: List[Dict[str, Any]], issues: Optional[str] = None) -> Dict[str, Any]:
        prompt = self._build_prompt(title, metrics, issues)
        payload = {
            "model": self._settings.model,
            "prompt": prompt,
            "options": {
                "temperature": self._settings.temperature,
                "num_predict": self._settings.max_tokens,
            },
        }
        LOGGER.debug("Sending prompt to Ollama", extra={"payload": payload})
        response = requests.post(f"{self._settings.host}/api/generate", json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        return {
            "model": self._settings.model,
            "prompt": prompt,
            "response": data.get("response"),
        }


__all__ = ["LLMAnalyzer"]
