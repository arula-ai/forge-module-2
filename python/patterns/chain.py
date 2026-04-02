"""
Sequential Chain Pattern — Diagnostic analysis pipeline.

The DiagnosticChain runs a series of LLM calls in sequence, where each step
builds on the results of the previous one:
  1. Parse Logs → extract structured error data
  2. Analyze Root Cause → determine what went wrong
  3. Generate Recommendations → suggest fixes

Students: Implement the execute() method. Everything else is provided.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field

from rich.console import Console

from .llm_client import LLMClient

console = Console()


@dataclass
class ChainState:
    """Mutable state passed through each step of the chain."""

    incident_id: str
    raw_input: str
    logs: str
    results: dict = field(default_factory=dict)
    steps_completed: list = field(default_factory=list)
    errors: list = field(default_factory=list)


@dataclass
class ChainStep:
    """Definition of a single step in the chain."""

    name: str
    system_prompt: str
    user_prompt_template: str
    output_key: str


class DiagnosticChain:
    """Runs a sequential chain of LLM calls for incident diagnosis."""

    def __init__(self, llm: LLMClient):
        self.llm = llm
        self.steps = self._build_steps()

    def _build_steps(self) -> list[ChainStep]:
        """Define the 3 diagnostic chain steps."""
        return [
            ChainStep(
                name="Parse Logs",
                system_prompt=(
                    "You are a log analysis expert. Extract structured data "
                    "from logs. Respond ONLY with JSON."
                ),
                user_prompt_template=(
                    "Parse the following incident logs and extract key information.\n\n"
                    "Logs:\n{logs}\n\n"
                    "Respond with ONLY this JSON:\n"
                    '{{\n'
                    '  "errors_found": <number>,\n'
                    '  "error_types": ["<type1>", "<type2>"],\n'
                    '  "time_range": "<start> - <end>",\n'
                    '  "affected_services": ["<service1>", "<service2>"]\n'
                    '}}'
                ),
                output_key="parsed_logs",
            ),
            ChainStep(
                name="Analyze Root Cause",
                system_prompt=(
                    "You are a root cause analysis expert. "
                    "Respond ONLY with JSON."
                ),
                user_prompt_template=(
                    "Based on the parsed log data, analyze the root cause of this incident.\n\n"
                    "Parsed Logs:\n{parsed_logs}\n\n"
                    "Respond with ONLY this JSON:\n"
                    '{{\n'
                    '  "root_cause": "<description of the root cause>",\n'
                    '  "impact": "<description of the impact>",\n'
                    '  "severity_assessment": "<HIGH/MEDIUM/LOW — explanation>"\n'
                    '}}'
                ),
                output_key="root_cause",
            ),
            ChainStep(
                name="Generate Recommendations",
                system_prompt=(
                    "You are a DevOps remediation expert. "
                    "Respond ONLY with JSON."
                ),
                user_prompt_template=(
                    "Based on the root cause analysis, recommend actions to resolve "
                    "and prevent this incident.\n\n"
                    "Root Cause Analysis:\n{root_cause}\n\n"
                    "Respond with ONLY this JSON:\n"
                    '{{\n'
                    '  "immediate_actions": ["<action1>", "<action2>"],\n'
                    '  "investigation_steps": ["<step1>", "<step2>"],\n'
                    '  "prevention": ["<measure1>", "<measure2>"]\n'
                    '}}'
                ),
                output_key="recommendations",
            ),
        ]

    def _format_prompt(self, template: str, state: ChainState) -> str:
        """Interpolate state values into a prompt template."""
        format_values = {
            "incident_id": state.incident_id,
            "raw_input": state.raw_input,
            "logs": state.logs,
        }
        for key, value in state.results.items():
            format_values[key] = json.dumps(value, indent=2) if isinstance(value, (dict, list)) else str(value)
        return template.format_map(format_values)

    async def execute(self, state: ChainState) -> ChainState:
        """Execute the diagnostic chain: run each step sequentially, passing state through.

        TODO: Implement the chain execution loop.
        For each step in self.steps:
            # 1. Build the prompt using self._format_prompt(step.user_prompt_template, state)
            # 2. Call the LLM: await self.llm.chat(prompt, system=step.system_prompt)
            # 3. Parse the JSON response using response.as_json()
            # 4. Store the result in state.results[step.output_key]
            # 5. Track completion: state.steps_completed.append(step.name)
            # 6. Handle errors: append to state.errors, log, but don't crash the loop
        """
        raise NotImplementedError("Implement the chain execution loop — see pseudocode above")


def create_chain_state(incident: dict) -> ChainState:
    """Create a ChainState from an incident dict."""
    return ChainState(
        incident_id=incident["id"],
        raw_input=json.dumps(incident),
        logs=incident.get("logs", ""),
    )
