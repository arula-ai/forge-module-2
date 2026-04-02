"""
LLM Client — Ollama API wrapper for AgentForge.

This module provides two client implementations:
  - LLMClient: Makes real HTTP requests to the Ollama /api/chat endpoint.
  - CachedLLMClient: Returns pre-built responses using keyword matching.
                     Used for offline mode (--cached) and test suites.

Students: You do NOT need to modify this file. Use the `chat()` method
from whichever client is passed to your pattern classes.

API:
    response = await llm.chat("your prompt here", system="optional system prompt")
    response.content      # Raw text from the model
    response.duration_ms  # How long the call took
    response.as_json()    # Parse content as JSON dict (raises ValueError if invalid)
"""

from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass
from pathlib import Path

import httpx


@dataclass
class LLMResponse:
    """Response from an LLM call."""

    content: str
    duration_ms: float

    def as_json(self) -> dict:
        """Parse content as JSON. Strips markdown code fences if present."""
        text = self.content.strip()
        # Strip markdown code fences (```json ... ``` or ``` ... ```)
        text = re.sub(r"^```(?:json)?\s*\n?", "", text)
        text = re.sub(r"\n?```\s*$", "", text)
        text = text.strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse LLM response as JSON: {e}") from e


class LLMClient:
    """Async client for Ollama's /api/chat endpoint."""

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "qwen3.5:4b",
        temperature: float = 0.3,
        timeout: float = 30.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.temperature = temperature
        self.timeout = timeout

    async def chat(
        self, prompt: str, system: str = "", temperature: float | None = None
    ) -> LLMResponse:
        """Send a chat request to Ollama and return the response."""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature if temperature is not None else self.temperature},
        }

        start = time.perf_counter()
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(f"{self.base_url}/api/chat", json=payload)
            resp.raise_for_status()
        duration_ms = (time.perf_counter() - start) * 1000

        data = resp.json()
        content = data.get("message", {}).get("content", "")
        return LLMResponse(content=content, duration_ms=duration_ms)


class CachedLLMClient(LLMClient):
    """Returns pre-built responses from cached_responses.json via keyword matching.

    Matching rules are evaluated in numbered order (1-17). First match wins.
    See the design spec Section 2 for the full algorithm.
    """

    def __init__(self, cache_path: str):
        super().__init__()
        with open(cache_path, "r") as f:
            self.cache: dict = json.load(f)

    async def chat(
        self, prompt: str, system: str = "", temperature: float | None = None
    ) -> LLMResponse:
        """Match the prompt against cached responses using keyword rules.

        Always returns a valid LLMResponse (never raises). If no rule matches,
        returns a JSON error object. Results are deterministic.
        """
        p = prompt.lower()
        s = system.lower()

        key = self._match(p, s)
        if key is not None:
            content = json.dumps(self.cache[key])
        else:
            content = json.dumps({"error": "No cached response matched", "status": "unknown"})
        return LLMResponse(content=content, duration_ms=1.0)

    def _match(self, prompt: str, system: str) -> str | None:
        """Evaluate the 17 matching rules in order. Return the cache key or None."""

        # Rules 1-4: Classification (prompt contains "classify" + incident keywords)
        if "classify" in prompt:
            if any(kw in prompt for kw in ("connection pool", "postgresql", "hikari")):
                return "classify_database"
            if any(kw in prompt for kw in ("double charge", "duplicate", "overcharge", "refund")):
                return "classify_billing"
            if any(kw in prompt for kw in ("503", "gateway", "upstream", "circuit breaker")):
                return "classify_network"
            if any(kw in prompt for kw in ("password reset", "email", "queue depth")):
                return "classify_general"

        # Rules 5-9: Handler responses (check SYSTEM prompt)
        if system and ("specialist" in system or "handler" in system):
            if "database" in system:
                return "handler_database"
            if "billing" in system or "payment" in system:
                return "handler_billing"
            if "network" in system:
                return "handler_network"
            if "email" in system:
                return "handler_email"
            return "handler_general"

        # Rules 10-12: Chain steps
        if ("parse" in prompt or "extract" in prompt) and "classify" not in prompt:
            return "chain_parse"
        if ("root cause" in prompt or "analyze" in prompt) and "classify" not in prompt:
            return "chain_analyze"
        if "recommend" in prompt:
            return "chain_recommend"

        # Rules 13-16: Parallel health checks
        health_keywords = ("health", "status", "check", "assess")
        if "memory" in prompt and any(kw in prompt for kw in health_keywords):
            return "parallel_memory_check"
        if "cpu" in prompt and any(kw in prompt for kw in health_keywords):
            return "parallel_cpu_check"
        if "disk" in prompt and any(kw in prompt for kw in health_keywords):
            return "parallel_disk_check"
        if "network" in prompt and any(kw in prompt for kw in health_keywords):
            return "parallel_network_check"

        # Rule 17: Fallback
        return None


def create_llm_client(cached: bool = False) -> LLMClient:
    """Factory to create the appropriate LLM client.

    Args:
        cached: If True, return a CachedLLMClient using data/cached_responses.json.
                If False, return a live LLMClient configured from environment variables.
    """
    if cached:
        cache_path = Path(__file__).parent.parent.parent / "data" / "cached_responses.json"
        return CachedLLMClient(str(cache_path))

    return LLMClient(
        base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
        model=os.environ.get("MODEL_NAME", "qwen3.5:4b"),
        temperature=float(os.environ.get("MODEL_TEMPERATURE", "0.3")),
        timeout=float(os.environ.get("REQUEST_TIMEOUT", "30")),
    )
