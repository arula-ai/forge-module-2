"""
Test suite for AgentForge patterns.

All tests use CachedLLMClient for deterministic, offline testing.
Tests will FAIL with NotImplementedError until students implement the patterns.
Once implemented, all 20 tests should pass.
"""

import json
from pathlib import Path

import pytest
import pytest_asyncio

from patterns.llm_client import CachedLLMClient
from patterns.chain import DiagnosticChain, ChainState, ChainStep, create_chain_state
from patterns.router import IncidentRouter, IncidentCategory, RouteResult, HandlerResponse
from patterns.parallel import ParallelHealthChecker, CheckResult, HealthReport
from patterns.orchestrator import IncidentOrchestrator, IncidentReport


# ── Fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture
def cached_llm():
    cache_path = Path(__file__).parent.parent.parent / "data" / "cached_responses.json"
    return CachedLLMClient(str(cache_path))


@pytest.fixture
def incidents():
    incidents_path = Path(__file__).parent.parent.parent / "data" / "incidents.json"
    with open(incidents_path) as f:
        data = json.load(f)
    return {inc["id"]: inc for inc in data}


@pytest.fixture
def chain(cached_llm):
    return DiagnosticChain(cached_llm)


@pytest.fixture
def router(cached_llm):
    return IncidentRouter(cached_llm)


@pytest.fixture
def health_checker(cached_llm):
    return ParallelHealthChecker(cached_llm)


@pytest.fixture
def orchestrator(router, health_checker, chain):
    return IncidentOrchestrator(router, health_checker, chain)


# ── TestDiagnosticChain (4 tests) ──────────────────────────────────────────


class TestDiagnosticChain:

    def test_chain_has_three_steps(self, chain):
        assert len(chain.steps) == 3

    @pytest.mark.asyncio
    async def test_chain_execute_populates_state(self, chain, incidents):
        state = create_chain_state(incidents["INC-001"])
        state = await chain.execute(state)
        assert "parsed_logs" in state.results
        assert "root_cause" in state.results
        assert "recommendations" in state.results

    @pytest.mark.asyncio
    async def test_chain_tracks_completed_steps(self, chain, incidents):
        state = create_chain_state(incidents["INC-001"])
        state = await chain.execute(state)
        assert len(state.steps_completed) == 3

    @pytest.mark.asyncio
    async def test_chain_handles_errors_gracefully(self, cached_llm, incidents):
        chain = DiagnosticChain(cached_llm)
        # Replace one step's prompt template to cause a KeyError in format_prompt
        chain.steps[1] = ChainStep(
            name="Bad Step",
            system_prompt="test",
            user_prompt_template="{nonexistent_key}",
            output_key="bad_result",
        )
        state = create_chain_state(incidents["INC-001"])
        state = await chain.execute(state)
        assert len(state.errors) > 0


# ── TestIncidentRouter (7 tests) ───────────────────────────────────────────


class TestIncidentRouter:

    @pytest.mark.asyncio
    async def test_classify_database_incident(self, router, incidents):
        result = await router.classify(incidents["INC-001"])
        assert result.category == IncidentCategory.DATABASE

    @pytest.mark.asyncio
    async def test_classify_billing_incident(self, router, incidents):
        result = await router.classify(incidents["INC-002"])
        assert result.category == IncidentCategory.BILLING

    @pytest.mark.asyncio
    async def test_classify_network_incident(self, router, incidents):
        result = await router.classify(incidents["INC-003"])
        assert result.category == IncidentCategory.NETWORK

    @pytest.mark.asyncio
    async def test_classify_returns_confidence(self, router, incidents):
        result = await router.classify(incidents["INC-001"])
        assert 0.0 <= result.confidence <= 1.0

    @pytest.mark.asyncio
    async def test_route_returns_tuple(self, router, incidents):
        result = await router.route(incidents["INC-001"])
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], RouteResult)
        assert isinstance(result[1], HandlerResponse)

    @pytest.mark.asyncio
    async def test_route_selects_correct_handler(self, router, incidents):
        route_result, handler_response = await router.route(incidents["INC-001"])
        assert "Database" in route_result.handler_name

    @pytest.mark.asyncio
    async def test_low_confidence_uses_fallback(self, cached_llm, incidents):
        router = IncidentRouter(cached_llm, confidence_threshold=0.99)
        route_result, handler_response = await router.route(incidents["INC-001"])
        assert "General" in route_result.handler_name


# ── TestParallelHealthChecker (4 tests) ────────────────────────────────────


class TestParallelHealthChecker:

    def test_has_four_checks(self, health_checker):
        assert len(health_checker.checks) == 4

    @pytest.mark.asyncio
    async def test_run_all_checks_returns_health_report(self, health_checker, incidents):
        report = await health_checker.run_all_checks(incidents["INC-001"])
        assert isinstance(report, HealthReport)
        assert len(report.results) == 4

    def test_aggregate_critical_status(self, health_checker):
        results = [
            CheckResult(name="Memory", subsystem="memory", status="healthy", details="OK", duration_ms=1.0),
            CheckResult(name="CPU", subsystem="cpu", status="healthy", details="OK", duration_ms=1.0),
            CheckResult(name="Disk", subsystem="disk", status="critical", details="Full", duration_ms=1.0),
            CheckResult(name="Network", subsystem="network", status="warning", details="Slow", duration_ms=1.0),
        ]
        report = health_checker._aggregate(results, 10.0)
        assert report.overall_status == "critical"

    def test_aggregate_healthy_status(self, health_checker):
        results = [
            CheckResult(name="Memory", subsystem="memory", status="healthy", details="OK", duration_ms=1.0),
            CheckResult(name="CPU", subsystem="cpu", status="healthy", details="OK", duration_ms=1.0),
            CheckResult(name="Disk", subsystem="disk", status="healthy", details="OK", duration_ms=1.0),
            CheckResult(name="Network", subsystem="network", status="healthy", details="OK", duration_ms=1.0),
        ]
        report = health_checker._aggregate(results, 10.0)
        assert report.overall_status == "healthy"


# ── TestIncidentOrchestrator (5 tests) ─────────────────────────────────────


class TestIncidentOrchestrator:

    @pytest.mark.asyncio
    async def test_process_incident_returns_report(self, orchestrator, incidents):
        report = await orchestrator.process_incident(incidents["INC-001"])
        assert isinstance(report, IncidentReport)

    @pytest.mark.asyncio
    async def test_report_has_classification(self, orchestrator, incidents):
        report = await orchestrator.process_incident(incidents["INC-001"])
        assert report.classification
        assert "category" in report.classification

    @pytest.mark.asyncio
    async def test_report_has_health_report(self, orchestrator, incidents):
        report = await orchestrator.process_incident(incidents["INC-001"])
        assert report.health_report

    @pytest.mark.asyncio
    async def test_report_has_diagnostic_chain(self, orchestrator, incidents):
        report = await orchestrator.process_incident(incidents["INC-001"])
        assert report.diagnostic_chain

    @pytest.mark.asyncio
    async def test_report_tracks_stages(self, orchestrator, incidents):
        report = await orchestrator.process_incident(incidents["INC-001"])
        assert "complete" in report.stages_completed
