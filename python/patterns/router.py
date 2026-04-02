"""
Intent Router Pattern — Classify incidents and route to specialist handlers.

The IncidentRouter:
  1. Classifies an incident into a category (database, network, billing, etc.)
  2. Routes to a specialist handler based on the classification
  3. Falls back to a general handler if confidence is low

Students: Implement classify() and route(). Everything else is provided.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from rich.console import Console

from .llm_client import LLMClient

console = Console()


class IncidentCategory(str, Enum):
    """Categories for incident classification."""

    DATABASE = "technical/database"
    NETWORK = "technical/network"
    BILLING = "billing/payment"
    EMAIL = "general/email"
    OTHER = "general/other"


@dataclass
class RouteResult:
    """Result of classifying an incident."""

    category: IncidentCategory
    confidence: float
    reasoning: str
    handler_name: str


@dataclass
class HandlerResponse:
    """Response from a specialist handler."""

    handler: str
    summary: str
    priority: str
    escalation_needed: bool


@dataclass
class IncidentHandler:
    """A specialist handler for a specific incident category."""

    name: str
    category: IncidentCategory
    system_prompt: str
    llm: LLMClient

    async def handle(self, incident: dict) -> HandlerResponse:
        """Process an incident and return a structured response."""
        prompt = (
            f"Analyze this incident and provide your specialist assessment.\n\n"
            f"Title: {incident.get('title', 'N/A')}\n"
            f"Description: {incident.get('description', 'N/A')}\n"
            f"Severity: {incident.get('severity', 'unknown')}\n"
            f"Logs:\n{incident.get('logs', 'No logs available')}\n\n"
            "Respond with ONLY this JSON:\n"
            '{\n'
            f'  "handler": "{self.name}",\n'
            '  "summary": "<one sentence assessment>",\n'
            '  "priority": "<low|medium|high|critical>",\n'
            '  "escalation_needed": <true|false>\n'
            '}'
        )
        response = await self.llm.chat(prompt, system=self.system_prompt)
        data = response.as_json()
        return HandlerResponse(
            handler=data.get("handler", self.name),
            summary=data.get("summary", "No summary provided"),
            priority=data.get("priority", "medium"),
            escalation_needed=data.get("escalation_needed", False),
        )


class IncidentRouter:
    """Routes incidents to specialist handlers based on LLM classification."""

    def __init__(self, llm: LLMClient, confidence_threshold: float = 0.6):
        self.llm = llm
        self.confidence_threshold = confidence_threshold
        self.handlers = self._build_handlers()
        self.fallback_handler = self.handlers[IncidentCategory.OTHER]

    def _build_handlers(self) -> dict[IncidentCategory, IncidentHandler]:
        """Create specialist handlers for each incident category."""
        return {
            IncidentCategory.DATABASE: IncidentHandler(
                name="Database Specialist",
                category=IncidentCategory.DATABASE,
                system_prompt=(
                    "You are a database incident specialist. Analyze database-related "
                    "incidents and provide actionable recommendations. Respond ONLY with JSON."
                ),
                llm=self.llm,
            ),
            IncidentCategory.NETWORK: IncidentHandler(
                name="Network Specialist",
                category=IncidentCategory.NETWORK,
                system_prompt=(
                    "You are a network infrastructure specialist. Analyze network and "
                    "gateway incidents and provide remediation steps. Respond ONLY with JSON."
                ),
                llm=self.llm,
            ),
            IncidentCategory.BILLING: IncidentHandler(
                name="Billing Specialist",
                category=IncidentCategory.BILLING,
                system_prompt=(
                    "You are a billing and payment incident specialist. Analyze billing-related "
                    "incidents and provide refund/resolution recommendations. Respond ONLY with JSON."
                ),
                llm=self.llm,
            ),
            IncidentCategory.EMAIL: IncidentHandler(
                name="Email Specialist",
                category=IncidentCategory.EMAIL,
                system_prompt=(
                    "You are an email systems specialist. Analyze email delivery "
                    "incidents and provide resolution steps. Respond ONLY with JSON."
                ),
                llm=self.llm,
            ),
            IncidentCategory.OTHER: IncidentHandler(
                name="General Specialist",
                category=IncidentCategory.OTHER,
                system_prompt=(
                    "You are a general incident response specialist. Provide initial "
                    "triage and recommendations. Respond ONLY with JSON."
                ),
                llm=self.llm,
            ),
        }

    def _match_category(self, raw: str) -> IncidentCategory:
        """Normalize a free-text category string to an IncidentCategory enum value.

        Algorithm:
        1. Lowercase and strip whitespace
        2. Try exact match against enum values
        3. Check for substring matches: database, network, billing/payment, email
        4. Default to OTHER
        """
        normalized = raw.lower().strip()

        # Exact match against enum values
        for cat in IncidentCategory:
            if normalized == cat.value:
                return cat

        # Substring matching
        if "database" in normalized:
            return IncidentCategory.DATABASE
        if "network" in normalized:
            return IncidentCategory.NETWORK
        if "billing" in normalized or "payment" in normalized:
            return IncidentCategory.BILLING
        if "email" in normalized:
            return IncidentCategory.EMAIL

        return IncidentCategory.OTHER

    async def classify(self, incident: dict) -> RouteResult:
        """Classify an incident into a category using the LLM.

        TODO: Implement incident classification.
            # 1. Build list of valid categories from IncidentCategory enum
            # 2. Construct prompt with incident title, description, severity
            # 3. Ask LLM to classify — request JSON with: category, confidence (0-1), reasoning
            # 4. Parse response, match category using self._match_category()
            # 5. Look up handler from self.handlers (fallback to self.fallback_handler)
            # 6. Return RouteResult with category, confidence, reasoning, handler_name
        """
        raise NotImplementedError("Implement classify — see pseudocode above")

    async def route(self, incident: dict) -> tuple[RouteResult, HandlerResponse]:
        """Classify an incident and route to the appropriate handler.

        TODO: Implement routing logic.
            # 1. Call self.classify(incident) to get RouteResult
            # 2. If confidence >= self.confidence_threshold, select matching handler
            # 3. If confidence < threshold, use self.fallback_handler
            # 4. Call handler.handle(incident) to get HandlerResponse
            # 5. Return (RouteResult, HandlerResponse)
        """
        raise NotImplementedError("Implement route — see pseudocode above")
