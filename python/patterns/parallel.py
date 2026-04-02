"""
Parallel Fan-Out Pattern — Run multiple health checks concurrently.

The ParallelHealthChecker fans out 4 independent health checks in parallel
and aggregates results into an overall health report:
  - Memory Analysis
  - CPU Analysis
  - Disk I/O Analysis
  - Network Analysis

Students: Implement run_all_checks() and _aggregate(). Everything else is provided.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

from rich.console import Console

from .llm_client import LLMClient

console = Console()


@dataclass
class HealthCheck:
    """Definition of a single health check."""

    name: str
    subsystem: str
    prompt_template: str


@dataclass
class CheckResult:
    """Result from a single health check."""

    name: str
    subsystem: str
    status: str
    details: str
    duration_ms: float


@dataclass
class HealthReport:
    """Aggregated report from all health checks."""

    results: list[CheckResult]
    overall_status: str
    total_duration_ms: float
    summary: str


class ParallelHealthChecker:
    """Runs multiple health checks concurrently against the LLM."""

    def __init__(self, llm: LLMClient):
        self.llm = llm
        self.checks = self._build_checks()

    def _build_checks(self) -> list[HealthCheck]:
        """Define the 4 parallel health checks."""
        return [
            HealthCheck(
                name="Memory Analysis",
                subsystem="memory",
                prompt_template=(
                    "Assess the memory health status for this incident.\n\n"
                    "Incident: {title}\n"
                    "Description: {description}\n\n"
                    "Check the memory utilization and report any concerns.\n"
                    'Respond with ONLY this JSON:\n'
                    '{{\n'
                    '  "status": "healthy|warning|critical",\n'
                    '  "usage_percent": <number>,\n'
                    '  "details": "<description>"\n'
                    '}}'
                ),
            ),
            HealthCheck(
                name="CPU Analysis",
                subsystem="cpu",
                prompt_template=(
                    "Assess the cpu health status for this incident.\n\n"
                    "Incident: {title}\n"
                    "Description: {description}\n\n"
                    "Check the CPU utilization and report any concerns.\n"
                    'Respond with ONLY this JSON:\n'
                    '{{\n'
                    '  "status": "healthy|warning|critical",\n'
                    '  "usage_percent": <number>,\n'
                    '  "details": "<description>"\n'
                    '}}'
                ),
            ),
            HealthCheck(
                name="Disk I/O Analysis",
                subsystem="disk",
                prompt_template=(
                    "Assess the disk health status for this incident.\n\n"
                    "Incident: {title}\n"
                    "Description: {description}\n\n"
                    "Check the disk I/O and storage utilization.\n"
                    'Respond with ONLY this JSON:\n'
                    '{{\n'
                    '  "status": "healthy|warning|critical",\n'
                    '  "usage_percent": <number>,\n'
                    '  "details": "<description>"\n'
                    '}}'
                ),
            ),
            HealthCheck(
                name="Network Analysis",
                subsystem="network",
                prompt_template=(
                    "Assess the network health status for this incident.\n\n"
                    "Incident: {title}\n"
                    "Description: {description}\n\n"
                    "Check the network connectivity and report any concerns.\n"
                    'Respond with ONLY this JSON:\n'
                    '{{\n'
                    '  "status": "healthy|warning|critical",\n'
                    '  "details": "<description>"\n'
                    '}}'
                ),
            ),
        ]

    async def _run_single_check(self, check: HealthCheck, incident: dict) -> CheckResult:
        """Run a single health check against the LLM."""
        prompt = check.prompt_template.format(
            title=incident.get("title", "N/A"),
            description=incident.get("description", "N/A"),
        )

        start = time.perf_counter()
        response = await self.llm.chat(
            prompt,
            system=(
                "You are a system health check analyzer. Assess the health status "
                "of the specified subsystem. Respond ONLY with JSON."
            ),
        )
        duration_ms = (time.perf_counter() - start) * 1000

        data = response.as_json()
        return CheckResult(
            name=check.name,
            subsystem=check.subsystem,
            status=data.get("status", "unknown"),
            details=data.get("details", "No details available"),
            duration_ms=round(duration_ms, 1),
        )

    async def run_all_checks(self, incident: dict) -> HealthReport:
        """Run all health checks concurrently and return aggregated report.

        TODO: Implement parallel health check execution.
            # 1. Create a coroutine for each check: self._run_single_check(check, incident)
            # 2. Run ALL concurrently with asyncio.gather(*tasks, return_exceptions=True)
            # 3. Process results: if an item is an Exception, convert to CheckResult with status="error"
            # 4. Display results with status icons (green checkmark healthy, yellow warning, red X critical, ! error)
            # 5. Return self._aggregate(results, total_ms)
        """
        raise NotImplementedError("Implement run_all_checks — see pseudocode above")

    def _aggregate(self, results: list[CheckResult], total_ms: float) -> HealthReport:
        """Aggregate individual check results into an overall health report.

        TODO: Implement result aggregation.
            # 1. Collect all statuses from results
            # 2. Determine overall status (priority: critical > error > warning > healthy)
            # 3. Build summary string: "Overall: <status> | memory: <s>, cpu: <s>, ..."
            # 4. Return HealthReport with results, overall_status, total_duration_ms, summary
        """
        raise NotImplementedError("Implement _aggregate — see pseudocode above")
