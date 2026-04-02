# Lab Experience Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Improve the AgentForge lab with track parity, differentiated pacing, structured experiments, success examples, a Copilot Chat grading agent, and updated presentation materials.

**Architecture:** Documentation-heavy changes across student guides, action guides, facilitator guide, and presentation outline. Two new files for the Copilot Chat grading agent. Two new Node tests for parity. No changes to pattern files, LLM client, or entry points.

**Tech Stack:** Markdown (guides), JavaScript/vitest (Node tests), GitHub Copilot Chat (grading agent)

---

### Task 1: Add 2 Missing Node Tests for Track Parity

**Files:**
- Modify: `node/tests/patterns.test.js`

- [ ] **Step 1: Add chain error handling test**

In `node/tests/patterns.test.js`, add this test inside the `DiagnosticChain` describe block, after the "tracks completed steps" test (after line 66):

```javascript
  it('handles errors gracefully without crashing', async () => {
    const errorChain = new DiagnosticChain(llm);
    errorChain.steps[1] = {
      name: 'Bad Step',
      systemPrompt: 'test',
      userPromptTemplate: '{nonexistent_key}',
      outputKey: 'bad_result',
    };
    const state = createChainState(incidents['INC-001']);
    const result = await errorChain.execute(state);
    expect(result.errors.length).toBeGreaterThan(0);
  });
```

Also update the section comment on line 47 from `// ── DiagnosticChain (3 tests)` to `// ── DiagnosticChain (4 tests)`.

- [ ] **Step 2: Add classify returns confidence test**

In `node/tests/patterns.test.js`, add this test inside the `IncidentRouter` describe block, after the "classifies network incident" test (after line 85):

```javascript
  it('classify returns confidence between 0 and 1', async () => {
    const result = await router.classify(incidents['INC-001']);
    expect(result.confidence).toBeGreaterThanOrEqual(0.0);
    expect(result.confidence).toBeLessThanOrEqual(1.0);
  });
```

Also update the section comment from `// ── IncidentRouter (6 tests)` to `// ── IncidentRouter (7 tests)`.

- [ ] **Step 3: Update file header comment**

Change line 6 from:
```javascript
 * Once implemented, all 18 tests should pass.
```
to:
```javascript
 * Once implemented, all 20 tests should pass.
```

- [ ] **Step 4: Run tests to verify they fail correctly with stubs**

Run: `cd node && npx vitest run`
Expected: 20 tests collected, 2 pass (structural), 18 fail with Error messages. The two new tests should appear in the failure list.

- [ ] **Step 5: Verify tests pass with reference solutions**

Temporarily apply reference solutions to all 4 Node pattern files (same approach used during initial repo build — edit stubs, run tests, revert). Verify 20/20 pass. Then restore stubs from `origin/main`:
```bash
git fetch origin main
git show origin/main:node/patterns/chain.js > node/patterns/chain.js
git show origin/main:node/patterns/router.js > node/patterns/router.js
git show origin/main:node/patterns/parallel.js > node/patterns/parallel.js
git show origin/main:node/patterns/orchestrator.js > node/patterns/orchestrator.js
```

- [ ] **Step 6: Commit**

```bash
git add node/tests/patterns.test.js
git commit -m "feat: add 2 Node tests for track parity (20 tests total)

Adds chain error handling test and classify confidence test.
Node now matches Python's 20-test count exactly."
```

---

### Task 2: Update Node Action Guide for Parity

**Files:**
- Modify: `node/LAB_ACTION_GUIDE.md`

- [ ] **Step 1: Update test counts and add common mistakes**

Replace the entire content of `node/LAB_ACTION_GUIDE.md` with:

```markdown
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
<summary>✅ Expected output</summary>

```
 ✓ DiagnosticChain > has three steps
 ✓ DiagnosticChain > execute populates state with all results
 ✓ DiagnosticChain > tracks completed steps
 ✓ DiagnosticChain > handles errors gracefully without crashing
```
</details>

<details>
<summary>❌ Common failure</summary>

```
FAIL  DiagnosticChain > execute populates state with all results
  → results is empty: {}
```
**Fix:** Your loop isn't storing results. Check `state.results[step.outputKey] = result`
</details>

<details>
<summary>🆘 If you're stuck</summary>

- `results` is empty → Make sure you're calling `response.asJson()` and storing the return value
- Only 1-2 steps complete → Your catch block might be re-throwing. Catch errors per step, push to `state.errors`, and continue the loop
- `TypeError: formatPrompt is not a function` → It's a module-level function, not a method. Call `formatPrompt(template, state)` directly
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
<summary>✅ Expected output</summary>

```
 ✓ IncidentRouter > classifies database incident
 ✓ IncidentRouter > classifies billing incident
 ✓ IncidentRouter > classifies network incident
 ✓ IncidentRouter > classify returns confidence between 0 and 1
 ✓ IncidentRouter > route returns object with routeResult and handlerResponse
 ✓ IncidentRouter > route selects correct handler
 ✓ IncidentRouter > low confidence uses fallback handler
```
</details>

<details>
<summary>❌ Common failure</summary>

```
FAIL  IncidentRouter > classifies database incident
  → expected 'general/other' to be 'technical/database'
```
**Fix:** Your classification prompt probably doesn't include the incident description. Make sure you include `incident.title` and `incident.description` in the prompt.
</details>

<details>
<summary>🆘 If you're stuck</summary>

- Everything classifies as `general/other` → Print your prompt to verify incident details are included
- `matchCategory` returns OTHER → Pass `data.category` (the string), not the whole `data` object
- Fallback test fails → Check that you update `routeResult.handlerName` when using the fallback handler
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
<summary>❌ Common failure</summary>

```
FAIL  ParallelHealthChecker > aggregate returns critical when any result is critical
  → expected 'healthy' to be 'critical'
```
**Fix:** Check priority ordering: `if (statuses.includes('critical'))` must come first. Use if/else if chain, not just the first status.
</details>

<details>
<summary>🆘 If you're stuck</summary>

- Tests hang forever → You're using `await` in a loop. Create all promises first, then `await Promise.allSettled(promises)`
- One failure kills all checks → Use `Promise.allSettled` (NOT `Promise.all`). allSettled never rejects.
- `outcome.value` is undefined → Check `outcome.status === 'fulfilled'` before accessing `.value`. Rejected outcomes have `.reason` instead.
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
<summary>❌ Common failure</summary>

```
FAIL  IncidentOrchestrator > report tracks stages including complete
  → expected [ 'classifying', 'health_check', 'diagnosing' ] to contain 'complete'
```
**Fix:** After all stages, push `'complete'` to `stagesCompleted` before building the report.
</details>

<details>
<summary>🆘 If you're stuck</summary>

- `ReferenceError: classification is not defined` → Initialize all result variables (`classification = {}`, etc.) BEFORE the try blocks
- Only 1-2 stages run → Each stage needs its own independent try/catch. Don't nest them.
- `createChainState is not defined` → Add `import { createChainState } from './chain.js'` at the top, or use dynamic import inside the function
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
```

- [ ] **Step 2: Commit**

```bash
git add node/LAB_ACTION_GUIDE.md
git commit -m "docs: overhaul Node action guide with parity, stuck blocks, experiments"
```

---

### Task 3: Update Python Action Guide

**Files:**
- Modify: `python/LAB_ACTION_GUIDE.md`

- [ ] **Step 1: Update with stuck blocks, expected output, experiments, grader**

Replace the entire content of `python/LAB_ACTION_GUIDE.md` with:

```markdown
# Lab Action Guide — Python Track

## 1. Setup

```bash
cd python
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python verify_setup.py
```

Expected: "All checks passed. You're ready for the lab!"

If Ollama isn't running, that's OK — you can use `--cached` mode for everything.

---

## 2. Chain Pattern

Open `patterns/chain.py` — find `execute()`.

**Implement the loop:** for each step, build the prompt, call the LLM, parse JSON, store the result.

```bash
python -m pytest tests/test_patterns.py::TestDiagnosticChain -v
```

Expected: **4 tests pass**

<details>
<summary>✅ Expected output</summary>

```
test_chain_has_three_steps PASSED
test_chain_execute_populates_state PASSED
test_chain_tracks_completed_steps PASSED
test_chain_handles_errors_gracefully PASSED

4 passed in 0.15s
```
</details>

<details>
<summary>❌ Common failure</summary>

```
FAILED test_chain_execute_populates_state
> assert "parsed_logs" in state.results
E AssertionError: assert "parsed_logs" in {}
```
**Fix:** Empty results dict = your loop isn't storing results. Check `state.results[step.output_key] = result`
</details>

<details>
<summary>🆘 If you're stuck</summary>

- `KeyError` on format → Check that you're using `self._format_prompt(step.user_prompt_template, state)`, not building the string manually
- Only 1-2 steps complete → Your error handling might be crashing the loop. Wrap each step in its own try/except, not one big try around the whole loop
- `ValueError: Failed to parse` → The LLM returned non-JSON. Check that you're passing `system=step.system_prompt` to the chat call
</details>

---

## 3. Router Pattern

Open `patterns/router.py` — find `classify()` and `route()`.

**classify():** Build a prompt with the incident details and category list. Ask the LLM to return JSON with category, confidence, and reasoning. Use `_match_category()` to normalize the result.

**route():** Call classify, check confidence against threshold, pick handler or fallback, call handler.

```bash
python -m pytest tests/test_patterns.py::TestIncidentRouter -v
```

Expected: **7 tests pass**

<details>
<summary>❌ Common failure</summary>

```
FAILED test_classify_database_incident
> assert IncidentCategory.OTHER == IncidentCategory.DATABASE
```
**Fix:** Your classification prompt probably doesn't include the incident description. Make sure you include `incident.get('title')` and `incident.get('description')` in the prompt.
</details>

<details>
<summary>🆘 If you're stuck</summary>

- Everything classifies as OTHER → Print your prompt to verify incident details are included
- `_match_category` returns OTHER → Pass `data.get("category", "")` (the string), not the whole `data` dict
- Fallback test fails → When confidence is below threshold, update `route_result.handler_name = handler.name`
</details>

---

## 4. Parallel Pattern

Open `patterns/parallel.py` — find `run_all_checks()` and `_aggregate()`.

**run_all_checks():** Create coroutines for each check, run ALL with `asyncio.gather(*tasks, return_exceptions=True)`. Handle exceptions.

**_aggregate():** Determine overall status (critical > error > warning > healthy). Build a summary string.

```bash
python -m pytest tests/test_patterns.py::TestParallelHealthChecker -v
```

Expected: **4 tests pass**

<details>
<summary>❌ Common failure</summary>

```
FAILED test_aggregate_critical_status
> assert "healthy" == "critical"
```
**Fix:** Check priority ordering: `if "critical" in statuses` must come first. Use if/elif chain.
</details>

<details>
<summary>🆘 If you're stuck</summary>

- Tests hang forever → You're using `await` in a loop. Create all tasks first: `tasks = [self._run_single_check(check, incident) for check in self.checks]`, then `await asyncio.gather(*tasks, return_exceptions=True)`
- One failure kills all checks → Add `return_exceptions=True` to `asyncio.gather()`
- `isinstance` check doesn't work → Check `isinstance(result, Exception)` for each item in the gather results
</details>

---

## 5. Orchestrator Pattern

Open `patterns/orchestrator.py` — find `process_incident()`.

**Implement 3 stages:** classification & routing, parallel health checks, diagnostic chain. Wrap each in try/except. Build IncidentReport at the end.

Tip: Use `create_chain_state` from the chain module for Stage 3.

```bash
python -m pytest tests/test_patterns.py::TestIncidentOrchestrator -v
```

Expected: **5 tests pass**

<details>
<summary>❌ Common failure</summary>

```
FAILED test_report_tracks_stages
> assert "complete" in []
```
**Fix:** After all stages, append `PipelineStage.COMPLETE.value` to `stages_completed`.
</details>

<details>
<summary>🆘 If you're stuck</summary>

- `NameError: classification is not defined` → Initialize all result variables (`classification = {}`, etc.) BEFORE the try blocks
- Only 1-2 stages run → Each stage needs its own independent try/except. Don't nest them.
- `ImportError` → Add `from .chain import create_chain_state` and `import json` at the top
</details>

> **Common mistake:** Don't forget `import json` — you need it for `json.dumps(incident)` when creating the chain state.

---

## 6. Run It

```bash
# All tests
python -m pytest tests/ -v
# Expected: 20 passed

# Full system (cached mode)
python agent_forge.py --cached

# Single incident
python agent_forge.py --incident INC-001 --cached

# Live mode (requires Ollama running)
python agent_forge.py
```

---

## 7. Experiment

### Experiment 1: Temperature and Confidence
Change `MODEL_TEMPERATURE` to `0.9` in `.env`. Run `python agent_forge.py --incident INC-001` (live, NOT cached) three times. Does classification stay consistent?

**Learn:** Higher temperature = more randomness = less predictable classification. Cached mode won't show this — that's the point of caching.

### Experiment 2: Break and Recover
Comment out the health check stage in your `process_incident()`. Run with `--cached`. Does the pipeline still complete?

**Learn:** Independent try/except per stage = graceful degradation. A broken health checker shouldn't stop diagnosis.

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
```

- [ ] **Step 2: Commit**

```bash
git add python/LAB_ACTION_GUIDE.md
git commit -m "docs: overhaul Python action guide with stuck blocks, experiments, grader"
```

---

### Task 4: Add "If You're Stuck" and Stretch Goals to Python Student Guide

**Files:**
- Modify: `docs/LAB_STUDENT_GUIDE_PYTHON.md`

- [ ] **Step 1: Add stretch goals and stuck blocks to each phase**

After each phase's test section in `docs/LAB_STUDENT_GUIDE_PYTHON.md`, add an "If You're Stuck" block and a "Stretch Goal" box. The content should match exactly what's in the Action Guide (Task 3) for the stuck blocks, plus these stretch goals:

After Phase 2 (Chain) test section, add:
```markdown
> **🚀 Stretch Goal:** Add a 4th step that generates a severity score 1-10. Does your chain still work with 4 steps? Do the existing tests still pass? What would you need to add to `cached_responses.json` to make this work in cached mode?
```

After Phase 3 (Router) test section, add:
```markdown
> **🚀 Stretch Goal:** What happens if you set `confidence_threshold` to 0.0? To 1.0? Try both. Can you write a test that verifies edge-case behavior at these extremes?
```

After Phase 4 (Parallel) test section, add:
```markdown
> **🚀 Stretch Goal:** Add timing output showing wall-clock time for the parallel run. Then change your implementation to run checks sequentially (one at a time). Compare the wall-clock times. How much faster is the parallel version? (In cached mode they'll be similar — why?)
```

After Phase 5 (Orchestrator) test section, add:
```markdown
> **🚀 Stretch Goal:** What happens if Stage 1 (classification) fails completely? Does Stage 2 (health checks) still run? Deliberately break `router.route()` by making it raise an exception, then run the pipeline. Verify that your error handling lets the remaining stages continue.
```

- [ ] **Step 2: Replace Phase 6 experiments with structured experiments**

Replace the current Phase 6 content (lines 543-575) with the three structured experiments from the spec (Temperature and Confidence, Break and Recover, The Unknown Incident). Use the same Do/Observe/Learn format as in the Action Guide (Task 3), but with more explanation appropriate for a student guide.

- [ ] **Step 3: Commit**

```bash
git add docs/LAB_STUDENT_GUIDE_PYTHON.md
git commit -m "docs: add stretch goals, stuck blocks, structured experiments to Python guide"
```

---

### Task 5: Add "If You're Stuck" and Stretch Goals to Node Student Guide

**Files:**
- Modify: `docs/LAB_STUDENT_GUIDE_NODE.md`

- [ ] **Step 1: Update test counts throughout**

Update all test count references in the guide to reflect the new 20-test total:
- Phase 2 Chain: 3 → 4 tests
- Phase 3 Router: 6 → 7 tests (one new confidence test)
- Phase 6/7 total: 18 → 20 tests
- Any other references to "18 tests" should become "20 tests"

- [ ] **Step 2: Add stretch goals and stuck blocks to each phase**

Use the same format as Task 4 but with Node.js-specific content. The "If You're Stuck" blocks should reference JavaScript patterns (`Promise.allSettled`, `outcome.status === 'rejected'`, ESM imports). The stretch goals are identical in concept but use JS syntax.

- [ ] **Step 3: Replace Phase 6 experiments with structured experiments**

Same three experiments as Python, but with Node commands (`node agent_forge.js` instead of `python agent_forge.py`).

- [ ] **Step 4: Add grading section after Submit**

Add the same "Grade Your Work" section as in the action guides — open Copilot Chat, select Claude Sonnet 4, ask it to grade using `grade-lab.prompt.md`.

- [ ] **Step 5: Fix router `route()` return type documentation**

The current guide (line 179) shows `route()` returning an array `[routeResult, handlerResponse]` but the test (line 87-93) expects an object `{ routeResult, handlerResponse }`. Update the guide's `route()` example to return `{ routeResult, handlerResponse }` to match the test expectations.

- [ ] **Step 6: Commit**

```bash
git add docs/LAB_STUDENT_GUIDE_NODE.md
git commit -m "docs: add parity updates, stuck blocks, stretch goals, experiments to Node guide"
```

---

### Task 6: Create Copilot Chat Grading Agent

**Files:**
- Create: `.github/copilot-instructions.md`
- Create: `grade-lab.prompt.md`
- Modify: `.gitignore`

- [ ] **Step 1: Create `.github/copilot-instructions.md`**

```bash
mkdir -p .github
```

Write to `.github/copilot-instructions.md`:

```markdown
# AgentForge — Module 2 Lab

This is a teaching lab where students implement 4 agentic AI patterns (Chain, Router, Parallel, Orchestrator) in an incident response system.

## Structure

- `python/` — Python track (Python 3.11+, async with httpx)
- `node/` — Node.js track (Node 20+, ESM with native fetch)
- `data/` — Shared incident data and cached LLM responses

## What Students Implement

Students implement core methods marked with `raise NotImplementedError` (Python) or `throw new Error` (Node):

- **Chain:** `execute()` — loop through steps, call LLM, accumulate state
- **Router:** `classify()` + `route()` — classify incident, delegate to handler
- **Parallel:** `run_all_checks()` + `_aggregate()` — fan-out checks, aggregate results
- **Orchestrator:** `process_incident()` — compose all 3 patterns into a pipeline

## Testing

- Python: `cd python && python -m pytest tests/ -v` (20 tests)
- Node: `cd node && npx vitest run` (20 tests)
- All tests use `CachedLLMClient` — no Ollama dependency

## Grading

See `grade-lab.prompt.md` for the complete grading rubric. Students can ask you to grade their lab using that rubric.
```

- [ ] **Step 2: Create `grade-lab.prompt.md`**

Write to `grade-lab.prompt.md` in the repo root:

```markdown
# Lab 2 Grading Rubric — AgentForge

> **For best results, select Claude Sonnet 4 or later in the Copilot Chat model dropdown.**

You are grading a student's implementation of the AgentForge Module 2 lab. The student implemented 4 agentic patterns (Chain, Router, Parallel, Orchestrator) in either the Python or Node.js track.

## Instructions

1. Detect which track the student is using (check for `python/patterns/` or `node/patterns/`)
2. Ask the student to run the test suite and paste the output, OR read the pattern files directly
3. Evaluate against the rubric below
4. Write the grade report to `GRADE_REPORT.md` in the track directory (`python/GRADE_REPORT.md` or `node/GRADE_REPORT.md`)

## Rubric (100 points)

### Section 1: Technical Correctness (50 points)

Ask the student to run their test suite and share the results. Score based on passing tests:

| Component | Tests | Points |
|-----------|-------|--------|
| Chain | 4 tests | 10 |
| Router | 7 tests | 12 |
| Parallel | 4 tests | 10 |
| Orchestrator | 5 tests | 13 |
| Full suite (all 20 green) | bonus | 5 |

Award points proportionally (e.g., 3/4 chain tests = 8/10 points, rounded to nearest integer).

### Section 2: Code Quality (25 points)

Read each pattern file and check for these implementation patterns:

**Chain (6 pts):**
- Uses `_format_prompt`/`formatPrompt` helper, not manual string building — 2 pts
- Has try/except (or try/catch) per step, not one big try around the whole loop — 2 pts
- Returns state at the end of the method — 2 pts

**Router (7 pts):**
- Builds category list dynamically from enum/object (not a hardcoded string) — 2 pts
- Uses `_match_category`/`matchCategory` helper — 2 pts
- Checks confidence against threshold before selecting handler — 2 pts
- Updates handler_name/handlerName when using fallback — 1 pt

**Parallel (6 pts):**
- Uses `asyncio.gather`/`Promise.allSettled` (not sequential await in a loop) — 3 pts
- Handles exceptions from gather results — 2 pts
- Correct priority ordering in aggregate: critical > error > warning > healthy — 1 pt

**Orchestrator (6 pts):**
- Initializes all result variables before try blocks — 2 pts
- All 3 stages wrapped independently in try/except or try/catch (not nested) — 2 pts
- Uses `create_chain_state`/`createChainState` factory — 2 pts

### Section 3: Report Quality (15 points)

Read `report.md` and evaluate:

- All 4 pattern checkboxes marked — 2 pts
- Metrics section filled in with actual numbers (not `___` placeholders) — 3 pts
- All 4 reflection questions answered — 4 pts (1 per question)
- Reflection depth — 6 pts:
  - References specific patterns by name (not generic "the patterns") — 1.5 pts
  - Mentions concrete challenges encountered — 1.5 pts
  - Proposes specific production improvements — 1.5 pts
  - Shows understanding of why patterns exist, not just what they do — 1.5 pts

### Section 4: Implementation Style (10 points)

Holistic assessment of the code:

- Consistent style: naming, formatting, error messages — 3 pts
- Uses provided helpers appropriately (doesn't reinvent them) — 3 pts
- Clean code: no dead code, debugging artifacts, or commented-out experiments — 2 pts
- Evidence of understanding vs. copy-paste: personalized error messages, different prompt wording, or additional logging score higher than verbatim matches to reference solutions — 2 pts

## Output Format

Write `GRADE_REPORT.md` with this structure:

```
# Lab 2 Grade Report

**Track:** [Python/Node.js] | **Date:** [today] | **Total: [N]/100**

## Technical Correctness ([N]/50)
| Component | Tests | Result | Points |
|-----------|-------|--------|--------|
| Chain | [N]/4 pass | [✓/details] | [N]/10 |
| Router | [N]/7 pass | [✓/details] | [N]/12 |
| Parallel | [N]/4 pass | [✓/details] | [N]/10 |
| Orchestrator | [N]/5 pass | [✓/details] | [N]/13 |
| Full suite bonus | [N]/20 | — | [N]/5 |

> [Specific notes on any failures — what's likely wrong]

## Code Quality ([N]/25)
| Pattern | Score | Notes |
|---------|-------|-------|
| Chain | [N]/6 | [notes] |
| Router | [N]/7 | [notes] |
| Parallel | [N]/6 | [notes] |
| Orchestrator | [N]/6 | [notes] |

## Report Quality ([N]/15)
- Checkboxes: [N]/2
- Metrics filled: [N]/3
- Questions answered: [N]/4
- Reflection depth: [N]/6 — [specific feedback]

## Implementation Style ([N]/10)
- Consistency: [N]/3
- Helper usage: [N]/3
- Clean code: [N]/2
- Understanding: [N]/2 — [specific feedback]

---

**Strengths:** [2-3 sentences about what the student did well]

**Areas for improvement:** [2-3 sentences of constructive feedback]

*Graded by GitHub Copilot using the AgentForge Lab 2 rubric.*
*Rubric version: 1.0*
```

Be fair but strict. Give specific, actionable feedback. Point to exact lines when noting issues.
```

- [ ] **Step 3: Add GRADE_REPORT.md to .gitignore**

Add to `.gitignore` after the `# Node` section:

```
# Grading output
GRADE_REPORT.md
```

- [ ] **Step 4: Commit**

```bash
git add .github/copilot-instructions.md grade-lab.prompt.md .gitignore
git commit -m "feat: add Copilot Chat grading agent with rubric

.github/copilot-instructions.md provides project context.
grade-lab.prompt.md contains the full 100-point grading rubric.
Students ask Copilot Chat to grade their work and get GRADE_REPORT.md."
```

---

### Task 7: Update Facilitator Guide with Grading Agent Reference

**Files:**
- Modify: `docs/LAB_FACILITATOR_GUIDE.md`

- [ ] **Step 1: Add grading agent section after the existing grading rubric**

After the "Automated Grading Script" section (around line 420), add:

```markdown
### AI-Assisted Grading (GitHub Copilot Chat)

Students can self-grade using GitHub Copilot Chat. The repo includes:
- `.github/copilot-instructions.md` — project context for Copilot
- `grade-lab.prompt.md` — complete grading rubric as a Copilot prompt

**Student workflow:**
1. Open Copilot Chat in VS Code
2. Select Claude Sonnet 4 (recommended) from the model dropdown
3. Ask: "Grade my lab using the rubric in grade-lab.prompt.md"
4. Review the generated `GRADE_REPORT.md`

**Facilitator note:** The AI grader is a teaching tool, not a replacement for your judgment. Use its output as a conversation starter: "The grader flagged X — what do you think about that?" The grader checks code quality patterns (proper use of helpers, error handling structure, copy-paste detection) that are hard to verify manually at scale.

**Limitations:** The grader cannot run tests itself — it relies on student-provided test output. It may give slightly different scores across models. The rubric is designed for Claude Sonnet 4 but works with any frontier model.
```

- [ ] **Step 2: Update experiment section references**

Find the "Common Student Issues" section and add a note referencing the new structured experiments:

```markdown
### Issue 6: Students don't know what to do in the experiment phase

**Response:** Point them to the three structured experiments in the guide:
1. Temperature and Confidence — change MODEL_TEMPERATURE to 0.9, run 3 times
2. Break and Recover — comment out a stage, observe graceful degradation
3. The Unknown Incident — add INC-005 (security), observe fallback routing
```

- [ ] **Step 3: Commit**

```bash
git add docs/LAB_FACILITATOR_GUIDE.md
git commit -m "docs: add grading agent reference and experiment guidance to facilitator guide"
```

---

### Task 8: Update Presentation Outline

**Files:**
- Modify: `docs/MODULE_2_PRESENTATION_OUTLINE.md`

- [ ] **Step 1: Update Lab Intro talking points**

Find the "Lab Intro" block in the timing cheat sheet (around line 616). Add a new slide section before "Lab Work" begins:

```markdown
#### Slide: Lab Kickoff — How This Lab Works

**Speaker Notes:**
> This lab is designed for all experience levels. Go at your own pace.
> If you're stuck, look for the "If You're Stuck" boxes in the guide — they diagnose common problems.
> If you finish a pattern early, look for the "Stretch Goal" box to go deeper.
> Don't just get the tests green — understand *why* each pattern exists.
> When you're completely done, use the AI grader to evaluate your work.

**On-Screen:**
- Lab structure: Setup → Chain → Router → Parallel → Orchestrator → Experiment → Submit → Grade
- "If You're Stuck" / "Stretch Goal" callouts highlighted
- Target: 20 tests passing
```

- [ ] **Step 2: Add grading agent slide after Slide 28**

After the "Assignment & Next Session" slide (line 595), add:

```markdown
#### Slide 29: Grade Your Work with AI

**Speaker Notes:**
> When you've completed the lab and written your reflection, you can use
> GitHub Copilot Chat to grade your work. Open Copilot Chat, select
> Claude Sonnet 4 from the model dropdown, and ask it to grade your lab
> using the rubric in grade-lab.prompt.md. It evaluates four dimensions:
> technical correctness, code quality, report quality, and implementation style.
> This is a teaching tool — use the feedback to improve, not just the score.

**On-Screen:**
- Screenshot of Copilot Chat grading interaction
- The 4 evaluation dimensions with point breakdown
- Example GRADE_REPORT.md output

**Facilitator note:** "The grading agent is not the final grade. Use its output as a conversation starter. Ask students: 'What did the grader catch that you missed? What would you add to the rubric?'"
```

- [ ] **Step 3: Update experiment talking points**

Find the Phase 6 reference in the presentation. Replace any vague "change temperature and explore" language with the three structured experiments:

```markdown
**Experiment Phase Talking Points:**

Three guided experiments (3-4 min each):
1. **Temperature and Confidence** — Change temp to 0.9, run 3 times. "Watch how randomness affects classification reliability."
2. **Break and Recover** — Comment out a stage, run pipeline. "This is graceful degradation — a production pattern."
3. **The Unknown Incident** — Add a security incident. "The system handles novel input through fallback routing."

Expected discussion: "Why would you want low temperature in production for classification tasks?"
```

- [ ] **Step 4: Update debrief discussion questions**

Add to the debrief/discussion slide:

```markdown
**Additional discussion questions:**
- "What did the AI grader catch that you missed?"
- "What would you add to the grading rubric?"
- "Is automated code review fair? What can it evaluate well, and what can't it?"
```

- [ ] **Step 5: Add facilitator intervention guidance**

Add to the instructor resources appendix:

```markdown
### Differentiated Pacing Guidance

- At each phase checkpoint, scan the room. Students who finished early should be working on stretch goals, not idle.
- Students stuck past the time marker: point them to the "If You're Stuck" block first. Only intervene directly if the block doesn't resolve it.
- The most common facilitator mistake is helping too quickly. The struggle is where learning happens. Give them 2-3 minutes with the guide before stepping in.
```

- [ ] **Step 6: Commit**

```bash
git add docs/MODULE_2_PRESENTATION_OUTLINE.md
git commit -m "docs: update presentation with grading agent, experiments, pacing guidance"
```

---

### Task 9: Final Verification

**Files:** None (verification only)

- [ ] **Step 1: Verify Node test count**

```bash
cd node && npx vitest run 2>&1 | tail -5
```
Expected: "Tests  18 failed | 2 passed (20)" — 20 total tests collected with stubs.

- [ ] **Step 2: Verify Python test count unchanged**

```bash
cd python && source .venv/bin/activate && python -m pytest tests/ -v --tb=no 2>&1 | tail -5
```
Expected: "18 failed, 2 passed" — 20 total, unchanged.

- [ ] **Step 3: Verify new files exist**

```bash
ls -la .github/copilot-instructions.md grade-lab.prompt.md
```
Both should exist.

- [ ] **Step 4: Verify .gitignore includes GRADE_REPORT.md**

```bash
grep GRADE_REPORT .gitignore
```
Expected: `GRADE_REPORT.md`

- [ ] **Step 5: Verify no pattern files were modified**

```bash
git diff origin/main -- python/patterns/ node/patterns/
```
Expected: no output (pattern files unchanged).

- [ ] **Step 6: Push all changes**

```bash
git push origin main
```
