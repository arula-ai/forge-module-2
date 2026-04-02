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

Expected: **4 tests pass**

<details>
<summary>Expected output</summary>

```
 DiagnosticChain > has three steps
 DiagnosticChain > execute populates state with all results
 DiagnosticChain > tracks completed steps
 DiagnosticChain > handles errors gracefully without crashing
```
</details>

<details>
<summary>Common failure</summary>

```
FAIL  DiagnosticChain > execute populates state with all results
  results is empty: {}
```
**Fix:** Your loop isn't storing results. Check `state.results[step.outputKey] = result`
</details>

<details>
<summary>If you're stuck</summary>

- `results` is empty: Make sure you're calling `response.asJson()` and storing the return value
- Only 1-2 steps complete: Your catch block might be re-throwing. Catch errors per step, push to `state.errors`, and continue the loop
- `TypeError: formatPrompt is not a function`: It's a module-level function, not a method. Call `formatPrompt(template, state)` directly
</details>

---

## 3. Router Pattern

Open `patterns/router.js` — find `classify()` and `route()`.

**classify():** Build a prompt with the incident details and category list. Ask the LLM to return JSON with category, confidence, and reasoning. Use `matchCategory()` to normalize the result.

**route():** Call classify, check confidence against threshold, pick handler or fallback, call `handleIncident()`.

```bash
npx vitest run -t "IncidentRouter"
```

Expected: **7 tests pass**

<details>
<summary>Expected output</summary>

```
 IncidentRouter > classifies database incident
 IncidentRouter > classifies billing incident
 IncidentRouter > classifies network incident
 IncidentRouter > classify returns confidence between 0 and 1
 IncidentRouter > route returns object with routeResult and handlerResponse
 IncidentRouter > route selects correct handler
 IncidentRouter > low confidence uses fallback handler
```
</details>

<details>
<summary>Common failure</summary>

```
FAIL  IncidentRouter > classifies database incident
  expected 'general/other' to be 'technical/database'
```
**Fix:** Your classification prompt probably doesn't include the incident description. Make sure you include `incident.title` and `incident.description` in the prompt.
</details>

<details>
<summary>If you're stuck</summary>

- Everything classifies as `general/other`: Print your prompt to verify incident details are included
- `matchCategory` returns OTHER: Pass `data.category` (the string), not the whole `data` object
- Fallback test fails: Check that you update `routeResult.handlerName` when using the fallback handler
</details>

> **Common mistake:** ESM requires file extensions in imports — `import { foo } from './bar.js'` not `'./bar'`

---

## 4. Parallel Pattern

Open `patterns/parallel.js` — find `runAllChecks()` and `aggregate()`.

**runAllChecks():** Create promises for each check using `runSingleCheck()`, run ALL with `Promise.allSettled()`. Handle rejected promises.

**aggregate():** Determine overall status (critical > error > warning > healthy). Build a summary string. Return `{ results, overallStatus, totalDurationMs, summary }`.

```bash
npx vitest run -t "ParallelHealthChecker"
```

Expected: **4 tests pass**

<details>
<summary>Common failure</summary>

```
FAIL  ParallelHealthChecker > aggregate returns critical when any result is critical
  expected 'healthy' to be 'critical'
```
**Fix:** Check priority ordering: `if (statuses.includes('critical'))` must come first. Use if/else if chain, not just the first status.
</details>

<details>
<summary>If you're stuck</summary>

- Tests hang forever: You're using `await` in a loop. Create all promises first, then `await Promise.allSettled(promises)`
- One failure kills all checks: Use `Promise.allSettled` (NOT `Promise.all`). allSettled never rejects.
- `outcome.value` is undefined: Check `outcome.status === 'fulfilled'` before accessing `.value`. Rejected outcomes have `.reason` instead.
</details>

> **Note:** `Promise.allSettled()` returns `{ status, value }` or `{ status, reason }` objects — not raw results like `Promise.all()`.

---

## 5. Orchestrator Pattern

Open `patterns/orchestrator.js` — find `processIncident()`.

**Implement 3 stages:** classification & routing, parallel health checks, diagnostic chain. Wrap each in try/catch. Build the report object at the end.

Tip: Import `createChainState` from `./chain.js` for Stage 3.

```bash
npx vitest run -t "IncidentOrchestrator"
```

Expected: **5 tests pass**

<details>
<summary>Common failure</summary>

```
FAIL  IncidentOrchestrator > report tracks stages including complete
  expected [ 'classifying', 'health_check', 'diagnosing' ] to contain 'complete'
```
**Fix:** After all stages, push `'complete'` to `stagesCompleted` before building the report.
</details>

<details>
<summary>If you're stuck</summary>

- `ReferenceError: classification is not defined`: Initialize all result variables (`classification = {}`, etc.) BEFORE the try blocks
- Only 1-2 stages run: Each stage needs its own independent try/catch. Don't nest them.
- `createChainState is not defined`: Add `import { createChainState } from './chain.js'` at the top, or use dynamic import inside the function
</details>

---

## 6. Run It

```bash
# All tests
npx vitest run
# Expected: 20 passed

# Full system (cached mode)
node agent_forge.js --cached

# Single incident
node agent_forge.js --incident INC-001 --cached

# Live mode (requires Ollama running)
node agent_forge.js
```

---

## 7. Experiment

### Experiment 1: Temperature and Confidence
Change `MODEL_TEMPERATURE` to `0.9` in `.env`. Run `node agent_forge.js --incident INC-001` (live, NOT cached) three times. Does classification stay consistent?

**Learn:** Higher temperature = more randomness = less predictable classification. Cached mode won't show this — that's the point of caching.

### Experiment 2: Break and Recover
Comment out the health check stage in your `processIncident()`. Run with `--cached`. Does the pipeline still complete?

**Learn:** Independent try/catch per stage = graceful degradation. A broken health checker shouldn't stop diagnosis.

### Experiment 3: The Unknown Incident
Add INC-005 (a security incident) to `data/incidents.json` and run classification. Which handler gets it?

**Learn:** The router falls back to `general/other` for unknown types. Production systems add new handlers as new categories emerge.

---

## 8. Submit

1. Fill in `report.md` (200+ words)
2. Commit and push:
   ```bash
   git add -A
   git commit -m "Complete Module 2 lab"
   git push
   ```
3. Run the lab grader (see below)

---

## 9. Grade Your Work

Open **GitHub Copilot Chat** in your IDE. For best results, select **Claude Sonnet 4** from the model dropdown. Then ask:

> "Grade my lab using the rubric in grade-lab.prompt.md"

Review the generated `GRADE_REPORT.md` in your track directory.
