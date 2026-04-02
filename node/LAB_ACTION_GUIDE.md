# Lab Action Guide — Node.js Track

## 1. Setup

```bash
cd node
npm install
cp .env.example .env
node verify_setup.js
```

Expected: "All checks passed. You're ready for the lab!"

If Ollama isn't running, that's OK — you can use `--cached` mode for everything.

---

## 2. Chain Pattern

Open `patterns/chain.js` — find `execute()`.

**Implement the loop:** for each step, build the prompt with `formatPrompt()`, call the LLM, parse JSON with `asJson()`, store in `state.results[step.outputKey]`.

```bash
npx vitest run -t "DiagnosticChain"
```

Expected: **3 tests pass**

---

## 3. Router Pattern

Open `patterns/router.js` — find `classify()` and `route()`.

**classify():** Build a prompt with the incident details and category list. Ask the LLM to return JSON with category, confidence, and reasoning. Use `matchCategory()` to normalize the result.

**route():** Call classify, check confidence against threshold, pick handler or fallback, call `handleIncident()`.

```bash
npx vitest run -t "IncidentRouter"
```

Expected: **6 tests pass**

---

## 4. Parallel Pattern

Open `patterns/parallel.js` — find `runAllChecks()` and `aggregate()`.

**runAllChecks():** Create promises for each check using `runSingleCheck()`, run ALL with `Promise.allSettled()`. Handle rejected promises.

**aggregate():** Determine overall status (critical > error > warning > healthy). Build a summary string. Return `{ results, overallStatus, totalDurationMs, summary }`.

```bash
npx vitest run -t "ParallelHealthChecker"
```

Expected: **4 tests pass**

---

## 5. Orchestrator Pattern

Open `patterns/orchestrator.js` — find `processIncident()`.

**Implement 3 stages:** classification & routing, parallel health checks, diagnostic chain. Wrap each in try/catch. Build the report object at the end.

Tip: Import `createChainState` from `./chain.js` for Stage 3.

```bash
npx vitest run -t "IncidentOrchestrator"
```

Expected: **5 tests pass**

---

## 6. Run It

```bash
# All tests
npx vitest run
# Expected: 18 passed

# Full system (cached mode)
node agent_forge.js --cached

# Single incident
node agent_forge.js --incident INC-001 --cached

# Live mode (requires Ollama running)
node agent_forge.js
```

---

## 7. Submit

1. Fill in `report.md` (200+ words)
2. Commit and push:
   ```bash
   git add -A
   git commit -m "Complete Module 2 lab"
   git push
   ```
3. Verify your tests pass one more time
