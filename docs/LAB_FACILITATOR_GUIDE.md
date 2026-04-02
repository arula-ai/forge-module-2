# Lab 2: Core Agentic Patterns — Facilitator Guide & Answer Key

## 🔒 CONFIDENTIAL — Do Not Distribute to Students

---

## Quick Reference

| Item | Detail |
|------|--------|
| Lab Duration | 110 minutes (90 min working + 20 min buffer) |
| Test Count | 20 tests (Python) / 18 tests (Node) |
| Patterns | Chain → Router → Parallel → Orchestrator |
| Model | Qwen3.5:4b via Ollama (local) |
| Fallback | `--cached` flag for offline mode |
| Difficulty | Medium-High (pattern composition in Phase 5 is the challenge) |

---

## Timing Guide & Intervention Points

```
 0:00 - 0:20   SETUP — Must be complete by 0:20 or pair the student
 0:20 - 0:35   CHAIN — Watch for JSON parsing errors
 0:35 - 0:50   ROUTER — Watch for classification prompt quality
 0:50 - 1:05   PARALLEL — Watch for async/await mistakes
 1:05 - 1:20   ORCHESTRATOR — Most students need help here
 1:20 - 1:30   EXPERIMENTS — Let them play
 1:30 - 1:40   TESTS & SUBMIT — Make sure all tests pass
 1:40 - 1:50   BUFFER — Catch stragglers, help with bonus challenges
```

### Critical Intervention Points

**At 0:20** — If anyone isn't set up, pair them immediately. Don't let setup
consume lab time. Have the Codespaces/Gitpod fallback URL ready.

**At 0:35** — Check that everyone's chain is working. The most common issue
is the LLM returning prose instead of JSON. Fix: lower temperature to 0.1
and add "respond with ONLY JSON, no other text" to the system prompt.

**At 0:50** — The router is where prompt engineering skills matter. If the
model is misclassifying, help the student improve their classification prompt
by adding explicit category descriptions.

**At 1:05** — The orchestrator is the integration challenge. Most students
copy-paste from the guide but miss the `import json` or the `createChainState`
import. Verify imports first when debugging.

---

## Complete Reference Solutions

### Python: chain.py `execute()` — Full Answer

```python
async def execute(self, state: ChainState) -> ChainState:
    for step in self.steps:
        console.print(f"  [cyan]⏳ {step.name}...[/cyan]")
        
        try:
            prompt = self._format_prompt(step.user_prompt_template, state)
            response = await self.llm.chat(prompt, system=step.system_prompt)
            result = response.as_json()
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

**Grading Notes:**
- Full marks (20/20): Correct loop, JSON parsing, state storage, error handling
- Partial marks (15/20): Works but no error handling (crashes on bad JSON)
- Partial marks (10/20): Loop works but doesn't use `_format_prompt` or misses output_key
- Minimal marks (5/20): Attempts the pattern but doesn't produce working chain

---

### Python: router.py `classify()` — Full Answer

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

**Grading Notes:**
- Full marks (15/15): Lists categories in prompt, parses JSON, uses _match_category
- Common mistake: Hardcoding categories instead of iterating the enum
- Common mistake: Not handling missing keys in the JSON response (KeyError)

---

### Python: router.py `route()` — Full Answer

```python
async def route(self, incident: dict) -> tuple[RouteResult, HandlerResponse]:
    route_result = await self.classify(incident)
    
    console.print(
        f"  [cyan]🎯 Classified as {route_result.category.value}[/cyan] "
        f"[dim](confidence: {route_result.confidence:.0%})[/dim]"
    )
    
    if route_result.confidence >= self.confidence_threshold:
        handler = self.handlers.get(route_result.category, self.fallback_handler)
    else:
        console.print(
            f"  [yellow]⚠ Low confidence ({route_result.confidence:.0%}), "
            f"using fallback handler[/yellow]"
        )
        handler = self.fallback_handler
        route_result.handler_name = handler.name
    
    console.print(f"  [cyan]🔀 Routing to: {handler.name}[/cyan]")
    handler_response = await handler.handle(incident)
    
    return route_result, handler_response
```

**Grading Notes:**
- Full marks (10/10): Threshold check, fallback usage, handler delegation
- Critical test: `test_low_confidence_uses_fallback` — threshold is set to 0.99

---

### Python: parallel.py `run_all_checks()` — Full Answer

```python
async def run_all_checks(self, incident: dict) -> HealthReport:
    console.print("  [cyan]🔄 Running parallel health checks...[/cyan]")
    
    start = time.perf_counter()
    
    tasks = [
        self._run_single_check(check, incident)
        for check in self.checks
    ]
    
    raw_results = await asyncio.gather(*tasks, return_exceptions=True)
    
    total_ms = (time.perf_counter() - start) * 1000
    
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
    
    for r in results:
        icon = {"healthy": "✓", "warning": "⚠", "critical": "✗", "error": "!"}.get(r.status, "?")
        style = {"healthy": "green", "warning": "yellow", "critical": "red", "error": "red"}.get(r.status, "white")
        console.print(
            f"    [{style}]{icon} {r.name}[/{style}] "
            f"[dim]{r.details[:50]}  ({r.duration_ms:.0f}ms)[/dim]"
        )
    
    return self._aggregate(results, total_ms)
```

**Grading Notes:**
- Full marks (15/15): Uses `asyncio.gather`, handles exceptions, times correctly
- Common mistake: Using a loop with `await` instead of gather (sequential, not parallel)
- Common mistake: Forgetting `return_exceptions=True` — one failure kills all checks

---

### Python: parallel.py `_aggregate()` — Full Answer

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

**Grading Notes:**
- Full marks (10/10): Correct priority order (critical > error > warning > healthy)
- Common mistake: Not checking all statuses, only the first result

---

### Python: orchestrator.py `process_incident()` — Full Answer

```python
async def process_incident(self, incident: dict) -> IncidentReport:
    start = time.perf_counter()
    stages_completed = []
    errors = []
    
    classification = {}
    handler_response_data = {}
    health_report_data = {}
    chain_results = {}
    
    # Stage 1: Classify and Route
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
    
    # Stage 2: Parallel Health Checks
    console.print(f"\n  [bold]Stage 2: Health Checks[/bold]")
    try:
        health_report = await self.health_checker.run_all_checks(incident)
        health_report_data = {
            "results": [
                {"name": r.name, "status": r.status, "details": r.details, "duration_ms": r.duration_ms}
                for r in health_report.results
            ],
            "overall_status": health_report.overall_status,
        }
        stages_completed.append(PipelineStage.HEALTH_CHECK.value)
    except Exception as e:
        errors.append(f"Health checks failed: {str(e)[:100]}")
        console.print(f"  [red]✗ Health checks failed: {e}[/red]")
    
    # Stage 3: Diagnostic Chain
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
    
    # Compile Report
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

**Grading Notes:**
- Full marks (20/20): All 3 stages with try/catch, correct state compilation, report generation
- Partial marks (15/20): Stages work but one is missing error handling
- Partial marks (10/20): Only 1-2 stages implemented
- Common mistake: Not importing `json` module (needed for `json.dumps(incident)`)
- Common mistake: Trying to access `route_result.category` outside the try block

---

## Node.js Solutions

The Node.js solutions mirror the Python ones exactly. The key differences:

| Python | Node.js |
|--------|---------|
| `asyncio.gather(*tasks, return_exceptions=True)` | `Promise.allSettled(promises)` |
| `isinstance(result, Exception)` | `outcome.status === 'rejected'` |
| `time.perf_counter()` | `performance.now()` |
| `response.as_json()` | `response.asJson()` |
| `from .chain import ChainState` | `import { createChainState } from './chain.js'` |

For complete Node solutions, see the student guide — the implementations provided
there are the answer key.

---

## Grading Rubric (100 points)

### Quick Grading Checklist

```
□ Run: pytest tests/test_patterns.py -v (or npx vitest run)
□ Count passing tests: ___ / 20
□ Run: python agent_forge.py --cached (verify it completes)
□ Check report.md exists and has 200+ words
□ Review code for copy-paste vs understanding
```

### Detailed Rubric

| Component | Points | Auto-Grade | Manual Check |
|-----------|--------|------------|--------------|
| Chain execute() | 20 | 4 tests pass | Code quality |
| Router classify() | 15 | 3 tests pass | Prompt quality |
| Router route() | 10 | 2 tests pass | Threshold logic |
| Parallel runAllChecks() | 15 | 3 tests pass | Uses gather/allSettled |
| Parallel aggregate() | 10 | 1 test pass | Status priority correct |
| Orchestrator processIncident() | 20 | 5 tests pass | Error handling |
| All tests pass | 10 | 20/20 tests | — |
| **Total** | **100** | | |

### Automated Grading Script

```bash
#!/bin/bash
# grade_lab2.sh — Run from the student's project directory

echo "=== CGSE Module 2 Lab Grading ==="

# Run tests and capture output
TEST_OUTPUT=$(pytest tests/test_patterns.py -v 2>&1)
PASS_COUNT=$(echo "$TEST_OUTPUT" | grep -c "PASSED")
FAIL_COUNT=$(echo "$TEST_OUTPUT" | grep -c "FAILED")

echo "Tests passed: $PASS_COUNT"
echo "Tests failed: $FAIL_COUNT"

# Check report exists
if [ -f "report.md" ]; then
    WORD_COUNT=$(wc -w < report.md)
    echo "Report: $WORD_COUNT words"
else
    echo "Report: MISSING"
fi

# Check if system runs
timeout 60 python agent_forge.py --cached > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "System execution: PASS"
else
    echo "System execution: FAIL"
fi

echo "=========================="
```

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

---

## Common Student Issues & Solutions

### Issue 1: "JSON parse error" / Model returns prose

**Cause:** The model ignores the "respond ONLY with JSON" instruction.

**Fixes (in order of escalation):**
1. Lower temperature to 0.1: `MODEL_TEMPERATURE=0.1` in `.env`
2. Add "IMPORTANT: Your response must be valid JSON. No markdown, no explanation." to system prompt
3. Add JSON schema example directly in the prompt
4. Switch to cached mode and move on

### Issue 2: Router misclassifies incidents

**Cause:** Classification prompt is too vague.

**Fix:** Help the student add brief descriptions to each category:
```
Categories:
- technical/database: Database connections, queries, replication
- technical/network: Load balancers, DNS, gateways, 503/504 errors
- billing/payment: Charges, refunds, webhooks, payment processing
```

### Issue 3: Parallel checks run sequentially

**Cause:** Student used a `for` loop with `await` inside instead of `gather`/`allSettled`.

**Wrong:**
```python
for check in self.checks:
    result = await self._run_single_check(check, incident)  # Sequential!
```

**Right:**
```python
tasks = [self._run_single_check(check, incident) for check in self.checks]
results = await asyncio.gather(*tasks)  # Concurrent!
```

### Issue 4: Orchestrator crashes on first stage failure

**Cause:** Variables referenced outside try blocks.

**Fix:** Initialize all result variables before the try blocks:
```python
classification = {}  # Default empty dict
# ...then inside try: classification = {...}
```

### Issue 5: Tests pass with cached client but fail with live model

**Cause:** Non-deterministic model output.

**Response:** This is expected. Tests are designed for the cached client.
Explain that production tests would use mocking or evaluation metrics
rather than exact output matching.

### Issue 6: Students don't know what to do in the experiment phase

**Response:** Point them to the three structured experiments in the guide:
1. Temperature and Confidence — change MODEL_TEMPERATURE to 0.9, run 3 times
2. Break and Recover — comment out a stage, observe graceful degradation
3. The Unknown Incident — add INC-005 (security), observe fallback routing

---

## Adjusted Prompts for Qwen3.5:2b (Fallback Model)

If students use the smaller 2B model, some prompts need simplification.
The main change: be even more explicit about JSON format and reduce context.

**Chain step prompts — add to system prompt:**
```
CRITICAL: Output ONLY a JSON object. No text before or after.
```

**Router classification — simplify categories:**
```
Classify as ONE of: database, network, billing, email, other
```

**Parallel checks — reduce prompt length:**
Remove the "Respond with ONLY this JSON" examples and instead use:
```
Reply with JSON: {"status":"healthy|warning|critical","details":"one sentence"}
```

---

## Discussion Questions & Expected Answers (Debrief)

### Q1: "What surprised you most about the patterns?"

**Expected themes:**
- How simple each individual pattern is vs how powerful composition is
- That the model's limitations force better software design (focused prompts)
- The importance of error handling at every boundary
- How much the prompt quality affects output quality

### Q2: "Where would this break in production?"

**Strong answers include:**
- No persistent state (in-memory only) — needs Redis/DB
- Sequential processing by Ollama — needs model serving infrastructure
- No authentication or authorization
- No audit logging for compliance
- Rate limiting absent
- No retry with circuit breaker
- Hardcoded model name — needs model registry/cascade

### Q3: "How would you test this at scale?"

**Strong answers include:**
- Property-based testing for prompt robustness
- Evaluation suites with golden test sets (reference Module 2 lecture)
- Load testing with mock model to test concurrency handling
- A/B testing router accuracy across model versions
- Chaos engineering — inject failures at each stage

---

## Bonus Challenge Solutions (Brief)

### 1. Retry Logic
```python
async def chat_with_retry(self, prompt, system="", max_retries=3):
    for attempt in range(max_retries):
        try:
            temp = max(0.1, self.temperature - (attempt * 0.1))
            response = await self.chat(prompt, system=system, temperature=temp)
            response.as_json()  # Validate it's JSON
            return response
        except (json.JSONDecodeError, ValueError):
            if attempt == max_retries - 1:
                raise
```

### 2. Severity Scorer
Add a 4th ChainStep with outputKey `severity_score` and prompt:
```
Given the parsed logs, root cause, and recommendations, assign a severity 1-10.
Respond: {"score": <1-10>, "justification": "<reason>"}
```

### 3. Cost Tracker
Track `response.token_count` at each LLM call and accumulate in a global counter.
Print at the end: `Total tokens: X | Estimated cost at GPT-4 rates: $Y`

---

## Post-Lab: What to Watch For

After grading, look for patterns across the cohort:

1. **If >30% failed the chain**: Prompt templates may need more structure
2. **If >30% failed the router**: Classification prompt needs better examples
3. **If >30% failed parallel**: Need more asyncio/Promise teaching in lecture
4. **If orchestrator was universally hard**: Consider adding a simpler 2-stage
   orchestrator as an intermediate step before the full 3-stage version

Report these findings in the weekly instructor sync.

---

*Last updated: [Session Date] | Version: 1.0*
