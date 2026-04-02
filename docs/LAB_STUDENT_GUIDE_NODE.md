# Lab 2: Core Agentic Patterns — Student Guide (Node.js Track)

## CGSE-Advanced | Module 2 | Estimated Time: 110 minutes

---

## 🎯 What You're Building

**AgentForge** is an AI-powered incident response system demonstrating four core
agentic design patterns. Your system will route, chain, parallelize, and orchestrate
using a local LLM (Qwen3.5:4b via Ollama) — no API keys, no cloud, no cost.

---

## 📋 Prerequisites

- [ ] Ollama installed and running (`ollama serve`)
- [ ] Qwen3.5:4b pulled (`ollama pull qwen3.5:4b`)
- [ ] Node.js 20+ installed
- [ ] npm dependencies installed (`npm install`)

```bash
npm run verify   # Should show "All checks passed"
```

---

## 📁 Project Structure

```
agentforge-node/
├── agent_forge.js              ← Main entry point (provided)
├── package.json                ← Dependencies (provided)
├── .env                        ← Configuration (provided)
├── data/
│   ├── incidents.json          ← Sample incidents (provided)
│   └── cached_responses.json   ← Offline fallback (provided)
├── patterns/
│   ├── llm_client.js           ← Ollama wrapper (DO NOT MODIFY)
│   ├── chain.js                ← 🔨 YOU IMPLEMENT: execute()
│   ├── router.js               ← 🔨 YOU IMPLEMENT: classify() + route()
│   ├── parallel.js             ← 🔨 YOU IMPLEMENT: runAllChecks() + aggregate()
│   └── orchestrator.js         ← 🔨 YOU IMPLEMENT: processIncident()
├── tests/
│   └── patterns.test.js        ← Test suite (provided)
└── report.md                   ← Your reflection (you write)
```

---

## Phase 1: Environment Setup (20 minutes)

```bash
cd agentforge-node
npm install
npm run verify
```

Familiarize yourself with `patterns/llm_client.js`. The `LLMClient.chat()` method returns:
- `.content` — Raw text response
- `.asJson()` — Parsed JSON (throws if invalid)
- `.durationMs` — Response time in ms

---

## Phase 2: Build the Sequential Chain (15 minutes)

Open `patterns/chain.js`. The `CHAIN_STEPS` array defines 3 steps (Parse Logs →
Analyze Root Cause → Recommend). Implement `execute()`:

```javascript
async execute(state) {
  for (const step of this.steps) {
    console.log(chalk.cyan(`  ⏳ ${step.name}...`));

    try {
      // 1. Build prompt from template
      const prompt = step.promptTemplate(state);

      // 2. Call the LLM
      const response = await this.llm.chat(prompt, {
        system: step.systemPrompt,
      });

      // 3. Parse JSON response
      const result = response.asJson();

      // 4. Store in state
      state.results[step.outputKey] = result;
      state.stepsCompleted.push(step.name);

      console.log(
        chalk.green(`  ✓ ${step.name}`) +
        chalk.dim(` (${response.durationMs.toFixed(0)}ms)`)
      );
    } catch (err) {
      const msg = `${step.name} failed: ${err.message?.slice(0, 100)}`;
      state.errors.push(msg);
      console.log(chalk.red(`  ✗ ${msg}`));
    }
  }

  return state;
}
```

**Test:**
```bash
npx vitest run --reporter=verbose -- DiagnosticChain
```

---

## Phase 3: Build the Router (15 minutes)

Open `patterns/router.js`. Implement `classify()` and `route()`.

### 3.1 Implement `classify()`

```javascript
async classify(incident) {
  const categories = Object.values(IncidentCategory).join(', ');

  const prompt =
    `Classify this incident into one of these categories: ${categories}\n\n` +
    `Title: ${incident.title || 'N/A'}\n` +
    `Description: ${incident.description || 'N/A'}\n` +
    `Severity: ${incident.severity || 'unknown'}\n\n` +
    `Respond with ONLY this JSON:\n` +
    `{\n` +
    `  "category": "<one of the categories above>",\n` +
    `  "confidence": <0.0 to 1.0>,\n` +
    `  "reasoning": "<one sentence>"\n` +
    `}`;

  const response = await this.llm.chat(prompt, {
    system: 'You are an incident classification expert. Respond ONLY with JSON.',
  });

  const data = response.asJson();
  const category = matchCategory(data.category || '');
  const handler = this.handlers[category] || this.fallbackHandler;

  return {
    category,
    confidence: parseFloat(data.confidence) || 0.5,
    reasoning: data.reasoning || 'No reasoning provided',
    handlerName: handler.name,
  };
}
```

### 3.2 Implement `route()`

```javascript
async route(incident) {
  // 1. Classify
  const routeResult = await this.classify(incident);

  console.log(
    chalk.cyan(`  🎯 Classified: ${routeResult.category}`) +
    chalk.dim(` (${(routeResult.confidence * 100).toFixed(0)}%)`)
  );

  // 2. Select handler
  let handler;
  if (routeResult.confidence >= this.confidenceThreshold) {
    handler = this.handlers[routeResult.category] || this.fallbackHandler;
  } else {
    console.log(chalk.yellow(`  ⚠ Low confidence, using fallback`));
    handler = this.fallbackHandler;
    routeResult.handlerName = handler.name;
  }

  // 3. Delegate
  console.log(chalk.cyan(`  🔀 Routing to: ${handler.name}`));
  const handlerResponse = await handleIncident(this.llm, handler, incident);

  return [routeResult, handlerResponse];
}
```

> Note: `handleIncident` is already defined at the module level — just call it.

**Test:**
```bash
npx vitest run --reporter=verbose -- IncidentRouter
```

---

## Phase 4: Build the Parallel Health Checker (15 minutes)

Open `patterns/parallel.js`. Implement `runAllChecks()` and `aggregate()`.

### 4.1 Implement `runAllChecks()`

```javascript
async runAllChecks(incident) {
  console.log(chalk.cyan('  🔄 Running parallel health checks...'));

  const start = performance.now();

  // 1. Create a promise for each check
  const promises = this.checks.map(check =>
    runSingleCheck(this.llm, check, incident)
  );

  // 2. Run ALL concurrently
  const settled = await Promise.allSettled(promises);

  const totalMs = performance.now() - start;

  // 3. Extract results
  const results = settled.map((outcome, i) => {
    if (outcome.status === 'fulfilled') {
      return outcome.value;
    }
    return {
      name: this.checks[i].name,
      subsystem: this.checks[i].subsystem,
      status: 'error',
      details: `Exception: ${outcome.reason?.message?.slice(0, 80)}`,
      durationMs: 0,
    };
  });

  // 4. Display
  for (const r of results) {
    const icons = { healthy: chalk.green('✓'), warning: chalk.yellow('⚠'), critical: chalk.red('✗'), error: chalk.red('!') };
    const icon = icons[r.status] || '?';
    console.log(`    ${icon} ${r.name.padEnd(20)} ${chalk.dim((r.details || '').slice(0, 50) + '  ' + r.durationMs.toFixed(0) + 'ms')}`);
  }

  return this.aggregate(results, totalMs);
}
```

### 4.2 Implement `aggregate()`

```javascript
aggregate(results, totalMs) {
  const statuses = results.map(r => r.status);

  let overallStatus;
  if (statuses.includes('critical')) overallStatus = 'critical';
  else if (statuses.includes('error')) overallStatus = 'error';
  else if (statuses.includes('warning')) overallStatus = 'warning';
  else overallStatus = 'healthy';

  const summary = results.map(r => `${r.subsystem}: ${r.status}`).join(', ');

  console.log(chalk.cyan(`  📊 Health: ${chalk.bold(overallStatus.toUpperCase())} (${totalMs.toFixed(0)}ms total)`));

  return {
    results,
    overallStatus,
    totalDurationMs: Math.round(totalMs * 10) / 10,
    summary: `Overall: ${overallStatus} | ${summary}`,
  };
}
```

**Key concept:** `Promise.allSettled()` is the JavaScript equivalent of Python's
`asyncio.gather(return_exceptions=True)`. It never rejects — every promise gets
a `{status, value}` or `{status, reason}` result.

**Test:**
```bash
npx vitest run --reporter=verbose -- ParallelHealthChecker
```

---

## Phase 5: Build the Orchestrator (15 minutes)

Open `patterns/orchestrator.js`. Implement `processIncident()`:

```javascript
async processIncident(incident) {
  const start = performance.now();
  const stagesCompleted = [];
  const errors = [];

  let classification = {};
  let handlerResponseData = {};
  let healthReport = {};
  let diagnosticResults = {};

  // ── Stage 1: Classify & Route ──
  console.log(chalk.bold('\n  Stage 1: Classification & Routing'));
  try {
    const [routeResult, handlerResponse] = await this.router.route(incident);
    classification = {
      category: routeResult.category,
      confidence: routeResult.confidence,
      reasoning: routeResult.reasoning,
      handler: routeResult.handlerName,
    };
    handlerResponseData = {
      handler: handlerResponse.handler,
      summary: handlerResponse.summary,
      priority: handlerResponse.priority,
      escalationNeeded: handlerResponse.escalationNeeded,
    };
    stagesCompleted.push('classifying');
  } catch (err) {
    errors.push(`Classification failed: ${err.message?.slice(0, 100)}`);
    console.log(chalk.red(`  ✗ Classification failed: ${err.message}`));
  }

  // ── Stage 2: Parallel Health Checks ──
  console.log(chalk.bold('\n  Stage 2: Health Checks'));
  try {
    const health = await this.healthChecker.runAllChecks(incident);
    healthReport = health;
    stagesCompleted.push('health_check');
  } catch (err) {
    errors.push(`Health checks failed: ${err.message?.slice(0, 100)}`);
    console.log(chalk.red(`  ✗ Health checks failed: ${err.message}`));
  }

  // ── Stage 3: Diagnostic Chain ──
  console.log(chalk.bold('\n  Stage 3: Diagnostic Chain'));
  try {
    const { createChainState } = await import('./chain.js');
    const state = createChainState(incident);
    const result = await this.diagnosticChain.execute(state);
    diagnosticResults = result.results;
    stagesCompleted.push('diagnosing');
    if (result.errors.length > 0) errors.push(...result.errors);
  } catch (err) {
    errors.push(`Chain failed: ${err.message?.slice(0, 100)}`);
    console.log(chalk.red(`  ✗ Chain failed: ${err.message}`));
  }

  // ── Stage 4: Compile Report ──
  stagesCompleted.push('complete');
  const totalDurationMs = performance.now() - start;

  const report = {
    incidentId: incident.id,
    title: incident.title || 'Unknown',
    classification,
    handlerResponse: handlerResponseData,
    healthReport,
    diagnosticChain: diagnosticResults,
    totalDurationMs: Math.round(totalDurationMs * 10) / 10,
    stagesCompleted,
    errors,
  };

  this.displayReport(report);
  return report;
}
```

**Test everything:**
```bash
npx vitest run
```

---

## Phase 6: Run & Experiment (10 minutes)

```bash
# Process all incidents
npm start

# Single incident
node agent_forge.js --incident INC-001

# Offline mode
npm run start:cached
```

Try changing `MODEL_TEMPERATURE` in `.env` and observe the differences.

---

## Phase 7: Submit (10 minutes)

```bash
npx vitest run   # All tests should pass
```

Write your reflection in `report.md` (same template as Python guide), then submit:
```bash
git add -A
git commit -m "feat: complete Module 2 lab - all 4 agentic patterns (Node.js)"
git push origin main
```

---

## 🏆 Bonus Challenges

1. **Add Retry Logic** — Retry failed JSON parsing 3 times with lower temperature
2. **Severity Scorer** — Add a 4th chain step that scores severity 1-10
3. **Timeout with AbortController** — 10s timeout per LLM call with fallback
4. **Token Cost Tracker** — Sum tokens across all calls, print cost report
5. **Swap Model** — Try `qwen3:4b` or `gemma3:4b` and compare results

---

## 🔑 Success Criteria

| Criteria | Points |
|----------|--------|
| Chain `execute()` works correctly | 20 |
| Router `classify()` returns accurate categories | 15 |
| Router `route()` handles confidence thresholds | 10 |
| Parallel `runAllChecks()` runs concurrently | 15 |
| Parallel `aggregate()` determines correct status | 10 |
| Orchestrator `processIncident()` runs full pipeline | 20 |
| All tests pass | 10 |
| **Total** | **100** |
