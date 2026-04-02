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

---

## 3. Router Pattern

Open `patterns/router.py` — find `classify()` and `route()`.

**classify():** Build a prompt with the incident details and category list. Ask the LLM to return JSON with category, confidence, and reasoning. Use `_match_category()` to normalize the result.

**route():** Call classify, check confidence against threshold, pick handler or fallback, call handler.

```bash
python -m pytest tests/test_patterns.py::TestIncidentRouter -v
```

Expected: **7 tests pass**

---

## 4. Parallel Pattern

Open `patterns/parallel.py` — find `run_all_checks()` and `_aggregate()`.

**run_all_checks():** Create coroutines for each check, run ALL with `asyncio.gather(*tasks, return_exceptions=True)`. Handle exceptions.

**_aggregate():** Determine overall status (critical > error > warning > healthy). Build a summary string.

```bash
python -m pytest tests/test_patterns.py::TestParallelHealthChecker -v
```

Expected: **4 tests pass**

---

## 5. Orchestrator Pattern

Open `patterns/orchestrator.py` — find `process_incident()`.

**Implement 3 stages:** classification & routing, parallel health checks, diagnostic chain. Wrap each in try/except. Build IncidentReport at the end.

Tip: Import `create_chain_state` from `chain` module for Stage 3.

```bash
python -m pytest tests/test_patterns.py::TestIncidentOrchestrator -v
```

Expected: **5 tests pass**

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

## 7. Submit

1. Fill in `report.md` (200+ words)
2. Commit and push:
   ```bash
   git add -A
   git commit -m "Complete Module 2 lab"
   git push
   ```
3. Verify your tests pass one more time
