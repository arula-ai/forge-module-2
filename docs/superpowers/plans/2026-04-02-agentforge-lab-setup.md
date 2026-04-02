# AgentForge Lab — Repo Setup & Issue Creation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Initialize the forge-module-2 repo with foundation files, CLAUDE.md, GitHub remote, and detailed issues — then pause for autowork to build the lab.

**Architecture:** Git repo at `arula-ai/forge-module-2` (private). Foundation files (data, .gitignore, CLAUDE.md, README) are committed directly. All implementation work is described in GitHub issues for autowork agents. Issues are tiered: foundation → Python track → Node track → polish, with dependency labels.

**Tech Stack:** Git, GitHub CLI (`gh`), Claude Code (`claude`)

---

### Task 1: Git Init & Directory Structure

**Files:**
- Create: `.gitignore`
- Create: `python/patterns/.gitkeep` (placeholder for empty dirs)
- Create: `python/tests/.gitkeep`
- Create: `node/patterns/.gitkeep`
- Create: `node/tests/.gitkeep`
- Create: `data/.gitkeep`

- [ ] **Step 1: Initialize git repo**

```bash
cd /Users/rob/projects/forge-module-2
git init
```

Expected: `Initialized empty Git repository in /Users/rob/projects/forge-module-2/.git/`

- [ ] **Step 2: Create .gitignore**

Create `/Users/rob/projects/forge-module-2/.gitignore`:

```
# Environment
.env

# Python
__pycache__/
*.pyc
*.pyo
.venv/
*.egg-info/
dist/
build/

# Node
node_modules/

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp
*.swo
```

- [ ] **Step 3: Create directory structure with placeholders**

```bash
mkdir -p python/patterns python/tests node/patterns node/tests data
touch python/patterns/.gitkeep python/tests/.gitkeep node/patterns/.gitkeep node/tests/.gitkeep data/.gitkeep
```

- [ ] **Step 4: Initial commit**

```bash
git add .gitignore docs/ python/ node/ data/
git commit -m "chore: initialize repo with docs and directory structure"
```

Expected: Commit succeeds with docs/, .gitignore, and directory placeholders.

---

### Task 2: Create Shared Data Files

**Files:**
- Create: `data/incidents.json`
- Create: `data/cached_responses.json`

- [ ] **Step 1: Create incidents.json**

Create `/Users/rob/projects/forge-module-2/data/incidents.json` with the 4 sample incidents exactly as specified in `docs/LAB_BUILD_INSTRUCTIONS.md` lines 367-404 (INC-001 through INC-004).

- [ ] **Step 2: Create cached_responses.json**

Create `/Users/rob/projects/forge-module-2/data/cached_responses.json` with the cached responses exactly as specified in `docs/LAB_BUILD_INSTRUCTIONS.md` lines 416-484.

- [ ] **Step 3: Remove .gitkeep from data/**

```bash
rm data/.gitkeep
```

- [ ] **Step 4: Commit**

```bash
git add data/
git commit -m "feat: add shared incident data and cached responses"
```

---

### Task 3: Create CLAUDE.md

**Files:**
- Create: `CLAUDE.md`

- [ ] **Step 1: Create CLAUDE.md**

Create `/Users/rob/projects/forge-module-2/CLAUDE.md`:

```markdown
# CLAUDE.md — AgentForge Lab (Module 2)

## Project Overview

This is a teaching lab where students implement 4 agentic AI patterns (Chain, Router, Parallel, Orchestrator) in an incident response system. Two equivalent tracks: Python and Node.js.

## Repository Structure

- `python/` — Python track (Python 3.11+, async with httpx)
- `node/` — Node.js track (Node 20+, ESM with native fetch)
- `data/` — Shared incident data and cached responses (used by both tracks)
- `docs/` — Student guides, facilitator guide, presentation outline

## Key Design Decisions

- **Student TODO stubs**: Pattern files provide data structures, helpers, and pseudocode skeleton comments. Students implement core methods (marked with `raise NotImplementedError` / `throw new Error`). The loop/structure is given; API calls, error handling, and state management are left to the student.
- **CachedLLMClient**: Both tracks have a cached LLM client that returns deterministic responses from `data/cached_responses.json` via keyword matching. This is used for: (1) offline fallback via `--cached` CLI flag, (2) test suites so they pass without Ollama running.
- **Shared data**: `data/incidents.json` has 4 sample incidents. `data/cached_responses.json` has pre-built responses for all pattern operations. Both tracks reference these via `../data/`.

## Conventions

### Python Track (`python/`)
- Python 3.11+ with async/await
- HTTP client: `httpx` (async)
- Terminal output: `rich`
- Testing: `pytest` + `pytest-asyncio`
- Dependencies in `requirements.txt`
- Run tests: `cd python && python -m pytest tests/ -v`
- Run app: `cd python && python agent_forge.py` (or `--cached` for offline mode)
- Student config: copy `.env.example` to `.env`

### Node.js Track (`node/`)
- Node.js 20+ with ESM (`"type": "module"` in package.json)
- HTTP client: native `fetch`
- Terminal output: `chalk` v5 (ESM) + `ora` v8 (ESM)
- Testing: `vitest`
- Run tests: `cd node && npx vitest run`
- Run app: `cd node && node agent_forge.js` (or `--cached` for offline mode)
- Student config: copy `.env.example` to `.env`

### Pattern Files (Both Tracks)
Each pattern file has 3 layers:
1. **Data structures** (provided) — dataclasses/objects for state, results, configs
2. **Helper methods** (provided) — prompt formatting, display, single-check execution
3. **Core methods** (student TODO) — the main pattern logic with pseudocode skeleton

The 4 patterns and their student-implemented methods:
- `chain`: `execute(state)` — loop through steps, call LLM, accumulate state
- `router`: `classify(incident)` + `route(incident)` — classify and delegate
- `parallel`: `run_all_checks(incident)` + `_aggregate(results)` — fan-out and aggregate
- `orchestrator`: `process_incident(incident)` — compose all 3 patterns into pipeline

### LLM Client (`patterns/llm_client.*`)
- Wraps Ollama `/api/chat` endpoint
- `LLMClient` for live inference, `CachedLLMClient` for deterministic responses
- Students do NOT modify this file
- `CachedLLMClient` keyword matching: inspects prompt for domain keywords + context keywords ("status"/"health" for parallel checks, "classify" for router) to select cached response key

### Testing
- All tests use `CachedLLMClient` — they MUST pass without Ollama running
- Python: 20 tests across 4 test classes (chain: 4, router: 7, parallel: 4, orchestrator: 5)
- Node: 18 tests (same structure, 2 fewer)
- Tests verify pattern behavior, not LLM output quality

## Spec & Design Doc

Full design specification: `docs/superpowers/specs/2026-04-02-agentforge-lab-design.md`

## Important Notes

- Do NOT modify `patterns/llm_client.*` — it's provided to students as-is
- Pattern TODO stubs use pseudocode comments (numbered steps), NOT partial code
- The `agent_forge.*` entry point is provided to students — they don't modify it
- `.env.example` is checked in; `.env` is gitignored
- Each track has its own `LAB_ACTION_GUIDE.md` — a concise step-by-step recipe
```

- [ ] **Step 2: Commit**

```bash
git add CLAUDE.md
git commit -m "chore: add CLAUDE.md with project conventions"
```

---

### Task 4: Create README.md

**Files:**
- Create: `README.md`

- [ ] **Step 1: Create README.md**

Create `/Users/rob/projects/forge-module-2/README.md`:

```markdown
# AgentForge — Incident Response System

**Module 2 Lab: Core Agentic Patterns**

Build a multi-pattern AI agent system that processes simulated DevOps incidents using four core agentic patterns:

1. **Sequential Chain** — Multi-step diagnostic pipeline
2. **Intent Router** — Classify and delegate to specialist handlers
3. **Parallel Fan-Out** — Concurrent health checks with aggregation
4. **Orchestrator** — Compose all patterns into a unified system

Runs entirely on your laptop using Ollama with Qwen3.5:4b. No API keys required.

## Choose Your Track

| | Python | Node.js |
|---|--------|---------|
| Runtime | Python 3.11+ | Node.js 20+ |
| Guide | [Python Student Guide](docs/LAB_STUDENT_GUIDE_PYTHON.md) | [Node.js Student Guide](docs/LAB_STUDENT_GUIDE_NODE.md) |
| Action Guide | [Python Action Guide](python/LAB_ACTION_GUIDE.md) | [Node.js Action Guide](node/LAB_ACTION_GUIDE.md) |

## Quickstart

### Prerequisites

1. Install [Ollama](https://ollama.com/download)
2. Pull the model: `ollama pull qwen3.5:4b`
3. Start Ollama: `ollama serve`

### Python Track

```bash
cd python
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python verify_setup.py
```

### Node.js Track

```bash
cd node
npm install
cp .env.example .env
npm run verify
```

## Documentation

- [Build Instructions](docs/LAB_BUILD_INSTRUCTIONS.md) — Full setup guide
- [Facilitator Guide](docs/LAB_FACILITATOR_GUIDE.md) — Answer key and grading rubric
- [Presentation Outline](docs/MODULE_2_PRESENTATION_OUTLINE.md) — Instructor slides
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add README with quickstart and track links"
```

---

### Task 5: Create GitHub Remote Repository

- [ ] **Step 1: Create private repo on arula-ai org**

```bash
cd /Users/rob/projects/forge-module-2
gh repo create arula-ai/forge-module-2 --private --source=. --push
```

Expected: Repo created at `https://github.com/arula-ai/forge-module-2`, local branch pushed.

- [ ] **Step 2: Verify remote**

```bash
git remote -v
```

Expected: Shows `origin` pointing to `github.com/arula-ai/forge-module-2`.

---

### Task 6: Create GitHub Issue Labels

- [ ] **Step 1: Create labels for issue tiers and tracks**

```bash
gh label create "tier-1-foundation" --color "0E8A16" --description "Must complete before track work"
gh label create "tier-2-python" --color "3572A5" --description "Python track implementation"
gh label create "tier-3-node" --color "F1E05A" --description "Node.js track implementation"
gh label create "tier-4-polish" --color "D93F0B" --description "Final integration and verification"
gh label create "llm-client" --color "C5DEF5" --description "LLM client component"
gh label create "pattern-chain" --color "BFD4F2" --description "Sequential chain pattern"
gh label create "pattern-router" --color "BFD4F2" --description "Intent router pattern"
gh label create "pattern-parallel" --color "BFD4F2" --description "Parallel fan-out pattern"
gh label create "pattern-orchestrator" --color "BFD4F2" --description "Orchestrator pattern"
gh label create "testing" --color "FBCA04" --description "Test suite"
gh label create "docs" --color "0075CA" --description "Documentation"
gh label create "scaffolding" --color "E4E669" --description "Project structure and config"
```

---

### Task 7: Create Tier 1 Foundation Issues

- [ ] **Step 1: Issue #1 — Initialize repo structure**

This is already done (Task 1-4), so create the issue and immediately close it:

```bash
gh issue create --title "Initialize repo structure" \
  --label "tier-1-foundation,scaffolding" \
  --body "$(cat <<'EOF'
## Description
Create the base directory structure, .gitignore, CLAUDE.md, and README.md.

## Acceptance Criteria
- [ ] `python/`, `node/`, `data/`, `docs/` directories exist
- [ ] `.gitignore` covers .env, __pycache__, node_modules, .venv, .DS_Store
- [ ] `CLAUDE.md` documents project conventions for both tracks
- [ ] `README.md` has quickstart for both tracks

## Status
Already completed in initial setup commits.
EOF
)"
gh issue close 1 --reason completed
```

- [ ] **Step 2: Issue #2 — Create shared data files**

Also already done (Task 2), close it:

```bash
gh issue create --title "Create shared data files" \
  --label "tier-1-foundation,scaffolding" \
  --body "$(cat <<'EOF'
## Description
Create `data/incidents.json` with 4 sample incidents and `data/cached_responses.json` with pre-built LLM responses.

## Files
- Create: `data/incidents.json`
- Create: `data/cached_responses.json`

## Acceptance Criteria
- [ ] `incidents.json` has 4 incidents (INC-001 through INC-004) matching the spec in `docs/LAB_BUILD_INSTRUCTIONS.md`
- [ ] `cached_responses.json` has all response keys: classify_database, classify_billing, classify_network, classify_general, chain_parse, chain_analyze, chain_recommend, parallel_memory_check, parallel_cpu_check, parallel_disk_check, parallel_network_check
- [ ] Both files are valid JSON

## Status
Already completed in initial setup commits.
EOF
)"
gh issue close 2 --reason completed
```

---

### Task 8: Create Tier 2 Python Track Issues

- [ ] **Step 1: Issue #3 — Python: LLM client**

```bash
gh issue create --title "Python: LLM client (llm_client.py)" \
  --label "tier-2-python,llm-client" \
  --body "$(cat <<'EOF'
## Description
Create `python/patterns/llm_client.py` — the Ollama API wrapper that students use but do NOT modify. This is the foundation all pattern files depend on.

## Files
- Create: `python/patterns/llm_client.py`

## Spec Reference
See `docs/superpowers/specs/2026-04-02-agentforge-lab-design.md` Section 2.

## Implementation Details

### LLMResponse dataclass
- `content: str` — raw text response from the model
- `duration_ms: float` — how long the call took
- `as_json() -> dict` — parses `content` as JSON, raises `ValueError` if invalid JSON. Must strip markdown code fences (```json ... ```) before parsing, as small models often wrap JSON in fences.

### LLMClient class
- `__init__(base_url: str, model: str, temperature: float = 0.3, timeout: float = 30.0)`
- `async chat(prompt: str, system: str = "", temperature: float | None = None) -> LLMResponse`
  - POST to `{base_url}/api/chat` with `{"model": model, "messages": [...], "stream": false, "options": {"temperature": temp}}`
  - If `system` is provided, prepend a system message
  - Time the request and populate `duration_ms`
  - Use `httpx.AsyncClient` with the configured timeout

### CachedLLMClient class (extends LLMClient)
- `__init__(cache_path: str)` — loads JSON from `cache_path`
- `async chat(prompt, system="", temperature=None) -> LLMResponse`
  - Matches keywords in the prompt to select a cached response key
  - Keyword matching rules (evaluated top-to-bottom, first match wins):
    - "classify" + "database" → `classify_database`
    - "classify" + ("billing" or "payment" or "charge") → `classify_billing`
    - "classify" + ("network" or "gateway" or "503") → `classify_network`
    - "classify" + ("email" or "password") → `classify_general`
    - ("parse" or "log") + ("error" or "extract") → `chain_parse`
    - ("root cause" or "analyze") → `chain_analyze`
    - "recommend" → `chain_recommend`
    - "memory" + ("status" or "health" or "check") → `parallel_memory_check`
    - "cpu" + ("status" or "health" or "check") → `parallel_cpu_check`
    - "disk" + ("status" or "health" or "check") → `parallel_disk_check`
    - "network" + ("status" or "health" or "check") → `parallel_network_check`
    - Fallback: `{"error": "No cached response matched", "status": "unknown"}`
  - Returns `LLMResponse` with `content=json.dumps(matched_response)`, `duration_ms=1.0`
  - Keyword matching should be case-insensitive on the lowercased prompt

### Factory function
- `create_llm_client(cached: bool = False) -> LLMClient`
  - If `cached=True`, return `CachedLLMClient("../data/cached_responses.json")`
  - Otherwise, return `LLMClient` configured from environment variables (`OLLAMA_BASE_URL`, `MODEL_NAME`, `MODEL_TEMPERATURE`, `REQUEST_TIMEOUT`)
  - Load env with `dotenv`

## Acceptance Criteria
- [ ] `LLMClient.chat()` makes async POST to Ollama and returns `LLMResponse`
- [ ] `LLMResponse.as_json()` parses content, strips markdown fences
- [ ] `CachedLLMClient` returns correct cached response for each keyword pattern
- [ ] `CachedLLMClient` fallback returns generic error response for unmatched prompts
- [ ] `create_llm_client()` factory works for both cached and live modes
- [ ] File is well-documented with docstrings (students will read this to understand the API)
EOF
)"
```

- [ ] **Step 2: Issue #4 — Python: Chain pattern**

```bash
gh issue create --title "Python: Chain pattern (chain.py)" \
  --label "tier-2-python,pattern-chain" \
  --body "$(cat <<'EOF'
## Description
Create `python/patterns/chain.py` — the sequential chain pattern scaffolding with TODO stub for students.

## Dependencies
- Depends on: Python LLM client (#3)

## Files
- Create: `python/patterns/chain.py`

## Spec Reference
See `docs/superpowers/specs/2026-04-02-agentforge-lab-design.md` Section 3.1.

## Implementation Details

### Provided (fully implemented):

**ChainState dataclass:**
```python
@dataclass
class ChainState:
    incident_id: str
    raw_input: str
    logs: str
    results: dict = field(default_factory=dict)
    steps_completed: list = field(default_factory=list)
    errors: list = field(default_factory=list)
```

**ChainStep dataclass:**
```python
@dataclass
class ChainStep:
    name: str
    system_prompt: str
    user_prompt_template: str
    output_key: str
```

**DiagnosticChain class:**
- `__init__(self, llm: LLMClient)` — stores llm, calls `_build_steps()`
- `_build_steps() -> list[ChainStep]` — returns 3 steps:
  1. "Parse Logs" (output_key: `parsed_logs`) — system prompt: "You are a log analysis expert. Extract structured data from logs. Respond ONLY with JSON." User prompt template includes `{logs}` and asks for JSON with `errors_found`, `error_types`, `time_range`, `affected_services`.
  2. "Analyze Root Cause" (output_key: `root_cause`) — system prompt: "You are a root cause analysis expert. Respond ONLY with JSON." User prompt template includes `{parsed_logs}` from previous step and asks for `root_cause`, `impact`, `severity_assessment`.
  3. "Generate Recommendations" (output_key: `recommendations`) — system prompt: "You are a DevOps remediation expert. Respond ONLY with JSON." User prompt template includes `{root_cause}` and asks for `immediate_actions`, `investigation_steps`, `prevention`.
- `_format_prompt(template: str, state: ChainState) -> str` — uses `str.format_map()` with a dict containing `state.logs`, `state.raw_input`, and all entries from `state.results` (flattened as JSON strings).

**Factory function:**
- `create_chain_state(incident: dict) -> ChainState` — creates a ChainState from an incident dict

### Student TODO stub:

**`execute(self, state: ChainState) -> ChainState`** — with pseudocode skeleton:
```python
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
```

Use `from rich.console import Console; console = Console()` for terminal output in the provided methods.

## Acceptance Criteria
- [ ] `ChainState`, `ChainStep` dataclasses are correct
- [ ] `DiagnosticChain._build_steps()` returns 3 well-crafted steps with prompt templates
- [ ] `_format_prompt()` correctly interpolates state into templates
- [ ] `execute()` raises `NotImplementedError` with pseudocode skeleton in docstring/comments
- [ ] `create_chain_state()` factory works
- [ ] Imports from `llm_client` work correctly
EOF
)"
```

- [ ] **Step 3: Issue #5 — Python: Router pattern**

```bash
gh issue create --title "Python: Router pattern (router.py)" \
  --label "tier-2-python,pattern-router" \
  --body "$(cat <<'EOF'
## Description
Create `python/patterns/router.py` — the intent router pattern scaffolding with TODO stubs for students.

## Dependencies
- Depends on: Python LLM client (#3)

## Files
- Create: `python/patterns/router.py`

## Spec Reference
See `docs/superpowers/specs/2026-04-02-agentforge-lab-design.md` Section 3.2.

## Implementation Details

### Provided (fully implemented):

**IncidentCategory enum:**
```python
class IncidentCategory(str, Enum):
    DATABASE = "technical/database"
    NETWORK = "technical/network"
    BILLING = "billing/payment"
    EMAIL = "general/email"
    OTHER = "general/other"
```

**RouteResult dataclass:**
- `category: IncidentCategory`, `confidence: float`, `reasoning: str`, `handler_name: str`

**HandlerResponse dataclass:**
- `handler: str`, `summary: str`, `priority: str`, `escalation_needed: bool`

**IncidentHandler dataclass:**
- `name: str`, `category: IncidentCategory`, `system_prompt: str`
- `async handle(self, incident: dict) -> HandlerResponse` — calls LLM with handler-specific system prompt, parses response into HandlerResponse

**IncidentRouter class:**
- `__init__(self, llm: LLMClient, confidence_threshold: float = 0.6)`
- `_build_handlers() -> dict[IncidentCategory, IncidentHandler]` — creates 5 handlers:
  - Database Specialist, Network Specialist, Billing Specialist, Email Specialist, General Specialist (fallback)
- `fallback_handler` — the General Specialist handler
- `_match_category(raw: str) -> IncidentCategory` — fuzzy matches a string to IncidentCategory. Checks if the raw string contains keywords like "database", "network", "billing", "email". Falls back to OTHER.

### Student TODO stubs:

**`classify(self, incident: dict) -> RouteResult`:**
```python
async def classify(self, incident: dict) -> RouteResult:
    """Classify an incident into a category using the LLM.

    TODO: Implement incident classification.
        # 1. Build list of valid categories from IncidentCategory enum
        # 2. Construct prompt with incident title, description, severity
        # 3. Ask LLM to classify — request JSON with: category, confidence (0-1), reasoning
        # 4. Parse response, match category using self._match_category()
        # 5. Look up handler from self.handlers (fallback to self.fallback_handler)
        # 6. Return RouteResult with category, confidence, reasoning, handler_name
    """
    raise NotImplementedError("Implement classify — see pseudocode above")
```

**`route(self, incident: dict) -> tuple[RouteResult, HandlerResponse]`:**
```python
async def route(self, incident: dict) -> tuple[RouteResult, HandlerResponse]:
    """Classify an incident and route it to the appropriate handler.

    TODO: Implement routing logic.
        # 1. Call self.classify(incident) to get RouteResult
        # 2. If confidence >= self.confidence_threshold, select matching handler
        # 3. If confidence < threshold, use self.fallback_handler
        # 4. Call handler.handle(incident) to get HandlerResponse
        # 5. Return (RouteResult, HandlerResponse)
    """
    raise NotImplementedError("Implement route — see pseudocode above")
```

## Acceptance Criteria
- [ ] `IncidentCategory` enum has all 5 categories
- [ ] `IncidentHandler.handle()` calls LLM and returns `HandlerResponse`
- [ ] `_match_category()` fuzzy matches strings to categories
- [ ] `_build_handlers()` creates properly configured handlers
- [ ] `classify()` and `route()` raise `NotImplementedError` with pseudocode
- [ ] `confidence_threshold` defaults to 0.6
EOF
)"
```

- [ ] **Step 4: Issue #6 — Python: Parallel pattern**

```bash
gh issue create --title "Python: Parallel pattern (parallel.py)" \
  --label "tier-2-python,pattern-parallel" \
  --body "$(cat <<'EOF'
## Description
Create `python/patterns/parallel.py` — the parallel fan-out pattern scaffolding with TODO stubs.

## Dependencies
- Depends on: Python LLM client (#3)

## Files
- Create: `python/patterns/parallel.py`

## Spec Reference
See `docs/superpowers/specs/2026-04-02-agentforge-lab-design.md` Section 3.3.

## Implementation Details

### Provided (fully implemented):

**HealthCheck dataclass:**
- `name: str`, `subsystem: str`, `prompt_template: str`

**CheckResult dataclass:**
- `name: str`, `subsystem: str`, `status: str`, `details: str`, `duration_ms: float`

**HealthReport dataclass:**
- `results: list[CheckResult]`, `overall_status: str`, `total_duration_ms: float`, `summary: str`

**ParallelHealthChecker class:**
- `__init__(self, llm: LLMClient)` — stores llm, calls `_build_checks()`
- `_build_checks() -> list[HealthCheck]` — returns 4 checks:
  1. "Memory Analysis" (subsystem: "memory") — prompt asks LLM to assess memory health given incident context, respond with JSON: `{"status": "healthy|warning|critical", "usage_percent": <number>, "details": "<description>"}`
  2. "CPU Analysis" (subsystem: "cpu") — same format for CPU
  3. "Disk I/O Analysis" (subsystem: "disk") — same format for disk
  4. "Network Analysis" (subsystem: "network") — same format for network
- `async _run_single_check(self, check: HealthCheck, incident: dict) -> CheckResult` — formats the check's prompt template with incident data, calls LLM with system prompt "You are a system health check analyzer. Respond ONLY with JSON.", parses response, returns `CheckResult` with timing.

### Student TODO stubs:

**`run_all_checks(self, incident: dict) -> HealthReport`:**
```python
async def run_all_checks(self, incident: dict) -> HealthReport:
    """Run all health checks concurrently and return aggregated report.

    TODO: Implement parallel health check execution.
        # 1. Create a coroutine for each check: self._run_single_check(check, incident)
        # 2. Run ALL concurrently with asyncio.gather(*tasks, return_exceptions=True)
        # 3. Process results: if an item is an Exception, convert to CheckResult with status="error"
        # 4. Display results with status icons (✓ healthy, ⚠ warning, ✗ critical, ! error)
        # 5. Return self._aggregate(results, total_ms)
    """
    raise NotImplementedError("Implement run_all_checks — see pseudocode above")
```

**`_aggregate(self, results: list[CheckResult], total_ms: float) -> HealthReport`:**
```python
def _aggregate(self, results: list[CheckResult], total_ms: float) -> HealthReport:
    """Aggregate individual check results into an overall health report.

    TODO: Implement result aggregation.
        # 1. Collect all statuses from results
        # 2. Determine overall status (priority: critical > error > warning > healthy)
        # 3. Build summary string: "Overall: <status> | memory: <s>, cpu: <s>, ..."
        # 4. Return HealthReport with results, overall_status, total_duration_ms, summary
    """
    raise NotImplementedError("Implement _aggregate — see pseudocode above")
```

## Acceptance Criteria
- [ ] 4 health checks defined with proper prompt templates
- [ ] `_run_single_check()` calls LLM, times it, returns `CheckResult`
- [ ] `run_all_checks()` and `_aggregate()` raise `NotImplementedError` with pseudocode
- [ ] All dataclasses are correct
EOF
)"
```

- [ ] **Step 5: Issue #7 — Python: Orchestrator pattern**

```bash
gh issue create --title "Python: Orchestrator pattern (orchestrator.py)" \
  --label "tier-2-python,pattern-orchestrator" \
  --body "$(cat <<'EOF'
## Description
Create `python/patterns/orchestrator.py` — the orchestrator pattern scaffolding with TODO stub.

## Dependencies
- Depends on: Python LLM client (#3), Chain (#4), Router (#5), Parallel (#6)

## Files
- Create: `python/patterns/orchestrator.py`

## Spec Reference
See `docs/superpowers/specs/2026-04-02-agentforge-lab-design.md` Section 3.4.

## Implementation Details

### Provided (fully implemented):

**PipelineStage enum:**
```python
class PipelineStage(str, Enum):
    CLASSIFYING = "classifying"
    HEALTH_CHECK = "health_check"
    DIAGNOSING = "diagnosing"
    COMPLETE = "complete"
```

**IncidentReport dataclass:**
```python
@dataclass
class IncidentReport:
    incident_id: str
    title: str
    classification: dict
    handler_response: dict
    health_report: dict
    diagnostic_chain: dict
    total_duration_ms: float
    stages_completed: list[str]
    errors: list[str]
```

**IncidentOrchestrator class:**
- `__init__(self, router, health_checker, diagnostic_chain)` — stores all 3 pattern instances
- `_display_report(self, report: IncidentReport)` — renders a rich terminal report with:
  - Box border with incident ID and title
  - Classification section: category, confidence, handler
  - Health Report section: each check with status icon and timing
  - Diagnostic Chain section: step results
  - Timing and error summary
  - Uses `rich` Panel, Table, and Console for beautiful output

### Student TODO stub:

**`process_incident(self, incident: dict) -> IncidentReport`:**
```python
async def process_incident(self, incident: dict) -> IncidentReport:
    """Run the full incident response pipeline: classify, health check, diagnose.

    TODO: Implement the orchestration pipeline.
        # Initialize: start timer, empty lists for stages_completed and errors,
        #             empty dicts for classification, handler_response, health_report, chain_results

        # Stage 1: Classification & Routing
        # 1. Call self.router.route(incident)
        # 2. Extract classification dict: category (use .value for enum), confidence, reasoning, handler
        # 3. Extract handler_response dict: handler, summary, priority, escalation_needed
        # 4. Append PipelineStage.CLASSIFYING.value to stages_completed
        # 5. Wrap in try/except — on failure, append error message, don't stop pipeline

        # Stage 2: Parallel Health Checks
        # 6. Call self.health_checker.run_all_checks(incident)
        # 7. Extract health_report dict with results list and overall_status
        # 8. Append PipelineStage.HEALTH_CHECK.value to stages_completed
        # 9. Wrap in try/except

        # Stage 3: Diagnostic Chain
        # 10. Create ChainState from incident (use create_chain_state or build manually)
        # 11. Call self.diagnostic_chain.execute(state)
        # 12. Extract chain_results from state.results
        # 13. Append PipelineStage.DIAGNOSING.value to stages_completed
        # 14. Merge any chain errors into the errors list
        # 15. Wrap in try/except

        # Stage 4: Compile Report
        # 16. Append PipelineStage.COMPLETE.value
        # 17. Build IncidentReport with all collected data
        # 18. Call self._display_report(report)
        # 19. Return report
    """
    raise NotImplementedError("Implement process_incident — see pseudocode above")
```

Note: The orchestrator imports `ChainState` (or `create_chain_state`) from `chain.py` and `json` from stdlib.

## Acceptance Criteria
- [ ] `PipelineStage` enum and `IncidentReport` dataclass correct
- [ ] `_display_report()` renders beautiful rich terminal output
- [ ] `process_incident()` raises `NotImplementedError` with pseudocode
- [ ] Imports from chain, router, parallel modules are correct
EOF
)"
```

- [ ] **Step 6: Issue #8 — Python: Main entry point**

```bash
gh issue create --title "Python: Main entry point (agent_forge.py + verify_setup.py)" \
  --label "tier-2-python,scaffolding" \
  --body "$(cat <<'EOF'
## Description
Create the main CLI entry point and setup verification script for the Python track.

## Dependencies
- Depends on: All Python pattern files (#3-#7)

## Files
- Create: `python/agent_forge.py`
- Create: `python/verify_setup.py`

## Spec Reference
See `docs/superpowers/specs/2026-04-02-agentforge-lab-design.md` Section 5.
See `docs/LAB_BUILD_INSTRUCTIONS.md` lines 171-223 for verify_setup.py.

## Implementation Details

### agent_forge.py
- Uses `argparse` for CLI: `--incident <ID>` (optional), `--cached` (flag)
- Loads `.env` with `python-dotenv`
- Loads incidents from `../data/incidents.json`
- Creates LLM client via `create_llm_client(cached=args.cached)`
- Wires up: `DiagnosticChain(llm)`, `IncidentRouter(llm)`, `ParallelHealthChecker(llm)`, `IncidentOrchestrator(router, checker, chain)`
- If `--incident` specified, filters to that incident
- For each incident: `await orchestrator.process_incident(incident)`
- Prints summary at end with `rich`: total incidents, total time, errors
- Wraps in `asyncio.run(main())`

### verify_setup.py
- Implementation as specified in `docs/LAB_BUILD_INSTRUCTIONS.md` lines 172-223
- Checks Ollama connectivity, model availability, test inference
- Uses `httpx`, `dotenv`, `asyncio`

## Acceptance Criteria
- [ ] `python agent_forge.py` processes all 4 incidents
- [ ] `python agent_forge.py --incident INC-001` processes single incident
- [ ] `python agent_forge.py --cached` uses CachedLLMClient
- [ ] `python verify_setup.py` checks Ollama and reports status
- [ ] Both files have `if __name__ == "__main__"` guards
EOF
)"
```

- [ ] **Step 7: Issue #9 — Python: Test suite**

```bash
gh issue create --title "Python: Test suite (test_patterns.py)" \
  --label "tier-2-python,testing" \
  --body "$(cat <<'EOF'
## Description
Create the test suite with 20 tests that validate student implementations using the CachedLLMClient.

## Dependencies
- Depends on: All Python pattern files (#3-#7)

## Files
- Create: `python/tests/test_patterns.py`
- Create: `python/tests/__init__.py` (empty)

## Spec Reference
See `docs/superpowers/specs/2026-04-02-agentforge-lab-design.md` Section 4.

## Implementation Details

Use `pytest` + `pytest-asyncio`. All tests use `CachedLLMClient` loaded from `../../data/cached_responses.json`.

### Shared fixture (conftest or within file):
```python
@pytest.fixture
def cached_llm():
    return CachedLLMClient(Path(__file__).parent.parent.parent / "data" / "cached_responses.json")

@pytest.fixture
def incidents():
    with open(Path(__file__).parent.parent.parent / "data" / "incidents.json") as f:
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
```

### 20 Tests:

**TestDiagnosticChain (4):**
1. `test_chain_has_three_steps(chain)` — `assert len(chain.steps) == 3`
2. `test_chain_execute_populates_state(chain, incidents)` — run execute on INC-001, assert `"parsed_logs"`, `"root_cause"`, `"recommendations"` all in `state.results`
3. `test_chain_tracks_completed_steps(chain, incidents)` — after execute, `len(state.steps_completed) == 3`
4. `test_chain_handles_errors_gracefully(cached_llm, incidents)` — create a chain, replace one step's prompt template with something that will cause a bad response, execute, verify errors list is non-empty but chain didn't crash

**TestIncidentRouter (7):**
5. `test_classify_database_incident(router, incidents)` — classify INC-001, assert category is `IncidentCategory.DATABASE`
6. `test_classify_billing_incident(router, incidents)` — classify INC-002, assert `BILLING`
7. `test_classify_network_incident(router, incidents)` — classify INC-003, assert `NETWORK`
8. `test_classify_returns_confidence(router, incidents)` — classify INC-001, assert `0.0 <= result.confidence <= 1.0`
9. `test_route_returns_tuple(router, incidents)` — route INC-001, assert returns tuple of (RouteResult, HandlerResponse)
10. `test_route_selects_correct_handler(router, incidents)` — route INC-001, assert handler name contains "Database"
11. `test_low_confidence_uses_fallback(cached_llm, incidents)` — create router with `confidence_threshold=0.99`, route INC-001, assert handler is the fallback (General)

**TestParallelHealthChecker (4):**
12. `test_has_four_checks(health_checker)` — `assert len(health_checker.checks) == 4`
13. `test_run_all_checks_returns_health_report(health_checker, incidents)` — run on INC-001, assert returns HealthReport with 4 results
14. `test_aggregate_critical_status(health_checker)` — create CheckResults with one critical, call _aggregate, assert overall is "critical"
15. `test_aggregate_healthy_status(health_checker)` — create all-healthy CheckResults, call _aggregate, assert overall is "healthy"

**TestIncidentOrchestrator (5):**
16. `test_process_incident_returns_report(orchestrator, incidents)` — process INC-001, assert returns IncidentReport
17. `test_report_has_classification(orchestrator, incidents)` — process, assert `report.classification` is non-empty dict
18. `test_report_has_health_report(orchestrator, incidents)` — process, assert `report.health_report` is non-empty
19. `test_report_has_diagnostic_chain(orchestrator, incidents)` — process, assert `report.diagnostic_chain` is non-empty
20. `test_report_tracks_stages(orchestrator, incidents)` — process, assert `"complete"` in `report.stages_completed`

## Acceptance Criteria
- [ ] 20 tests defined across 4 test classes
- [ ] All tests use CachedLLMClient (no Ollama dependency)
- [ ] Tests are deterministic
- [ ] `cd python && python -m pytest tests/ -v` runs successfully (tests will FAIL until students implement patterns — that's correct)
- [ ] Test names clearly describe what they verify
EOF
)"
```

- [ ] **Step 8: Issue #10 — Python: Supporting files**

```bash
gh issue create --title "Python: Supporting files (requirements.txt, .env.example, __init__.py, report.md)" \
  --label "tier-2-python,scaffolding" \
  --body "$(cat <<'EOF'
## Description
Create supporting configuration and template files for the Python track.

## Files
- Create: `python/requirements.txt`
- Create: `python/.env.example`
- Create: `python/patterns/__init__.py`
- Create: `python/report.md`

## Implementation Details

### requirements.txt
```
httpx>=0.27.0
rich>=13.7.0
pydantic>=2.6.0
pytest>=8.0.0
pytest-asyncio>=0.23.0
python-dotenv>=1.0.0
```

### .env.example
```
OLLAMA_BASE_URL=http://localhost:11434
MODEL_NAME=qwen3.5:4b
MODEL_TEMPERATURE=0.3
REQUEST_TIMEOUT=30
```

### patterns/__init__.py
Export key classes for convenient imports:
```python
from .llm_client import LLMClient, CachedLLMClient, LLMResponse, create_llm_client
from .chain import DiagnosticChain, ChainState, ChainStep, create_chain_state
from .router import IncidentRouter, IncidentCategory, RouteResult, HandlerResponse
from .parallel import ParallelHealthChecker, HealthCheck, CheckResult, HealthReport
from .orchestrator import IncidentOrchestrator, IncidentReport, PipelineStage
```

### report.md
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

## Acceptance Criteria
- [ ] `pip install -r requirements.txt` succeeds
- [ ] `.env.example` has all required variables
- [ ] `__init__.py` exports all key classes (will fail to import until pattern files exist — that's expected)
- [ ] `report.md` has the reflection template
EOF
)"
```

- [ ] **Step 9: Issue #11 — Python: LAB_ACTION_GUIDE.md**

```bash
gh issue create --title "Python: LAB_ACTION_GUIDE.md" \
  --label "tier-2-python,docs" \
  --body "$(cat <<'EOF'
## Description
Create a concise, step-by-step action guide for the Python track. This is a linear recipe students follow top-to-bottom during the lab session.

## Dependencies
- Depends on: All Python track files (#3-#10)

## Files
- Create: `python/LAB_ACTION_GUIDE.md`

## Spec Reference
See `docs/superpowers/specs/2026-04-02-agentforge-lab-design.md` Section 6.
Reference `docs/LAB_STUDENT_GUIDE_PYTHON.md` for content (this is the condensed version).

## Implementation Details

Structure as a numbered checklist. Each phase has:
- File to open
- Method to implement (with 1-2 sentence hint, NOT full solution)
- Exact test command to run
- Expected result (e.g., "4 tests pass")

Phases:
1. **Setup** — clone, venv, install, copy .env, verify
2. **Chain** — implement `execute()` in `patterns/chain.py`, test with `python -m pytest tests/test_patterns.py::TestDiagnosticChain -v`
3. **Router** — implement `classify()` + `route()` in `patterns/router.py`, test with `python -m pytest tests/test_patterns.py::TestIncidentRouter -v`
4. **Parallel** — implement `run_all_checks()` + `_aggregate()` in `patterns/parallel.py`, test with `python -m pytest tests/test_patterns.py::TestParallelHealthChecker -v`
5. **Orchestrator** — implement `process_incident()` in `patterns/orchestrator.py`, test with `python -m pytest tests/test_patterns.py::TestIncidentOrchestrator -v`
6. **Run** — `python -m pytest tests/ -v` (all 20 pass), `python agent_forge.py --cached`, `python agent_forge.py`
7. **Submit** — write report.md, git add/commit/push

Keep it SHORT. No explanations of patterns. Just actions and expected results. Link to the full student guide for deeper understanding.

## Acceptance Criteria
- [ ] All commands are copy-paste ready
- [ ] Each phase lists exact file, method, test command, expected output
- [ ] Total length under 150 lines
- [ ] Links to full student guide for details
EOF
)"
```

---

### Task 9: Create Tier 3 Node Track Issues

- [ ] **Step 1: Issue #12 — Node: LLM client**

```bash
gh issue create --title "Node: LLM client (llm_client.js)" \
  --label "tier-3-node,llm-client" \
  --body "$(cat <<'EOF'
## Description
Create `node/patterns/llm_client.js` — the Ollama API wrapper for the Node.js track.

## Files
- Create: `node/patterns/llm_client.js`

## Spec Reference
See `docs/superpowers/specs/2026-04-02-agentforge-lab-design.md` Section 2.
Mirror the Python `llm_client.py` (#3) but with Node.js conventions.

## Implementation Details

### LLMResponse class
- `constructor(content, durationMs)` — stores raw text and timing
- `get content()` — returns raw text
- `get durationMs()` — returns timing
- `asJson()` — parses `content` as JSON, strips markdown fences (```json ... ```), throws Error on invalid

### LLMClient class
- `constructor({ baseUrl, model, temperature = 0.3, timeout = 30000 })`
- `async chat(prompt, { system = '', temperature = null } = {})` — returns LLMResponse
  - Uses native `fetch` to POST to `{baseUrl}/api/chat`
  - Body: `{ model, messages: [...], stream: false, options: { temperature } }`
  - Uses `AbortSignal.timeout(this.timeout)` for timeout
  - Times with `performance.now()`

### CachedLLMClient class (extends LLMClient)
- `constructor(cachePath)` — reads and parses JSON from cachePath
- Same keyword matching logic as Python version (case-insensitive, top-to-bottom, first match wins)
- Returns `LLMResponse` with `content = JSON.stringify(matchedResponse)`, `durationMs = 1.0`

### Factory function
- `export function createLLMClient({ cached = false } = {})` — reads from `process.env`, returns appropriate client
- Uses `dotenv/config` for env loading

All exports are named ESM exports.

## Acceptance Criteria
- [ ] Same behavior as Python version
- [ ] Uses native `fetch` (no axios/node-fetch)
- [ ] ESM exports (`export class`, `export function`)
- [ ] `asJson()` strips markdown fences
- [ ] CachedLLMClient keyword matching matches Python version
EOF
)"
```

- [ ] **Step 2: Issue #13 — Node: Chain pattern**

```bash
gh issue create --title "Node: Chain pattern (chain.js)" \
  --label "tier-3-node,pattern-chain" \
  --body "$(cat <<'EOF'
## Description
Create `node/patterns/chain.js` — mirrors Python chain.py with JS conventions.

## Dependencies
- Depends on: Node LLM client (#12)

## Files
- Create: `node/patterns/chain.js`

## Spec Reference
See `docs/superpowers/specs/2026-04-02-agentforge-lab-design.md` Section 3.1.
Mirror Python `chain.py` (#4) with camelCase and JS idioms.

## Implementation Details

Same structure as Python version:
- `ChainState` as a plain object (or class): `{ incidentId, rawInput, logs, results: {}, stepsCompleted: [], errors: [] }`
- `ChainStep` as plain object: `{ name, systemPrompt, userPromptTemplate, outputKey }`
- `DiagnosticChain` class with `_buildSteps()`, `_formatPrompt(template, state)`, and TODO `execute(state)`
- `createChainState(incident)` factory function
- Same 3 steps with same prompt templates (adapted for JS string interpolation)
- Uses `chalk` for colored console output instead of `rich`

Student TODO stub for `execute(state)`:
```javascript
async execute(state) {
    // TODO: Implement the chain execution loop.
    // For each step in this.steps:
    //   1. Build the prompt using this._formatPrompt(step.userPromptTemplate, state)
    //   2. Call the LLM: await this.llm.chat(prompt, { system: step.systemPrompt })
    //   3. Parse the JSON response using response.asJson()
    //   4. Store the result in state.results[step.outputKey]
    //   5. Track completion: state.stepsCompleted.push(step.name)
    //   6. Handle errors: push to state.errors, log, but don't crash the loop
    throw new Error('Implement the chain execution loop — see comments above');
}
```

## Acceptance Criteria
- [ ] Same behavior as Python chain.py
- [ ] camelCase throughout
- [ ] ESM exports
- [ ] Pseudocode comments in TODO stub
EOF
)"
```

- [ ] **Step 3: Issue #14 — Node: Router pattern**

```bash
gh issue create --title "Node: Router pattern (router.js)" \
  --label "tier-3-node,pattern-router" \
  --body "$(cat <<'EOF'
## Description
Create `node/patterns/router.js` — mirrors Python router.py with JS conventions.

## Dependencies
- Depends on: Node LLM client (#12)

## Files
- Create: `node/patterns/router.js`

## Spec Reference
See `docs/superpowers/specs/2026-04-02-agentforge-lab-design.md` Section 3.2.
Mirror Python `router.py` (#5) with camelCase and JS idioms.

## Implementation Details

- `IncidentCategory` as a frozen object: `{ DATABASE: 'technical/database', NETWORK: 'technical/network', BILLING: 'billing/payment', EMAIL: 'general/email', OTHER: 'general/other' }`
- `IncidentRouter` class with `_buildHandlers()`, `_matchCategory()`, `confidenceThreshold = 0.6`
- Handler objects with `name`, `category`, `systemPrompt`, and `async handle(incident)` method
- `handleIncident(llm, handler, incident)` module-level helper function
- `matchCategory(raw)` module-level fuzzy matcher

Student TODO stubs for `classify(incident)` and `route(incident)` with same pseudocode as Python version but JS syntax.

## Acceptance Criteria
- [ ] Same behavior as Python router.py
- [ ] Handlers call LLM and return handler response objects
- [ ] `matchCategory()` fuzzy matches strings
- [ ] Both TODO methods throw Error with pseudocode comments
EOF
)"
```

- [ ] **Step 4: Issue #15 — Node: Parallel pattern**

```bash
gh issue create --title "Node: Parallel pattern (parallel.js)" \
  --label "tier-3-node,pattern-parallel" \
  --body "$(cat <<'EOF'
## Description
Create `node/patterns/parallel.js` — mirrors Python parallel.py with JS conventions.

## Dependencies
- Depends on: Node LLM client (#12)

## Files
- Create: `node/patterns/parallel.js`

## Spec Reference
See `docs/superpowers/specs/2026-04-02-agentforge-lab-design.md` Section 3.3.
Mirror Python `parallel.py` (#6) with camelCase and JS idioms.

## Implementation Details

Same structure as Python:
- Plain objects for `HealthCheck`, `CheckResult`, `HealthReport`
- `ParallelHealthChecker` class with `_buildChecks()`, `_runSingleCheck(check, incident)`
- `runSingleCheck(llm, check, incident)` module-level helper
- Uses `Promise.allSettled()` instead of `asyncio.gather(return_exceptions=True)`
- Uses `performance.now()` for timing
- Uses `chalk` for colored output

Student TODO stubs for `runAllChecks(incident)` and `aggregate(results, totalMs)`.

Key JS difference: `Promise.allSettled` returns `[{status: 'fulfilled', value}, {status: 'rejected', reason}]` — the pseudocode should reference this.

## Acceptance Criteria
- [ ] Same behavior as Python parallel.py
- [ ] Uses `Promise.allSettled` (not `Promise.all`)
- [ ] `_runSingleCheck` / `runSingleCheck` works correctly
- [ ] TODO stubs reference `Promise.allSettled` in pseudocode
EOF
)"
```

- [ ] **Step 5: Issue #16 — Node: Orchestrator pattern**

```bash
gh issue create --title "Node: Orchestrator pattern (orchestrator.js)" \
  --label "tier-3-node,pattern-orchestrator" \
  --body "$(cat <<'EOF'
## Description
Create `node/patterns/orchestrator.js` — mirrors Python orchestrator.py with JS conventions.

## Dependencies
- Depends on: Node LLM client (#12), Chain (#13), Router (#14), Parallel (#15)

## Files
- Create: `node/patterns/orchestrator.js`

## Spec Reference
See `docs/superpowers/specs/2026-04-02-agentforge-lab-design.md` Section 3.4.
Mirror Python `orchestrator.py` (#7).

## Implementation Details

- `PipelineStage` frozen object (same values as Python enum)
- Report object with same fields as Python `IncidentReport`
- `IncidentOrchestrator` class with `constructor(router, healthChecker, diagnosticChain)`
- `displayReport(report)` — rich terminal output using `chalk` for colors, manual box drawing
- Student TODO stub for `processIncident(incident)` with same pseudocode structure
- Imports `createChainState` from `./chain.js`

## Acceptance Criteria
- [ ] Same behavior as Python orchestrator.py
- [ ] `displayReport()` produces formatted terminal output
- [ ] TODO stub has numbered pseudocode comments
- [ ] Imports from sibling modules work
EOF
)"
```

- [ ] **Step 6: Issue #17 — Node: Main entry point**

```bash
gh issue create --title "Node: Main entry point (agent_forge.js + verify_setup.js)" \
  --label "tier-3-node,scaffolding" \
  --body "$(cat <<'EOF'
## Description
Create the main CLI entry point and setup verification script for the Node.js track.

## Dependencies
- Depends on: All Node pattern files (#12-#16)

## Files
- Create: `node/agent_forge.js`
- Create: `node/verify_setup.js`

## Spec Reference
See `docs/superpowers/specs/2026-04-02-agentforge-lab-design.md` Section 5.
See `docs/LAB_BUILD_INSTRUCTIONS.md` lines 307-352 for verify_setup.js.

## Implementation Details

### agent_forge.js
- Parse CLI args manually (`process.argv`): `--incident <ID>`, `--cached`
- `import 'dotenv/config'` for env loading
- Load incidents from `../data/incidents.json` (use `fs.readFileSync` + `JSON.parse` or `import` with assert)
- Wire up all patterns with `createLLMClient({ cached })`
- Process incidents, print summary with `chalk`

### verify_setup.js
- As specified in `docs/LAB_BUILD_INSTRUCTIONS.md` lines 307-352
- Uses native `fetch`, `dotenv/config`

## Acceptance Criteria
- [ ] `node agent_forge.js` processes all incidents
- [ ] `node agent_forge.js --incident INC-001` processes single
- [ ] `node agent_forge.js --cached` uses cached client
- [ ] `node verify_setup.js` checks Ollama status
EOF
)"
```

- [ ] **Step 7: Issue #18 — Node: Test suite**

```bash
gh issue create --title "Node: Test suite (patterns.test.js)" \
  --label "tier-3-node,testing" \
  --body "$(cat <<'EOF'
## Description
Create the test suite with 18 tests for the Node.js track using vitest.

## Dependencies
- Depends on: All Node pattern files (#12-#16)

## Files
- Create: `node/tests/patterns.test.js`

## Spec Reference
See `docs/superpowers/specs/2026-04-02-agentforge-lab-design.md` Section 4.
Mirror Python test suite (#9) minus 2 tests (18 total).

## Implementation Details

Use `vitest` with `describe`/`it` blocks. Same fixture setup as Python but with JS:
- Load `../../data/incidents.json` and `../../data/cached_responses.json`
- Create `CachedLLMClient`, wire up all patterns

### 18 Tests (same as Python minus test_chain_handles_errors_gracefully and test_classify_returns_confidence):

**DiagnosticChain (3):** has three steps, execute populates state, tracks completed steps
**IncidentRouter (6):** classify database/billing/network, route returns array, route selects correct handler, low confidence uses fallback
**ParallelHealthChecker (4):** has four checks, runAllChecks returns report, aggregate critical, aggregate healthy
**IncidentOrchestrator (5):** process returns report, has classification, has health report, has diagnostic chain, tracks stages

## Acceptance Criteria
- [ ] 18 tests in vitest format
- [ ] `cd node && npx vitest run` works (tests fail until students implement — correct)
- [ ] Uses CachedLLMClient
- [ ] Deterministic
EOF
)"
```

- [ ] **Step 8: Issue #19 — Node: Supporting files**

```bash
gh issue create --title "Node: Supporting files (package.json, .env.example, report.md)" \
  --label "tier-3-node,scaffolding" \
  --body "$(cat <<'EOF'
## Description
Create supporting configuration and template files for the Node.js track.

## Files
- Create: `node/package.json`
- Create: `node/.env.example`
- Create: `node/report.md`

## Implementation Details

### package.json
```json
{
  "name": "agentforge-node",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "start": "node agent_forge.js",
    "start:cached": "node agent_forge.js --cached",
    "test": "vitest run",
    "test:watch": "vitest",
    "verify": "node verify_setup.js"
  },
  "dependencies": {
    "chalk": "^5.0.0",
    "ora": "^8.0.0",
    "dotenv": "^16.0.0"
  },
  "devDependencies": {
    "vitest": "^1.0.0"
  }
}
```

### .env.example
```
OLLAMA_BASE_URL=http://localhost:11434
MODEL_NAME=qwen3.5:4b
MODEL_TEMPERATURE=0.3
REQUEST_TIMEOUT=30000
```

### report.md
Same template as Python version (see #10).

## Acceptance Criteria
- [ ] `npm install` succeeds
- [ ] `"type": "module"` for ESM
- [ ] All scripts defined
- [ ] `.env.example` uses milliseconds for timeout (30000)
EOF
)"
```

- [ ] **Step 9: Issue #20 — Node: LAB_ACTION_GUIDE.md**

```bash
gh issue create --title "Node: LAB_ACTION_GUIDE.md" \
  --label "tier-3-node,docs" \
  --body "$(cat <<'EOF'
## Description
Create a concise, step-by-step action guide for the Node.js track.

## Dependencies
- Depends on: All Node track files (#12-#19)

## Files
- Create: `node/LAB_ACTION_GUIDE.md`

## Spec Reference
See `docs/superpowers/specs/2026-04-02-agentforge-lab-design.md` Section 6.
Reference `docs/LAB_STUDENT_GUIDE_NODE.md` for content.

## Implementation Details

Same structure as Python LAB_ACTION_GUIDE.md (#11) but with Node commands:
1. **Setup** — clone, `cd node`, `npm install`, copy .env, `npm run verify`
2. **Chain** — `patterns/chain.js`, implement `execute()`, `npx vitest run -- DiagnosticChain`
3. **Router** — `patterns/router.js`, `classify()` + `route()`, `npx vitest run -- IncidentRouter`
4. **Parallel** — `patterns/parallel.js`, `runAllChecks()` + `aggregate()`, `npx vitest run -- ParallelHealthChecker`
5. **Orchestrator** — `patterns/orchestrator.js`, `processIncident()`, `npx vitest run -- IncidentOrchestrator`
6. **Run** — `npx vitest run` (all 18 pass), `npm start`, `npm run start:cached`
7. **Submit** — report.md, git add/commit/push

## Acceptance Criteria
- [ ] All commands are copy-paste ready for Node.js track
- [ ] Under 150 lines
- [ ] Links to full Node student guide
EOF
)"
```

---

### Task 10: Create Tier 4 Polish Issue

- [ ] **Step 1: Issue #21 — Integration verification**

```bash
gh issue create --title "Integration verification: run both tracks end-to-end" \
  --label "tier-4-polish,testing" \
  --body "$(cat <<'EOF'
## Description
Final verification that both tracks work correctly end-to-end.

## Dependencies
- Depends on: All Python (#3-#11) and Node (#12-#20) issues

## Verification Steps

### Python Track
1. `cd python`
2. `python -m venv .venv && source .venv/bin/activate`
3. `pip install -r requirements.txt`
4. `cp .env.example .env`
5. `python -m pytest tests/ -v` — should show 20 tests, all FAIL (NotImplementedError) — this is correct
6. Implement all TODO methods with reference solutions from `docs/LAB_FACILITATOR_GUIDE.md`
7. `python -m pytest tests/ -v` — all 20 PASS
8. `python agent_forge.py --cached` — completes without error
9. Revert implementations back to NotImplementedError stubs

### Node Track
1. `cd node`
2. `npm install`
3. `cp .env.example .env`
4. `npx vitest run` — should show 18 tests, all FAIL — correct
5. Implement all TODO methods with reference solutions
6. `npx vitest run` — all 18 PASS
7. `node agent_forge.js --cached` — completes without error
8. Revert to stubs

### Cross-Track
- Both tracks reference `../data/incidents.json` and `../data/cached_responses.json` correctly
- `.gitignore` covers both tracks
- README links work
- LAB_ACTION_GUIDE.md files are accurate

## Acceptance Criteria
- [ ] Python: 20 tests fail with NotImplementedError, pass with reference solutions
- [ ] Node: 18 tests fail with Error, pass with reference solutions
- [ ] Both `--cached` modes work
- [ ] No broken imports or missing files
EOF
)"
```

---

### Task 11: Verify & Pause

- [ ] **Step 1: Verify all issues created**

```bash
gh issue list --state all --limit 25
```

Expected: 21 issues. Issues #1-#2 closed (already done). Issues #3-#21 open.

- [ ] **Step 2: Verify repo state**

```bash
git log --oneline
git remote -v
gh repo view arula-ai/forge-module-2 --json name,visibility
```

Expected: 3-4 commits, remote pointing to arula-ai/forge-module-2, visibility: private.

- [ ] **Step 3: Pause for autowork**

All foundation work is committed. 19 open issues are ready for autowork to pick up. The CLAUDE.md has all conventions needed for agents to implement correctly.

Report to user:
- Repo URL
- Issue count (open/closed)
- Recommended autowork order: start with LLM clients (#3, #12), then patterns, then tests/entry points, then action guides, finally integration (#21)
