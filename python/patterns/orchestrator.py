"""
Orchestrator Pattern — Compose all patterns into a full incident response pipeline.

The IncidentOrchestrator runs 3 stages in sequence:
  1. Classification & Routing (Router pattern)
  2. Parallel Health Checks (Parallel pattern)
  3. Diagnostic Chain (Chain pattern)

Then compiles an IncidentReport with results from all stages.

Students: Implement process_incident(). Everything else is provided.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from enum import Enum

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .chain import ChainState, DiagnosticChain, create_chain_state
from .parallel import ParallelHealthChecker
from .router import IncidentRouter

console = Console()


class PipelineStage(str, Enum):
    """Stages of the incident response pipeline."""

    CLASSIFYING = "classifying"
    HEALTH_CHECK = "health_check"
    DIAGNOSING = "diagnosing"
    COMPLETE = "complete"


@dataclass
class IncidentReport:
    """Final report from the full incident response pipeline."""

    incident_id: str
    title: str
    classification: dict = field(default_factory=dict)
    handler_response: dict = field(default_factory=dict)
    health_report: dict = field(default_factory=dict)
    diagnostic_chain: dict = field(default_factory=dict)
    total_duration_ms: float = 0.0
    stages_completed: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


class IncidentOrchestrator:
    """Orchestrates the full incident response pipeline."""

    def __init__(
        self,
        router: IncidentRouter,
        health_checker: ParallelHealthChecker,
        diagnostic_chain: DiagnosticChain,
    ):
        self.router = router
        self.health_checker = health_checker
        self.diagnostic_chain = diagnostic_chain

    def _display_report(self, report: IncidentReport) -> None:
        """Render a rich terminal report with panels and tables."""
        console.print()

        # Classification section
        if report.classification:
            cls = report.classification
            console.print(
                f"  [bold cyan]Classification:[/bold cyan] "
                f"{cls.get('category', 'N/A')} "
                f"[dim](confidence: {cls.get('confidence', 0):.0%})[/dim]"
            )
            console.print(
                f"  [cyan]Handler:[/cyan] {cls.get('handler', 'N/A')}"
            )

        # Handler response
        if report.handler_response:
            hr = report.handler_response
            console.print(
                f"  [cyan]Assessment:[/cyan] {hr.get('summary', 'N/A')}"
            )
            console.print(
                f"  [cyan]Priority:[/cyan] {hr.get('priority', 'N/A')} | "
                f"Escalation: {'Yes' if hr.get('escalation_needed') else 'No'}"
            )

        # Health report
        if report.health_report:
            console.print(
                f"\n  [bold cyan]Health Status:[/bold cyan] "
                f"{report.health_report.get('overall_status', 'unknown').upper()}"
            )
            for result in report.health_report.get("results", []):
                icon = {
                    "healthy": "[green]✓[/green]",
                    "warning": "[yellow]⚠[/yellow]",
                    "critical": "[red]✗[/red]",
                    "error": "[red]![/red]",
                }.get(result.get("status", ""), "?")
                console.print(
                    f"    {icon} {result.get('name', '?')}: "
                    f"{result.get('details', 'N/A')[:60]} "
                    f"[dim]({result.get('duration_ms', 0):.0f}ms)[/dim]"
                )

        # Diagnostic chain
        if report.diagnostic_chain:
            console.print(f"\n  [bold cyan]Diagnostics:[/bold cyan]")
            for key, value in report.diagnostic_chain.items():
                if isinstance(value, dict):
                    summary = json.dumps(value, indent=2)[:100]
                elif isinstance(value, list):
                    summary = ", ".join(str(v)[:30] for v in value[:3])
                else:
                    summary = str(value)[:100]
                console.print(f"    [dim]{key}:[/dim] {summary}")

        # Summary
        console.print(
            f"\n  [bold]Total time:[/bold] {report.total_duration_ms:.0f}ms | "
            f"Stages: {len(report.stages_completed)} | "
            f"Errors: {len(report.errors)}"
        )

        if report.errors:
            for err in report.errors:
                console.print(f"  [red]⚠ {err}[/red]")

        title = f"📋 {report.incident_id}: {report.title}"
        panel = Panel(
            f"Pipeline complete — {len(report.stages_completed)} stages",
            title=title,
            border_style="green" if not report.errors else "yellow",
        )
        console.print(panel)

    async def process_incident(self, incident: dict) -> IncidentReport:
        """Run the full incident response pipeline.

        TODO: Implement the orchestration pipeline.
            # Initialize: start timer, empty lists for stages_completed and errors,
            #             empty dicts for classification, handler_response, health_report, chain_results

            # Stage 1: Classification & Routing
            # 1. Call self.router.route(incident)
            # 2. Extract classification dict: category (.value for enum), confidence, reasoning, handler
            # 3. Extract handler_response dict: handler, summary, priority, escalation_needed
            # 4. Append PipelineStage.CLASSIFYING.value to stages_completed
            # 5. Wrap in try/except — on failure, append error, don't stop pipeline

            # Stage 2: Parallel Health Checks
            # 6. Call self.health_checker.run_all_checks(incident)
            # 7. Extract health_report dict with results list and overall_status
            # 8. Append PipelineStage.HEALTH_CHECK.value to stages_completed
            # 9. Wrap in try/except

            # Stage 3: Diagnostic Chain
            # 10. Create ChainState from incident (use create_chain_state from chain module)
            # 11. Call self.diagnostic_chain.execute(state)
            # 12. Extract chain_results from state.results
            # 13. Append PipelineStage.DIAGNOSING.value, merge chain errors
            # 14. Wrap in try/except

            # Stage 4: Compile Report
            # 15. Append PipelineStage.COMPLETE.value
            # 16. Build IncidentReport with all collected data and total_duration_ms
            # 17. Call self._display_report(report)
            # 18. Return report
        """
        raise NotImplementedError("Implement process_incident — see pseudocode above")
