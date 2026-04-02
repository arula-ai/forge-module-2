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
<summary>Expected output</summary>

```
test_chain_has_three_steps PASSED
test_chain_execute_populates_state PASSED
test_chain_tracks_completed_steps PASSED
test_chain_handles_errors_gracefully PASSED

4 passed
```
</details>

<details>
<summary>Common failure</summary>

```
FAILED test_chain_execute_populates_state
> assert "parsed_logs" in state.results
E AssertionError: assert "parsed_logs" in {}
```
**Fix:** Empty results dict = your loop isn't storing results. Check `state.results[step.output_key] = result`
</details>

<details>
<summary>If you're stuck</summary>

- `KeyError` on format: Check that you're using `self._format_prompt(step.user_prompt_template, state)`, not building the string manually
- Only 1-2 steps complete: Your error handling might be crashing the loop. Wrap each step in its own try/except, not one big try around the whole loop
- `ValueError: Failed to parse`: The LLM returned non-JSON. Check that you're passing `system=step.system_prompt` to the chat call
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
<summary>Common failure</summary>

```
FAILED test_classify_database_incident
> assert IncidentCategory.OTHER == IncidentCategory.DATABASE
```
**Fix:** Your classification prompt probably doesn't include the incident description. Make sure you include `incident.get('title')` and `incident.get('description')` in the prompt.
</details>

<details>
<summary>If you're stuck</summary>

- Everything classifies as OTHER: Print your prompt to verify incident details are included
- `_match_category` returns OTHER: Pass `data.get("category", "")` (the string), not the whole `data` dict
- Fallback test fails: When confidence is below threshold, update `route_result.handler_name = handler.name`
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
<summary>Common failure</summary>

```
FAILED test_aggregate_critical_status
> assert "healthy" == "critical"
```
**Fix:** Check priority ordering: `if "critical" in statuses` must come first. Use if/elif chain.
</details>

<details>
<summary>If you're stuck</summary>

- Tests hang forever: You're using `await` in a loop. Create all tasks first: `tasks = [self._run_single_check(check, incident) for check in self.checks]`, then `await asyncio.gather(*tasks, return_exceptions=True)`
- One failure kills all checks: Add `return_exceptions=True` to `asyncio.gather()`
- `isinstance` check doesn't work: Check `isinstance(result, Exception)` for each item in the gather results
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
<summary>Common failure</summary>

```
FAILED test_report_tracks_stages
> assert "complete" in []
```
**Fix:** After all stages, append `PipelineStage.COMPLETE.value` to `stages_completed`.
</details>

<details>
<summary>If you're stuck</summary>

- `NameError: classification is not defined`: Initialize all result variables (`classification = {}`, etc.) BEFORE the try blocks
- Only 1-2 stages run: Each stage needs its own independent try/except. Don't nest them.
- `ImportError`: Add `from .chain import create_chain_state` and `import json` at the top
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
