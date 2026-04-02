#!/usr/bin/env python3
"""
AgentForge — Incident Response System (Python Track)

Main entry point. Students do NOT modify this file.

Usage:
    python agent_forge.py                    # Process all incidents
    python agent_forge.py --incident INC-001 # Process single incident
    python agent_forge.py --cached           # Use cached responses (offline mode)
"""

import argparse
import asyncio
import json
import time
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

from patterns.llm_client import create_llm_client
from patterns.chain import DiagnosticChain
from patterns.router import IncidentRouter
from patterns.parallel import ParallelHealthChecker
from patterns.orchestrator import IncidentOrchestrator

console = Console()


def load_incidents() -> list[dict]:
    """Load incidents from the shared data directory."""
    incidents_path = Path(__file__).parent.parent / "data" / "incidents.json"
    with open(incidents_path) as f:
        return json.load(f)


async def main():
    parser = argparse.ArgumentParser(description="AgentForge — Incident Response System")
    parser.add_argument("--incident", type=str, help="Process a specific incident by ID (e.g., INC-001)")
    parser.add_argument("--cached", action="store_true", help="Use cached LLM responses (offline mode)")
    args = parser.parse_args()

    load_dotenv()

    # Banner
    console.print(Panel(
        "[bold cyan]AgentForge — Incident Response System[/bold cyan]\n"
        "[dim]Module 2: Core Agentic Patterns[/dim]",
        border_style="cyan",
    ))

    # Load incidents
    incidents = load_incidents()

    if args.incident:
        filtered = [inc for inc in incidents if inc["id"] == args.incident]
        if not filtered:
            console.print(f"[red]Error: Incident '{args.incident}' not found.[/red]")
            console.print(f"[dim]Available: {', '.join(inc['id'] for inc in incidents)}[/dim]")
            return
        incidents = filtered

    # Create LLM client
    llm = create_llm_client(cached=args.cached)
    mode = "cached" if args.cached else "live"
    console.print(f"[dim]Mode: {mode} | Incidents: {len(incidents)}[/dim]\n")

    # Wire up patterns
    chain = DiagnosticChain(llm)
    router = IncidentRouter(llm)
    checker = ParallelHealthChecker(llm)
    orchestrator = IncidentOrchestrator(router, checker, chain)

    # Process incidents
    start = time.perf_counter()
    results = []
    errors = []

    for incident in incidents:
        console.print(f"\n[bold]{'='*60}[/bold]")
        console.print(f"[bold cyan]Processing: {incident['id']} — {incident['title']}[/bold cyan]")
        console.print(f"[dim]Severity: {incident['severity']} | Source: {incident['source']}[/dim]")

        try:
            report = await orchestrator.process_incident(incident)
            results.append(report)
        except Exception as e:
            console.print(f"[red]Failed to process {incident['id']}: {e}[/red]")
            errors.append(f"{incident['id']}: {str(e)[:100]}")

    total_ms = (time.perf_counter() - start) * 1000

    # Summary
    console.print(f"\n[bold]{'='*60}[/bold]")
    console.print(Panel(
        f"[bold]Incidents processed:[/bold] {len(results)}/{len(incidents)}\n"
        f"[bold]Total time:[/bold] {total_ms:.0f}ms\n"
        f"[bold]Errors:[/bold] {len(errors)}",
        title="[bold cyan]Session Summary[/bold cyan]",
        border_style="green" if not errors else "yellow",
    ))

    if errors:
        for err in errors:
            console.print(f"  [red]• {err}[/red]")


if __name__ == "__main__":
    asyncio.run(main())
