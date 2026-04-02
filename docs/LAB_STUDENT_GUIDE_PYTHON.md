# Lab 2: Core Agentic Patterns — Student Guide (Python Track)

## CGSE-Advanced | Module 2 | Estimated Time: 110 minutes

---

## 🎯 What You're Building

**AgentForge** is an AI-powered incident response system that demonstrates the four
core agentic design patterns. When a DevOps incident is reported, your system will:

1. **Route** it to the right specialist using an intent classifier
2. **Chain** a multi-step diagnostic pipeline to analyze logs and recommend fixes
3. **Parallelize** health checks across memory, CPU, disk, and network
4. **Orchestrate** all three patterns into a unified pipeline with error handling

You'll run the entire system locally using **Qwen3.5:4b** via **Ollama** — no API keys,
no cloud, no cost.

**By the end of this lab, you'll see output like this in your terminal:**

```
╔═══════════════════════════════════════════════════════════╗
║  🚨 Incident Report: INC-001                             ║
║  Database connection pool exhausted                       ║
╠═══════════════════════════════════════════════════════════╣
║  🎯 Classification                                       ║
║     Category:   technical/database                        ║
║     Confidence: 95%                                       ║
║     Handler:    Database Specialist                        ║
║  🏥 System Health                                         ║
║     ✓ Memory Analysis    Normal at 68%           142ms    ║
║     ✓ CPU Analysis       Low at 34%              138ms    ║
║     ✓ Disk I/O Analysis  Normal parameters       151ms    ║
║     ⚠ Network Analysis   Elevated connections    147ms    ║
║  🔗 Diagnostic Chain                                      ║
║     parsed_logs → root_cause → recommendations            ║
╚═══════════════════════════════════════════════════════════╝
```

---

## 📋 Prerequisites

Before starting, verify:
- [ ] Ollama installed and running (`ollama serve`)
- [ ] Qwen3.5:4b model pulled (`ollama pull qwen3.5:4b`)
- [ ] Python 3.11+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)

Run the verification script to confirm everything works:
```bash
python verify_setup.py
```

---

## 📁 Project Structure

```
agentforge-python/
├── agent_forge.py              ← Main entry point (provided)
├── requirements.txt            ← Dependencies (provided)
├── verify_setup.py             ← Setup verification (provided)
├── .env                        ← Configuration (provided)
├── data/
│   ├── incidents.json          ← Sample incidents (provided)
│   └── cached_responses.json   ← Offline fallback (provided)
├── patterns/
│   ├── __init__.py             ← Package exports (provided)
│   ├── llm_client.py           ← Ollama API wrapper (provided — DO NOT MODIFY)
│   ├── chain.py                ← 🔨 YOU IMPLEMENT: execute()
│   ├── router.py               ← 🔨 YOU IMPLEMENT: classify() + route()
│   ├── parallel.py             ← 🔨 YOU IMPLEMENT: run_all_checks() + _aggregate()
│   └── orchestrator.py         ← 🔨 YOU IMPLEMENT: process_incident()
├── tests/
│   └── test_patterns.py        ← Test suite (provided)
└── report.md                   ← Your reflection (you write this)
```

**Files marked 🔨 contain `TODO` sections. Your job is to fill them in.**

---

## Phase 1: Environment Setup (20 minutes)

### 1.1 Clone and Set Up

```bash
# If using the lab repository:
git clone https://github.com/arula-ai/cgse-m02-lab.git
cd cgse-m02-lab/python

# Or if building from scratch, follow the Build Instructions document

python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 1.2 Verify Your Environment

```bash
python verify_setup.py
```

You should see all checks passing. If the model is slow to respond, that's normal
for the first call (model loading). Subsequent calls will be faster.

### 1.3 Explore the Codebase

Open the project in VS Code and spend 5 minutes reading:
1. `patterns/llm_client.py` — How we talk to Ollama (don't modify this)
2. `data/incidents.json` — The 4 incidents you'll process
3. `agent_forge.py` — The main entry point that ties everything together

**Key concept:** The `LLMClient.chat()` method returns an `LLMResponse` with:
- `.content` — The raw text response
- `.as_json()` — Parse content as JSON (throws if invalid)
- `.duration_ms` — How long the call took

---

## Phase 2: Build the Sequential Chain (15 minutes)

### 2.1 Understanding the Chain Pattern

Open `patterns/chain.py`. Read through the class structure:

- **`ChainState`** — A dataclass that flows through the chain, accumulating results
- **`ChainStep`** — Defines a single step: name, prompts, and output key
- **`DiagnosticChain`** — The chain itself with 3 pre-built steps

The three steps are already defined in `_build_steps()`:
1. **Parse Logs** → Extracts structured data from raw logs
2. **Analyze Root Cause** → Determines what went wrong
3. **Generate Recommendations** → Suggests fixes

### 2.2 Implement `execute()`

Find the `execute()` method. Replace the `raise NotImplementedError(...)` with
your implementation. Here's the pattern:

```python
async def execute(self, state: ChainState) -> ChainState:
    for step in self.steps:
        console.print(f"  [cyan]⏳ {step.name}...[/cyan]")
        
        try:
            # 1. Build the prompt using the helper method
            prompt = self._format_prompt(step.user_prompt_template, state)
            
            # 2. Call the LLM
            response = await self.llm.chat(prompt, system=step.system_prompt)
            
            # 3. Parse the JSON response
            result = response.as_json()
            
            # 4. Store in state
            state.results[step.output_key] = result
            state.steps_completed.append(step.name)
            
            console.print(
                f"  [green]✓ {step.name}[/green] "
                f"[dim]({response.duration_ms:.0f}ms)[/dim]"
            )
            
        except Exception as e:
            error_msg = f"{step.name} failed: {str(e)[:100]}"
            state.errors.append(error_msg)
            console.print(f"  [red]✗ {error_msg}[/red]")
    
    return state
```

### 2.3 Test the Chain

```bash
pytest tests/test_patterns.py::TestDiagnosticChain -v
```

All 4 chain tests should pass. If `test_chain_execute_populates_state` fails,
check that you're storing results using `step.output_key` as the dictionary key.

### 2.4 Key Concepts to Notice

- **State accumulation**: Each step can reference previous steps' output because
  `_format_prompt()` includes all of `state.results` in the template variables.
- **Error isolation**: A failure in Step 2 doesn't prevent Step 3 from running
  (if you handle errors correctly).
- **Observability**: Logging at each step creates a clear audit trail.

> 💡 **Think about it**: What happens if the LLM returns invalid JSON? How does
> your error handling deal with it? What would you do differently in production?

---

## Phase 3: Build the Router (15 minutes)

### 3.1 Understanding the Router Pattern

Open `patterns/router.py`. Read through:

- **`IncidentCategory`** — An enum of known incident types
- **`IncidentHandler`** — A specialist that processes one type of incident
- **`IncidentRouter`** — Classifies incidents and delegates to handlers

The handlers are pre-built in `_build_handlers()`. You need to implement the
classification and routing logic.

### 3.2 Implement `classify()`

This method sends the incident to the LLM and asks it to classify the category.

**Your classification prompt should:**
1. List all valid categories so the model knows its options
2. Include the incident title and description
3. Ask for a confidence score (0.0 to 1.0)
4. Request JSON output

```python
async def classify(self, incident: dict) -> RouteResult:
    categories_list = ", ".join(cat.value for cat in IncidentCategory)
    
    prompt = (
        f"Classify this incident into one of these categories: {categories_list}\n\n"
        f"Incident Title: {incident.get('title', 'N/A')}\n"
        f"Description: {incident.get('description', 'N/A')}\n"
        f"Severity: {incident.get('severity', 'unknown')}\n\n"
        "Respond with ONLY this JSON:\n"
        '{\n'
        '  "category": "<one of the categories listed above>",\n'
        '  "confidence": <number between 0.0 and 1.0>,\n'
        '  "reasoning": "<one sentence explaining your classification>"\n'
        '}'
    )
    
    response = await self.llm.chat(
        prompt,
        system="You are an incident classification expert. Classify accurately. Respond ONLY with JSON.",
    )
    
    data = response.as_json()
    category = self._match_category(data.get("category", ""))
    handler = self.handlers.get(category, self.fallback_handler)
    
    return RouteResult(
        category=category,
        confidence=float(data.get("confidence", 0.5)),
        reasoning=data.get("reasoning", "No reasoning provided"),
        handler_name=handler.name,
    )
```

### 3.3 Implement `route()`

This method combines classification with handler delegation:

```python
async def route(self, incident: dict) -> tuple[RouteResult, HandlerResponse]:
    # 1. Classify
    route_result = await self.classify(incident)
    
    console.print(
        f"  [cyan]🎯 Classified as {route_result.category.value}[/cyan] "
        f"[dim](confidence: {route_result.confidence:.0%})[/dim]"
    )
    
    # 2. Select handler based on confidence
    if route_result.confidence >= self.confidence_threshold:
        handler = self.handlers.get(route_result.category, self.fallback_handler)
    else:
        console.print(
            f"  [yellow]⚠ Low confidence ({route_result.confidence:.0%}), "
            f"using fallback handler[/yellow]"
        )
        handler = self.fallback_handler
        route_result.handler_name = handler.name
    
    # 3. Delegate to handler
    console.print(f"  [cyan]🔀 Routing to: {handler.name}[/cyan]")
    handler_response = await handler.handle(incident)
    
    return route_result, handler_response
```

### 3.4 Test the Router

```bash
pytest tests/test_patterns.py::TestIncidentRouter -v
```

All 7 router tests should pass. The most important one is
`test_low_confidence_uses_fallback` — it verifies your threshold logic works.

> 💡 **Think about it**: The classification prompt lists all categories. What if
> you had 50 categories? How would you handle that? (Hint: hierarchical routing)

---

## Phase 4: Build the Parallel Health Checker (15 minutes)

### 4.1 Understanding the Parallel Pattern

Open `patterns/parallel.py`. The key insight: we run 4 independent health checks
at the same time using `asyncio.gather()` instead of running them one by one.

The individual check execution (`_run_single_check`) is already implemented.
You need to implement the concurrent orchestration and aggregation.

### 4.2 Implement `run_all_checks()`

```python
async def run_all_checks(self, incident: dict) -> HealthReport:
    console.print("  [cyan]🔄 Running parallel health checks...[/cyan]")
    
    start = time.perf_counter()
    
    # 1. Create a coroutine for each check
    tasks = [
        self._run_single_check(check, incident)
        for check in self.checks
    ]
    
    # 2. Run ALL concurrently
    raw_results = await asyncio.gather(*tasks, return_exceptions=True)
    
    total_ms = (time.perf_counter() - start) * 1000
    
    # 3. Filter out exceptions, keep CheckResults
    results = []
    for i, result in enumerate(raw_results):
        if isinstance(result, Exception):
            results.append(CheckResult(
                name=self.checks[i].name,
                subsystem=self.checks[i].subsystem,
                status="error",
                details=f"Exception: {str(result)[:80]}",
                duration_ms=0,
            ))
        else:
            results.append(result)
    
    # 4. Display results
    for r in results:
        icon = {"healthy": "✓", "warning": "⚠", "critical": "✗", "error": "!"}.get(r.status, "?")
        style = {"healthy": "green", "warning": "yellow", "critical": "red", "error": "red"}.get(r.status, "white")
        console.print(
            f"    [{style}]{icon} {r.name}[/{style}] "
            f"[dim]{r.details[:50]}  ({r.duration_ms:.0f}ms)[/dim]"
        )
    
    return self._aggregate(results, total_ms)
```

### 4.3 Implement `_aggregate()`

```python
def _aggregate(self, results: list[CheckResult], total_ms: float) -> HealthReport:
    statuses = [r.status for r in results]
    
    if "critical" in statuses:
        overall = "critical"
    elif "error" in statuses:
        overall = "error"
    elif "warning" in statuses:
        overall = "warning"
    else:
        overall = "healthy"
    
    summary_parts = [f"{r.subsystem}: {r.status}" for r in results]
    summary = f"Overall: {overall} | " + ", ".join(summary_parts)
    
    console.print(
        f"  [cyan]📊 Health: [bold]{overall.upper()}[/bold] "
        f"({total_ms:.0f}ms total)[/cyan]"
    )
    
    return HealthReport(
        results=results,
        overall_status=overall,
        total_duration_ms=round(total_ms, 1),
        summary=summary,
    )
```

### 4.4 Test the Parallel Checker

```bash
pytest tests/test_patterns.py::TestParallelHealthChecker -v
```

### 4.5 Key Concepts to Notice

- **`asyncio.gather(*tasks, return_exceptions=True)`** — This is the magic. It
  launches all tasks concurrently and waits for all to complete. The
  `return_exceptions=True` flag means a failure in one check doesn't kill the others.

- **With a local model**, requests are actually processed sequentially by Ollama.
  But the concurrent structure still matters because: (a) it's the correct pattern
  for production with API models, (b) it handles timeouts and errors independently,
  and (c) the code is ready to scale.

> 💡 **Think about it**: Add `print(time.time())` at the start of each check.
> What ordering do you see? How would this differ with a cloud API?

---

## Phase 5: Build the Orchestrator (15 minutes)

### 5.1 Understanding the Orchestrator Pattern

Open `patterns/orchestrator.py`. The orchestrator composes all three patterns
into a pipeline with stage tracking and error recovery.

The `_display_report()` method is already implemented — it renders the beautiful
terminal output. You need to implement `process_incident()` which runs the pipeline.

### 5.2 Implement `process_incident()`

```python
async def process_incident(self, incident: dict) -> IncidentReport:
    start = time.perf_counter()
    stages_completed = []
    errors = []
    
    classification = {}
    handler_response_data = {}
    health_report_data = {}
    chain_results = {}
    
    # ── Stage 1: Classify and Route ──
    console.print(f"\n  [bold]Stage 1: Classification & Routing[/bold]")
    try:
        route_result, handler_response = await self.router.route(incident)
        classification = {
            "category": route_result.category.value,
            "confidence": route_result.confidence,
            "reasoning": route_result.reasoning,
            "handler": route_result.handler_name,
        }
        handler_response_data = {
            "handler": handler_response.handler,
            "summary": handler_response.summary,
            "priority": handler_response.priority,
            "escalation_needed": handler_response.escalation_needed,
        }
        stages_completed.append(PipelineStage.CLASSIFYING.value)
    except Exception as e:
        errors.append(f"Classification failed: {str(e)[:100]}")
        console.print(f"  [red]✗ Classification failed: {e}[/red]")
    
    # ── Stage 2: Parallel Health Checks ──
    console.print(f"\n  [bold]Stage 2: Health Checks[/bold]")
    try:
        health_report = await self.health_checker.run_all_checks(incident)
        health_report_data = {
            "results": [
                {
                    "name": r.name,
                    "status": r.status,
                    "details": r.details,
                    "duration_ms": r.duration_ms,
                }
                for r in health_report.results
            ],
            "overall_status": health_report.overall_status,
        }
        stages_completed.append(PipelineStage.HEALTH_CHECK.value)
    except Exception as e:
        errors.append(f"Health checks failed: {str(e)[:100]}")
        console.print(f"  [red]✗ Health checks failed: {e}[/red]")
    
    # ── Stage 3: Diagnostic Chain ──
    console.print(f"\n  [bold]Stage 3: Diagnostic Chain[/bold]")
    try:
        chain_state = ChainState(
            incident_id=incident["id"],
            raw_input=json.dumps(incident),
            logs=incident.get("logs", ""),
        )
        chain_state = await self.diagnostic_chain.execute(chain_state)
        chain_results = chain_state.results
        stages_completed.append(PipelineStage.DIAGNOSING.value)
        if chain_state.errors:
            errors.extend(chain_state.errors)
    except Exception as e:
        errors.append(f"Diagnostic chain failed: {str(e)[:100]}")
        console.print(f"  [red]✗ Diagnostic chain failed: {e}[/red]")
    
    # ── Stage 4: Compile Report ──
    total_ms = (time.perf_counter() - start) * 1000
    stages_completed.append(PipelineStage.COMPLETE.value)
    
    report = IncidentReport(
        incident_id=incident["id"],
        title=incident.get("title", "Unknown"),
        classification=classification,
        handler_response=handler_response_data,
        health_report=health_report_data,
        diagnostic_chain=chain_results,
        total_duration_ms=round(total_ms, 1),
        stages_completed=stages_completed,
        errors=errors,
    )
    
    self._display_report(report)
    return report
```

### 5.3 Add the Missing Import

At the top of `orchestrator.py`, you'll need:
```python
import json
```
(It's already there in the provided file, but double-check.)

### 5.4 Test the Orchestrator

```bash
pytest tests/test_patterns.py::TestIncidentOrchestrator -v
```

### 5.5 Run the Full System

```bash
# Process all 4 incidents
python agent_forge.py

# Or process just one
python agent_forge.py --incident INC-001

# If Ollama is giving trouble, use cached mode
python agent_forge.py --cached
```

Watch the terminal come alive with colored output as each pattern executes!

---

## Phase 6: Run Full System & Experiments (10 minutes)

### 6.1 Process All Incidents

```bash
python agent_forge.py
```

Watch how each incident gets classified differently, routed to different specialists,
and produces different diagnostic results.

### 6.2 Experiment: Change the Temperature

In your `.env` file, try changing `MODEL_TEMPERATURE=0.3` to `MODEL_TEMPERATURE=0.9`.
Run again. Notice the difference in classification confidence and recommendation creativity.

### 6.3 Experiment: Add a New Incident

Create a new incident in `data/incidents.json`:
```json
{
  "id": "INC-005",
  "timestamp": "2026-01-15T18:00:00Z",
  "source": "security-scanner",
  "severity": "critical",
  "title": "Unusual login patterns detected",
  "description": "Security scanner flagged 500 failed login attempts from 3 IP addresses targeting admin accounts in the last 15 minutes.",
  "logs": "2026-01-15T17:45:00Z WARN [auth] 50 failed logins for admin@company.com from 45.33.22.11"
}
```

Run again and observe how the router classifies it. Does it pick the right handler?

---

## Phase 7: Run Tests & Submit (10 minutes)

### 7.1 Run the Full Test Suite

```bash
pytest tests/test_patterns.py -v
```

All 20 tests should pass. If any fail, read the error message — it usually points
to exactly what's missing.

### 7.2 Write Your Reflection

Create or edit `report.md`:

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

### 7.3 Submit

```bash
git add -A
git commit -m "feat: complete Module 2 lab - all 4 agentic patterns"
git push origin main
```

---

## 🏆 Bonus Challenges

Finished early? Try these:

1. **Add Retry Logic** — If the LLM returns invalid JSON, retry up to 3 times
   with a lower temperature each time.

2. **Implement a Severity Scorer** — Add a 4th step to the diagnostic chain that
   assigns a numerical severity score (1-10) based on all previous analysis.

3. **Add Timeouts** — Set a 10-second timeout per LLM call. If it times out,
   use a fallback response and log a warning.

4. **Create a Cost Tracker** — Count tokens across all LLM calls and print a
   "cost report" at the end showing which stage used the most tokens.

5. **Swap the Model** — Try `ollama pull qwen3:4b` or `ollama pull gemma3:4b` and change your `.env`.
   How do the results compare to Qwen3.5?

---

## 🔑 Success Criteria

| Criteria | Points |
|----------|--------|
| Chain `execute()` works correctly | 20 |
| Router `classify()` returns accurate categories | 15 |
| Router `route()` handles confidence thresholds | 10 |
| Parallel `run_all_checks()` runs concurrently | 15 |
| Parallel `_aggregate()` determines correct status | 10 |
| Orchestrator `process_incident()` runs full pipeline | 20 |
| All 20 tests pass | 10 |
| **Total** | **100** |

---

## 📚 Key Vocabulary

| Term | Definition |
|------|-----------|
| **Chain** | Sequential pipeline where output of step N is input to step N+1 |
| **Router** | Classifier that delegates to specialized handlers |
| **Fan-Out** | Launching multiple tasks concurrently |
| **Aggregation** | Combining parallel results into a unified output |
| **Orchestrator** | Controller that composes multiple patterns |
| **State** | Accumulated data flowing through a pipeline |
| **Circuit Breaker** | Pattern that stops calling a failing service |
| **Graceful Degradation** | Continuing with partial results when one part fails |
