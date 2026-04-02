/**
 * Test suite for AgentForge patterns.
 *
 * All tests use CachedLLMClient for deterministic, offline testing.
 * Tests will FAIL until students implement the patterns.
 * Once implemented, all 18 tests should pass.
 */

import { describe, it, expect, beforeAll } from 'vitest';
import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { CachedLLMClient } from '../patterns/llm_client.js';
import { DiagnosticChain, createChainState } from '../patterns/chain.js';
import { IncidentRouter, IncidentCategory, handleIncident } from '../patterns/router.js';
import { ParallelHealthChecker } from '../patterns/parallel.js';
import { IncidentOrchestrator } from '../patterns/orchestrator.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// ── Shared Setup ───────────────────────────────────────────────────────────

const cachePath = join(__dirname, '..', '..', 'data', 'cached_responses.json');
const incidentsPath = join(__dirname, '..', '..', 'data', 'incidents.json');

let llm;
let incidents;
let chain;
let router;
let healthChecker;
let orchestrator;

beforeAll(() => {
  llm = new CachedLLMClient(cachePath);
  const raw = JSON.parse(readFileSync(incidentsPath, 'utf-8'));
  incidents = {};
  for (const inc of raw) {
    incidents[inc.id] = inc;
  }
  chain = new DiagnosticChain(llm);
  router = new IncidentRouter(llm);
  healthChecker = new ParallelHealthChecker(llm);
  orchestrator = new IncidentOrchestrator(router, healthChecker, chain);
});

// ── DiagnosticChain (3 tests) ──────────────────────────────────────────────

describe('DiagnosticChain', () => {
  it('has three steps', () => {
    expect(chain.steps).toHaveLength(3);
  });

  it('execute populates state with all results', async () => {
    const state = createChainState(incidents['INC-001']);
    const result = await chain.execute(state);
    expect(result.results).toHaveProperty('parsed_logs');
    expect(result.results).toHaveProperty('root_cause');
    expect(result.results).toHaveProperty('recommendations');
  });

  it('tracks completed steps', async () => {
    const state = createChainState(incidents['INC-001']);
    const result = await chain.execute(state);
    expect(result.stepsCompleted).toHaveLength(3);
  });
});

// ── IncidentRouter (6 tests) ───────────────────────────────────────────────

describe('IncidentRouter', () => {
  it('classifies database incident', async () => {
    const result = await router.classify(incidents['INC-001']);
    expect(result.category).toBe(IncidentCategory.DATABASE);
  });

  it('classifies billing incident', async () => {
    const result = await router.classify(incidents['INC-002']);
    expect(result.category).toBe(IncidentCategory.BILLING);
  });

  it('classifies network incident', async () => {
    const result = await router.classify(incidents['INC-003']);
    expect(result.category).toBe(IncidentCategory.NETWORK);
  });

  it('route returns object with routeResult and handlerResponse', async () => {
    const result = await router.route(incidents['INC-001']);
    expect(result).toHaveProperty('routeResult');
    expect(result).toHaveProperty('handlerResponse');
    expect(result.routeResult).toHaveProperty('category');
    expect(result.handlerResponse).toHaveProperty('handler');
  });

  it('route selects correct handler', async () => {
    const result = await router.route(incidents['INC-001']);
    expect(result.routeResult.handlerName).toContain('Database');
  });

  it('low confidence uses fallback handler', async () => {
    const strictRouter = new IncidentRouter(llm, { confidenceThreshold: 0.99 });
    const result = await strictRouter.route(incidents['INC-001']);
    expect(result.routeResult.handlerName).toContain('General');
  });
});

// ── ParallelHealthChecker (4 tests) ────────────────────────────────────────

describe('ParallelHealthChecker', () => {
  it('has four checks', () => {
    expect(healthChecker.checks).toHaveLength(4);
  });

  it('runAllChecks returns health report with 4 results', async () => {
    const report = await healthChecker.runAllChecks(incidents['INC-001']);
    expect(report).toHaveProperty('results');
    expect(report.results).toHaveLength(4);
    expect(report).toHaveProperty('overallStatus');
  });

  it('aggregate returns critical when any result is critical', () => {
    const results = [
      { name: 'Memory', subsystem: 'memory', status: 'healthy', details: 'OK', durationMs: 1 },
      { name: 'CPU', subsystem: 'cpu', status: 'healthy', details: 'OK', durationMs: 1 },
      { name: 'Disk', subsystem: 'disk', status: 'critical', details: 'Full', durationMs: 1 },
      { name: 'Network', subsystem: 'network', status: 'warning', details: 'Slow', durationMs: 1 },
    ];
    const report = healthChecker.aggregate(results, 10);
    expect(report.overallStatus).toBe('critical');
  });

  it('aggregate returns healthy when all results are healthy', () => {
    const results = [
      { name: 'Memory', subsystem: 'memory', status: 'healthy', details: 'OK', durationMs: 1 },
      { name: 'CPU', subsystem: 'cpu', status: 'healthy', details: 'OK', durationMs: 1 },
      { name: 'Disk', subsystem: 'disk', status: 'healthy', details: 'OK', durationMs: 1 },
      { name: 'Network', subsystem: 'network', status: 'healthy', details: 'OK', durationMs: 1 },
    ];
    const report = healthChecker.aggregate(results, 10);
    expect(report.overallStatus).toBe('healthy');
  });
});

// ── IncidentOrchestrator (5 tests) ─────────────────────────────────────────

describe('IncidentOrchestrator', () => {
  it('processIncident returns report', async () => {
    const report = await orchestrator.processIncident(incidents['INC-001']);
    expect(report).toHaveProperty('incidentId');
    expect(report.incidentId).toBe('INC-001');
  });

  it('report has classification', async () => {
    const report = await orchestrator.processIncident(incidents['INC-001']);
    expect(report.classification).toBeTruthy();
    expect(report.classification).toHaveProperty('category');
  });

  it('report has health report', async () => {
    const report = await orchestrator.processIncident(incidents['INC-001']);
    expect(report.healthReport).toBeTruthy();
  });

  it('report has diagnostic chain', async () => {
    const report = await orchestrator.processIncident(incidents['INC-001']);
    expect(report.diagnosticChain).toBeTruthy();
    expect(Object.keys(report.diagnosticChain).length).toBeGreaterThan(0);
  });

  it('report tracks stages including complete', async () => {
    const report = await orchestrator.processIncident(incidents['INC-001']);
    expect(report.stagesCompleted).toContain('complete');
  });
});
