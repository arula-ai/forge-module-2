# AgentForge Lab — Design Specification

## Overview

Build the complete lab repository for CGSE-Advanced Module 2: "AgentForge — Incident Response System." Students implement four core agentic patterns (Sequential Chain, Router, Parallel Fan-Out, Orchestrator) using Ollama + Qwen3.5:4b locally. Two tracks: Python and Node.js.

**Repo:** `arula-ai/forge-module-2` (private)
**Runtime:** Ollama with Qwen3.5:4b (local, no API keys)
**Audience:** Students in CGSE-Advanced course

---

## 1. Repository Structure

```
forge-module-2/
├── python/
│   ├── agent_forge.py              ← Main entry point (provided)
│   ├── verify_setup.py             ← Environment verification (provided)
│   ├── requirements.txt            ← Dependencies
│   ├── .env.example                ← Config template
│   ├── LAB_ACTION_GUIDE.md         ← Step-by-step student recipe
│   ├── patterns/
│   │   ├── __init__.py             ← Package exports
│   │   ├── llm_client.py           ← Ollama wrapper (DO NOT MODIFY)
│   │   ├── chain.py                ← Student implements execute()
│   │   ├── router.py               ← Student implements classify() + route()
│   │   ├── parallel.py             ← Student implements run_all_checks() + _aggregate()
│   │   └── orchestrator.py         ← Student implements process_incident()
│   ├── tests/
│   │   ├── __init__.py
│   │   └── test_patterns.py        ← 20 tests with cached LLM mock
│   └── report.md                   ← Reflection template
├── node/
│   ├── agent_forge.js              ← Main entry point (provided)
│   ├── verify_setup.js             ← Environment verification (provided)
│   ├── package.json                ← Dependencies + scripts
│   ├── .env.example                ← Config template
│   ├── LAB_ACTION_GUIDE.md         ← Step-by-step student recipe
│   ├── patterns/
│   │   ├── llm_client.js           ← Ollama wrapper (DO NOT MODIFY)
│   │   ├── chain.js                ← Student implements execute()
│   │   ├── router.js               ← Student implements classify() + route()
│   │   ├── parallel.js             ← Student implements runAllChecks() + aggregate()
│   │   └── orchestrator.js         ← Student implements processIncident()
│   ├── tests/
│   │   └── patterns.test.js        ← 18 tests with cached LLM mock
│   └── report.md                   ← Reflection template
├── data/
│   ├── incidents.json              ← 4 sample incidents (shared)
│   └── cached_responses.json       ← Offline fallback (shared)
├── docs/
│   ├── LAB_BUILD_INSTRUCTIONS.md   ← (existing)
│   ├── LAB_STUDENT_GUIDE_PYTHON.md ← (existing)
│   ├── LAB_STUDENT_GUIDE_NODE.md   ← (existing)
│   ├── LAB_FACILITATOR_GUIDE.md    ← (existing)
│   └── MODULE_2_PRESENTATION_OUTLINE.md ← (existing)
├── .gitignore
├── CLAUDE.md                       ← Project conventions for Claude Code / autowork
└── README.md                       ← Lab overview + quickstart
```

Key decisions:
- `.env.example` is checked in; `.env` is gitignored. Students copy it.
- Shared `data/` at repo root. Both tracks reference `../data/`.
- Each track has its own `LAB_ACTION_GUIDE.md` — self-contained step-by-step recipe.

---

## 2. LLM Client (Provided — Students Do Not Modify)

### Python: `patterns/llm_client.py`

```
class LLMResponse:
    content: str          # Raw text response
    duration_ms: float    # Response timing

    def as_json() -> dict  # Parses content as JSON; raises ValueError on invalid

class LLMClient:
    def __init__(base_url, model, temperature, timeout)
    async def chat(prompt: str, system: str = "", temperature: float = None) -> LLMResponse

class CachedLLMClient(LLMClient):
    """Returns pre-built responses from cached_responses.json based on keyword matching."""
    def __init__(cache_path: str)
    async def chat(prompt, system="", temperature=None) -> LLMResponse
```

- Uses `httpx.AsyncClient` for HTTP
- Loads config from environment: `OLLAMA_BASE_URL`, `MODEL_NAME`, `MODEL_TEMPERATURE`, `REQUEST_TIMEOUT`
- `CachedLLMClient` matches keywords in the prompt to keys in `cached_responses.json`

### Node: `patterns/llm_client.js`

Same interface, camelCase:
- `LLMResponse` with `.content`, `.durationMs`, `.asJson()`
- `LLMClient` with `async chat(prompt, { system, temperature })`
- `CachedLLMClient` same keyword-matching approach
- Uses native `fetch`

### Keyword Matching Strategy

The `CachedLLMClient` inspects the **lowercased prompt** to select a cached response. Rules are evaluated in the numbered order below; first match wins. Implementations MUST evaluate rules in this exact sequence.

**IMPORTANT DESIGN CONSTRAINT:** Classification prompts list ALL category names, so matching on category keywords (e.g., "database") would match every classification call. Instead, classification matching uses **incident-specific keywords** from the title/description that will appear in the prompt alongside "classify."

**Rule 1-4: Classification (router classify calls)**
Match: prompt contains "classify" AND incident-specific content keywords:
1. "classify" + ("connection pool" or "postgresql" or "hikari") → `classify_database`
2. "classify" + ("double charge" or "duplicate" or "overcharge" or "refund") → `classify_billing`
3. "classify" + ("503" or "gateway" or "upstream" or "circuit breaker") → `classify_network`
4. "classify" + ("password reset" or "email" or "queue depth") → `classify_general`

**Rule 5-9: Handler responses (router handler.handle calls)**
Match: prompt is from a handler (system prompt contains "specialist" or "handler"). The handler's system prompt contains domain keywords:
5. system prompt contains "database" → `handler_database`
6. system prompt contains "billing" or "payment" → `handler_billing`
7. system prompt contains "network" → `handler_network`
8. system prompt contains "email" → `handler_email`
9. fallback handler (no domain match in system prompt) → `handler_general`

Note: Handler matching checks the **system** prompt parameter, not the user prompt. This is because the system prompt is set per-handler and contains the specialist domain keyword. The `chat()` method receives both `prompt` and `system` parameters.

**Rule 10-12: Chain steps (diagnostic chain calls)**
10. prompt contains "parse" or "extract" (and does NOT contain "classify") → `chain_parse`
11. prompt contains "root cause" or "analyze" (and does NOT contain "classify") → `chain_analyze`
12. prompt contains "recommend" → `chain_recommend`

**Rule 13-16: Parallel health checks**
Match: prompt contains subsystem keyword AND health-check context keywords:
13. prompt contains "memory" + ("health" or "status" or "check" or "assess") → `parallel_memory_check`
14. prompt contains "cpu" + ("health" or "status" or "check" or "assess") → `parallel_cpu_check`
15. prompt contains "disk" + ("health" or "status" or "check" or "assess") → `parallel_disk_check`
16. prompt contains "network" + ("health" or "status" or "check" or "assess") → `parallel_network_check`

**Rule 17: Fallback**
17. No match → `{"error": "No cached response matched", "status": "unknown"}`

---

## 3. Pattern Files (Student TODO Stubs)

Each file provides data structures and helpers. Students implement core methods using pseudocode skeleton comments (Option B). The loop/structure is given; the API calls, error handling, and state management are left to the student.

### 3.1 chain.py / chain.js

**Provided:**
- `ChainState` — `incident_id`, `raw_input`, `logs`, `results: {}`, `steps_completed: []`, `errors: []`
- `ChainStep` — `name`, `system_prompt`, `user_prompt_template`, `output_key`
- `DiagnosticChain` class with `_build_steps()` defining 3 steps:
  1. **Parse Logs** (output_key: `parsed_logs`) — extract error messages, timestamps, affected services
  2. **Analyze Root Cause** (output_key: `root_cause`) — determine what went wrong
  3. **Generate Recommendations** (output_key: `recommendations`) — suggest fixes
- `_format_prompt(template, state)` — interpolates state into prompt templates
- `createChainState(incident)` factory (Node only)

**Student implements:** `execute(state)` with pseudocode skeleton:
```
# 1. Build the prompt using self._format_prompt()
# 2. Call the LLM with the prompt and step's system prompt
# 3. Parse the JSON response
# 4. Store result in state.results[step.output_key]
# 5. Track completion in state.steps_completed
# 6. Handle errors: append to state.errors, don't crash the loop
```

### 3.2 router.py / router.js

**Provided:**
- `IncidentCategory` enum: `technical/database`, `technical/network`, `billing/payment`, `general/email`, `general/other`
- `IncidentHandler` — `name`, `system_prompt`, `handle(incident)` method (calls LLM)
- `RouteResult` — `category`, `confidence`, `reasoning`, `handler_name`
- `HandlerResponse` — `handler`, `summary`, `priority`, `escalation_needed`
- `IncidentRouter` with `_build_handlers()` (5 handlers), `_match_category()` fuzzy matcher, `confidence_threshold = 0.6`
- `_match_category(raw: str) -> IncidentCategory` — normalizes the LLM's free-text category string to an enum value. Algorithm: lowercase and strip whitespace from `raw`. First try exact match against enum values. If no exact match, check if `raw` contains any of these substrings: "database" → DATABASE, "network" → NETWORK, "billing" or "payment" → BILLING, "email" → EMAIL. If still no match, return OTHER.
- `handleIncident(llm, handler, incident)` module-level helper (Node)

**Student implements:**

`classify(incident)` with pseudocode:
```
# 1. Build list of valid categories from IncidentCategory enum
# 2. Construct prompt with incident title, description, severity
# 3. Ask LLM to classify with JSON response (category, confidence, reasoning)
# 4. Parse response, match category using _match_category()
# 5. Return RouteResult with matched category, confidence, reasoning, handler name
```

`route(incident)` with pseudocode:
```
# 1. Call self.classify(incident)
# 2. If confidence >= threshold, select matching handler
# 3. If confidence < threshold, use fallback handler
# 4. Delegate to selected handler
# 5. Return (RouteResult, HandlerResponse)
```

### 3.3 parallel.py / parallel.js

**Provided:**
- `HealthCheck` — `name`, `subsystem`, `prompt_template`
- `CheckResult` — `name`, `subsystem`, `status`, `details`, `duration_ms`
- `HealthReport` — `results`, `overall_status`, `total_duration_ms`, `summary`
- `ParallelHealthChecker` with `_build_checks()` defining 4 checks: memory, CPU, disk, network
- `_run_single_check(check, incident)` — runs one check against the LLM, returns `CheckResult`

**Student implements:**

`run_all_checks(incident)` with pseudocode:
```
# 1. Create a coroutine/promise for each check using _run_single_check()
# 2. Run ALL concurrently with asyncio.gather / Promise.allSettled
# 3. Handle exceptions: convert to CheckResult with status "error"
# 4. Display results with status icons
# 5. Return self._aggregate(results, total_ms)
```

`_aggregate(results, total_ms)` / `aggregate(results, totalMs)` with pseudocode:
```
# 1. Collect all statuses
# 2. Determine overall: critical > error > warning > healthy
# 3. Build summary string
# 4. Return HealthReport
```

### 3.4 orchestrator.py / orchestrator.js

**Provided:**
- `PipelineStage` enum: `classifying`, `health_check`, `diagnosing`, `complete`
- `IncidentReport` dataclass with: `incident_id`, `title`, `classification`, `handler_response`, `health_report`, `diagnostic_chain`, `total_duration_ms`, `stages_completed`, `errors`
- `IncidentOrchestrator` initialized with `router`, `health_checker`, `diagnostic_chain`
- `_display_report(report)` — renders rich terminal output with boxes, colors, timing

**Student implements:** `process_incident(incident)` with pseudocode:
```
# Stage 1: Classification & Routing
# 1. Call self.router.route(incident)
# 2. Extract classification and handler response data
# 3. Track stage completion, catch errors

# Stage 2: Parallel Health Checks
# 4. Call self.health_checker.run_all_checks(incident)
# 5. Extract health report data
# 6. Track stage completion, catch errors

# Stage 3: Diagnostic Chain
# 7. Create ChainState from incident
# 8. Call self.diagnostic_chain.execute(state)
# 9. Extract chain results
# 10. Track stage completion, catch errors

# Stage 4: Compile Report
# 11. Build IncidentReport with all collected data
# 12. Call self._display_report(report)
# 13. Return report
```

---

## 4. Test Suites

All tests inject `CachedLLMClient` — deterministic, no Ollama required.

### Python: `tests/test_patterns.py` — 20 tests

**TestDiagnosticChain (4 tests):**
1. `test_chain_has_three_steps` — verifies step count is 3
2. `test_chain_execute_populates_state` — runs execute, checks results dict has all 3 output keys (`parsed_logs`, `root_cause`, `recommendations`)
3. `test_chain_tracks_completed_steps` — checks `steps_completed` has 3 entries
4. `test_chain_handles_errors_gracefully` — injects a failing step, verifies error captured but chain continues

**TestIncidentRouter (7 tests):**
5. `test_classify_database_incident` — INC-001 → `technical/database`
6. `test_classify_billing_incident` — INC-002 → `billing/payment`
7. `test_classify_network_incident` — INC-003 → `technical/network`
8. `test_classify_returns_confidence` — confidence is a float between 0 and 1
9. `test_route_returns_tuple` — returns (RouteResult, HandlerResponse)
10. `test_route_selects_correct_handler` — handler name matches category
11. `test_low_confidence_uses_fallback` — set threshold to 0.99, verify fallback handler used

**TestParallelHealthChecker (4 tests):**
12. `test_has_four_checks` — verifies check count is 4
13. `test_run_all_checks_returns_health_report` — returns HealthReport with 4 results
14. `test_aggregate_critical_status` — critical in any result → overall critical
15. `test_aggregate_healthy_status` — all healthy → overall healthy

**TestIncidentOrchestrator (5 tests):**
16. `test_process_incident_returns_report` — returns IncidentReport
17. `test_report_has_classification` — classification dict is populated
18. `test_report_has_health_report` — health_report dict is populated
19. `test_report_has_diagnostic_chain` — diagnostic_chain dict is populated
20. `test_report_tracks_stages` — stages_completed includes all expected stages

### Node: `tests/patterns.test.js` — 18 tests

Same structure, minus `test_chain_handles_errors_gracefully` and `test_classify_returns_confidence` (Node guide specifies 18). Same coverage intent with camelCase naming.

### Test Fixture

Shared setup in each test file:
- Load `../../data/incidents.json` and `../../data/cached_responses.json`
- Create `CachedLLMClient` from cached responses
- Wire up all pattern instances with the cached client
- Expose incidents by ID for individual test use

---

## 5. Main Entry Point (Provided)

### `agent_forge.py` / `agent_forge.js`

Students do not modify this file.

**CLI:**
- No args: process all 4 incidents
- `--incident INC-001`: process single incident
- `--cached`: use cached responses instead of Ollama

**Flow:**
1. Parse CLI args
2. Load `.env` config
3. Load incidents from `../data/incidents.json`
4. Create LLM client (real or cached based on `--cached`)
5. Wire up: `DiagnosticChain(llm)`, `IncidentRouter(llm)`, `ParallelHealthChecker(llm)`, `IncidentOrchestrator(router, checker, chain)`
6. For each selected incident: `await orchestrator.process_incident(incident)`
7. Print summary: total incidents, total time, any failures

**Terminal output:**
- Python: `rich` library (colored text, boxes, tables)
- Node: `chalk` (colors), `ora` (spinners)

### `verify_setup.py` / `verify_setup.js`

As specified in LAB_BUILD_INSTRUCTIONS.md:
1. Check Ollama is running at configured URL
2. List available models
3. Verify target model is pulled
4. Test inference with a simple prompt
5. Report pass/fail

---

## 6. LAB_ACTION_GUIDE.md (One Per Track)

Lives at `python/LAB_ACTION_GUIDE.md` and `node/LAB_ACTION_GUIDE.md`.

A concise, linear, copy-paste-ready checklist students follow top to bottom. No deep explanations — just actions and expected results.

**Structure per track:**

1. **Setup** (5 steps)
   - Clone repo
   - Enter track directory
   - Install dependencies (exact command)
   - Copy `.env.example` to `.env`
   - Run `verify_setup` (exact command + expected output)

2. **Phase 2: Chain** (4 steps)
   - Open `patterns/chain.py`
   - Implement `execute()` — brief hint
   - Run test: exact command
   - Expected: 4 tests pass

3. **Phase 3: Router** (5 steps)
   - Open `patterns/router.py`
   - Implement `classify()` — brief hint
   - Implement `route()` — brief hint
   - Run test: exact command
   - Expected: 7 tests pass

4. **Phase 4: Parallel** (5 steps)
   - Open `patterns/parallel.py`
   - Implement `run_all_checks()` — brief hint
   - Implement `_aggregate()` — brief hint
   - Run test: exact command
   - Expected: 4 tests pass

5. **Phase 5: Orchestrator** (4 steps)
   - Open `patterns/orchestrator.py`
   - Implement `process_incident()` — brief hint
   - Run test: exact command
   - Expected: 5 tests pass

6. **Run It** (3 steps)
   - Run all tests (exact command + expected "20 passed")
   - Run full system (exact command)
   - Try `--cached` mode

7. **Submit** (3 steps)
   - Write reflection in `report.md`
   - Git add, commit, push
   - Verify

---

## 7. Supporting Files

### `.env.example`
```
OLLAMA_BASE_URL=http://localhost:11434
MODEL_NAME=qwen3.5:4b
MODEL_TEMPERATURE=0.3
REQUEST_TIMEOUT=30
```
(Node version uses `REQUEST_TIMEOUT=30000` for milliseconds)

### `.gitignore`
```
.env
__pycache__/
*.pyc
.venv/
node_modules/
.DS_Store
```

### `CLAUDE.md`
Project conventions for Claude Code and autowork agents:
- Dual-track repo: Python (`python/`) and Node (`node/`)
- Shared data in `data/`
- Python: async with httpx, rich, pytest, Python 3.11+
- Node: ESM (`"type": "module"`), native fetch, chalk, vitest, Node 20+
- Pattern files have TODO stubs — students implement core methods
- Tests use CachedLLMClient — must pass without Ollama
- Test commands: `cd python && pytest tests/ -v` / `cd node && npx vitest run`

### `README.md`
Brief lab overview:
- What is AgentForge
- Choose your track (Python or Node)
- Quickstart (3 commands)
- Link to full student guides in `docs/`
- Link to LAB_ACTION_GUIDE.md in each track

### `data/incidents.json`
The 4 incidents as specified in LAB_BUILD_INSTRUCTIONS.md (INC-001 through INC-004).

### `data/cached_responses.json`
The cached responses as specified in LAB_BUILD_INSTRUCTIONS.md — classification, chain, and parallel check responses.

### `report.md` (template in each track)
```markdown
# Module 2 Lab Report

## Patterns Implemented
- [ ] Sequential Chain
- [ ] Intent Router
- [ ] Parallel Fan-Out
- [ ] Orchestrator

## Metrics
- All tests passing: Yes/No
- Total test count: ___
- Average incident processing time: ___ms

## Reflection (200 words minimum)
1. Which pattern was hardest to implement? Why?
2. Where did the small model struggle? How did you work around it?
3. How would you modify this system for production use?
4. What's one thing you'd add to make this more robust?
```

---

## 8. GitHub Issues (Approach B — Issue-per-File)

### Tier 1: Foundation (must complete first)
1. **Initialize repo structure** — create directories, .gitignore, CLAUDE.md, README.md
2. **Create shared data files** — `data/incidents.json` + `data/cached_responses.json`

### Tier 2: Python Track (can parallelize)
3. **Python: LLM client** — `patterns/llm_client.py` with `LLMClient` + `CachedLLMClient`
4. **Python: Chain pattern** — `patterns/chain.py` with scaffolding + TODO stub
5. **Python: Router pattern** — `patterns/router.py` with scaffolding + TODO stub
6. **Python: Parallel pattern** — `patterns/parallel.py` with scaffolding + TODO stub
7. **Python: Orchestrator pattern** — `patterns/orchestrator.py` with scaffolding + TODO stub
8. **Python: Main entry point** — `agent_forge.py` + `verify_setup.py`
9. **Python: Test suite** — `tests/test_patterns.py` with 20 tests
10. **Python: Supporting files** — `requirements.txt`, `.env.example`, `report.md`, `patterns/__init__.py`
11. **Python: LAB_ACTION_GUIDE.md** — step-by-step student recipe

### Tier 3: Node Track (can parallelize)
12. **Node: LLM client** — `patterns/llm_client.js` with `LLMClient` + `CachedLLMClient`
13. **Node: Chain pattern** — `patterns/chain.js` with scaffolding + TODO stub
14. **Node: Router pattern** — `patterns/router.js` with scaffolding + TODO stub
15. **Node: Parallel pattern** — `patterns/parallel.js` with scaffolding + TODO stub
16. **Node: Orchestrator pattern** — `patterns/orchestrator.js` with scaffolding + TODO stub
17. **Node: Main entry point** — `agent_forge.js` + `verify_setup.js`
18. **Node: Test suite** — `tests/patterns.test.js` with 18 tests
19. **Node: Supporting files** — `package.json`, `.env.example`, `report.md`
20. **Node: LAB_ACTION_GUIDE.md** — step-by-step student recipe

### Tier 4: Polish
21. **Integration verification** — run both test suites end-to-end, verify `--cached` mode works

### Issue Dependencies
- All Tier 2 + 3 issues are blocked by Tier 1
- Within each track: LLM client must be done first; pattern files depend on it; tests depend on pattern files; entry point depends on all patterns
- Tier 4 blocked by all of Tier 2 + 3

---

## 9. Workflow

1. `git init` in `/Users/rob/projects/forge-module-2`
2. Create private repo at `arula-ai/forge-module-2`
3. Initial commit with docs + spec
4. Set up CLAUDE.md
5. Create all GitHub issues with labels and dependencies
6. **Pause** — hand off to autowork
