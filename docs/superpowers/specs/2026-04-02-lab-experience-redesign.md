# AgentForge Lab Experience Redesign — Design Specification

## Overview

Redesign the AgentForge Module 2 lab to deliver an exceptional hands-on learning experience for mixed-skill classrooms. Preserves all existing code and tests. Changes are concentrated in documentation, guides, test additions, and a new Copilot Chat grading agent.

**Goals:**
- Deeper understanding (not just green tests)
- Full parity between Python and Node tracks
- Resilience for struggling students, challenge for fast ones
- Engaging "wow factor" throughout
- Automated grading via GitHub Copilot Chat

**Constraints:**
- 110-minute lab session; students continue on their own afterward
- Mixed classroom: some breeze through, others struggle with basics
- Existing pattern files, entry points, and LLM client are unchanged
- Grading agent runs in GitHub Copilot Chat (IDE), not CLI

---

## 1. Track Parity — Node.js to Python Equivalence

### Problem

Node has 18 tests vs Python's 20. Node student guide is compressed, missing bonus challenges and the 100-point rubric. Students comparing tracks see inconsistency.

### Changes

#### 1.1 Add 2 Tests to Node (`node/tests/patterns.test.js`)

**Test 1: Chain error handling**
Add to the `DiagnosticChain` describe block:
```javascript
it('handles errors gracefully without crashing', async () => {
  const errorChain = new DiagnosticChain(llm);
  // Replace one step's prompt template to cause a format error
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

**Test 2: Classify returns confidence**
Add to the `IncidentRouter` describe block:
```javascript
it('classify returns confidence between 0 and 1', async () => {
  const result = await router.classify(incidents['INC-001']);
  expect(result.confidence).toBeGreaterThanOrEqual(0.0);
  expect(result.confidence).toBeLessThanOrEqual(1.0);
});
```

This brings Node to 20 tests, matching Python exactly: chain (4), router (7), parallel (4), orchestrator (5).

#### 1.2 Expand Node Student Guide (`docs/LAB_STUDENT_GUIDE_NODE.md`)

- Expand each pattern phase from ~2 pages to ~3-4 pages, matching Python's depth
- Add conceptual explanations for `Promise.allSettled` vs `asyncio.gather` — bridge Python concepts to JS equivalents
- Add "Key Concepts" boxes matching Python's structure
- Fix test count references throughout to match new 20-test total

#### 1.3 Add Bonus Challenges to Node Student Guide

Add section matching Python's 5 bonus challenges, adapted to JS:

1. **Retry Logic** — `async chatWithRetry(prompt, { system, maxRetries = 3 })` with decreasing temperature
2. **Severity Scorer** — Add a 4th chain step with `outputKey: 'severity_score'`
3. **Timeout Budgets** — Use `AbortSignal.timeout()` per stage in orchestrator
4. **Cost Tracker** — Accumulate token counts across LLM calls, print summary
5. **Model Swap** — Change `MODEL_NAME` in `.env`, compare output quality

#### 1.4 Add 100-Point Rubric to Node Student Guide

Identical structure to Python:

| Component | Points |
|-----------|--------|
| Chain execute() | 20 |
| Router classify() | 15 |
| Router route() | 10 |
| Parallel runAllChecks() | 15 |
| Parallel aggregate() | 10 |
| Orchestrator processIncident() | 20 |
| All tests pass | 10 |
| **Total** | **100** |

#### 1.5 Update Both Action Guides

**Python `LAB_ACTION_GUIDE.md`:**
- Add "Common mistake" callout in Orchestrator section: "Don't forget `import json` — you need it for `json.dumps(incident)`"
- Update all test count expectations to be explicit: "Expected: 4/4 chain, 7/7 router, 4/4 parallel, 5/5 orchestrator = 20 total"

**Node `LAB_ACTION_GUIDE.md`:**
- Add "Common mistake" callout: "ESM requires file extensions in imports — `import { foo } from './bar.js'` not `'./bar'`"
- Update all test count expectations to match new 20-test total
- Add note about `Promise.allSettled` returning `{ status, value/reason }` objects, not raw results

---

## 2. Differentiated Pacing for Mixed Classrooms

### Problem

Fast students finish early with nothing to do. Struggling students get stuck with no escape hatch. The facilitator becomes the bottleneck.

### Changes

#### 2.1 "If You're Stuck" Blocks

Add to both Student Guides AND Action Guides, after each pattern's test command. Decision-tree format — students match their error to a diagnosis:

**Chain:**
- `KeyError` on format → Check that `state.results[step.output_key]` uses the step's key, not a hardcoded string
- `results` dict is empty after execute → Your loop isn't storing results. Check `state.results[step.output_key] = result`
- Only 1-2 steps complete → Your error handling might be crashing the loop. Wrap each step in its own try/except, not one big try around the whole loop

**Router:**
- Classification returns `general/other` for everything → Your prompt probably doesn't include the incident description. Print your prompt to verify.
- `_match_category` returns OTHER → Check that you're passing `data.get("category", "")` not the whole response object
- `AttributeError` on `handler.handle` → Your handler lookup failed. Check `self.handlers.get(category, self.fallback_handler)`

**Parallel:**
- Tests hang or run very slowly → You're using `await` in a loop instead of `asyncio.gather`/`Promise.allSettled`. Create all tasks first, then await them together.
- One failure kills all checks → Add `return_exceptions=True` (Python) or use `Promise.allSettled` not `Promise.all` (Node)
- `_aggregate` returns wrong status → Check priority ordering: critical > error > warning > healthy. Use `if/elif` chain, not just the first status.

**Orchestrator:**
- `NameError`/`ReferenceError` on `classification` → Initialize all result variables as empty dicts/objects BEFORE the try blocks
- Only 1-2 stages run → Each stage needs its own independent try/except. Don't nest them.
- `ImportError` on `ChainState`/`create_chain_state` → Add the import: `from .chain import ChainState, create_chain_state` (Python) or `import { createChainState } from './chain.js'` (Node)

#### 2.2 "Stretch Goal" Boxes

Add to both Student Guides, at the end of each pattern phase. These deepen understanding of the current pattern (different from end-of-lab bonus challenges which add new features):

**Chain Stretch:**
"Add a 4th step that generates a severity score 1-10. Does your chain still work with 4 steps? Do the existing tests still pass? What would you need to add to `cached_responses.json` to make this work in cached mode?"

**Router Stretch:**
"What happens if you set `confidence_threshold` to 0.0? To 1.0? Try both. Can you write a test that verifies edge-case behavior at these extremes?"

**Parallel Stretch:**
"Add timing output showing wall-clock time for the parallel run. Then change your implementation to run checks sequentially (one at a time). Compare the wall-clock times. How much faster is the parallel version? (In cached mode they'll be similar — why?)"

**Orchestrator Stretch:**
"What happens if Stage 1 (classification) fails completely? Does Stage 2 (health checks) still run? Deliberately break `router.route()` by making it throw, then run the pipeline. Verify that your error handling lets the remaining stages continue."

---

## 3. Experiment Phase Redesign

### Problem

Phase 6 ("Experiments") says "change temperature and run again" with no clear learning objective. Students don't know what to observe or whether they succeeded.

### Changes

Replace the current experiment phase with three structured mini-experiments (3-4 minutes each). Add to both Student Guides as Phase 6.

#### Experiment 1: "Temperature and Confidence"

**Do:** Change `MODEL_TEMPERATURE` to `0.9` in `.env`. Run `python agent_forge.py --incident INC-001` / `node agent_forge.js --incident INC-001` (live mode, NOT cached).

**Observe:** Does the classification confidence change? Does the router pick a different handler? Run it 3 times — are the results consistent?

**Learn:** Temperature controls randomness. Higher temperature = less predictable classification = more fallback handler activations. This is why production systems use low temperature for structured tasks.

**Note:** "If you're in cached mode, nothing will change — cached responses are deterministic by design. That's exactly why we have a cached mode: reproducible results for testing."

#### Experiment 2: "Break and Recover"

**Do:** Comment out one stage in your `process_incident()` implementation (e.g., the health check stage — just skip calling `run_all_checks`). Run the full system with `--cached`.

**Observe:** Does the pipeline complete? What does the report look like with a missing stage? Is `stages_completed` shorter? Is `health_report` empty?

**Learn:** The orchestrator's try/except per stage means partial results are still useful. This is graceful degradation — a key production pattern. A broken health checker shouldn't prevent classification and diagnosis.

#### Experiment 3: "The Unknown Incident"

**Do:** Add INC-005 to `data/incidents.json`:
```json
{
  "id": "INC-005",
  "timestamp": "2026-01-15T20:15:00Z",
  "source": "security-scanner",
  "severity": "critical",
  "title": "Unauthorized API access — brute force detected",
  "description": "Security scanner detected 500 failed authentication attempts from IP 203.0.113.42 in the last 15 minutes. Target: /api/admin endpoint. No successful logins. Rate limiting not triggered. WAF rules not matching pattern.",
  "logs": "2026-01-15T20:00:00Z WARN  [auth] Failed login attempt for admin from 203.0.113.42\n2026-01-15T20:00:02Z WARN  [auth] Failed login attempt for admin from 203.0.113.42\n2026-01-15T20:05:00Z ERROR [security] 200 failed attempts from 203.0.113.42 in 5 minutes\n2026-01-15T20:10:00Z ERROR [security] 400 failed attempts — possible brute force\n2026-01-15T20:15:00Z CRITICAL [security] Rate limit threshold exceeded, IP not blocked"
}
```

Run classification on it (live mode or `--cached` — in cached mode the fallback will trigger).

**Observe:** Which category does it get routed to? Is there a handler for it? What does the fallback handler produce?

**Learn:** The router falls back to `general/other` for unknown incident types. In production, you'd add new handlers as new categories emerge. The system degrades gracefully rather than crashing on unknown input.

---

## 4. "What Success Looks Like" Examples

### Problem

Students see "Expected: 4 tests pass" but don't know what correct runtime output looks like vs. buggy output. They can't self-diagnose.

### Changes

#### 4.1 End-to-End Output Preview

Add a new section to each Student Guide, after setup and before Phase 2. Title: "What You'll Build — End to End".

Show the complete terminal output of a successful `agent_forge --cached --incident INC-001` run. Capture this by applying the reference solutions from the facilitator guide, running the command, and copying the output. Then revert to stubs. This is the destination — students see the full pipeline output before they start implementing. Include:
- The banner
- Stage 1 classification output with category and confidence
- Stage 2 health check results with status icons
- Stage 3 diagnostic chain with step completion
- The final report panel

Add note: "This is what your system will produce when all 4 patterns are implemented. Right now, every pattern raises NotImplementedError/throws Error. You'll build this one pattern at a time."

#### 4.2 Per-Phase Expected Output in Action Guides

After each test command, show two things:

**Green path (success):**
```
tests/test_patterns.py::TestDiagnosticChain::test_chain_has_three_steps PASSED
tests/test_patterns.py::TestDiagnosticChain::test_chain_execute_populates_state PASSED
tests/test_patterns.py::TestDiagnosticChain::test_chain_tracks_completed_steps PASSED
tests/test_patterns.py::TestDiagnosticChain::test_chain_handles_errors_gracefully PASSED

4 passed in 0.15s
```

**Common failure (diagnosis):**
```
FAILED test_chain_execute_populates_state
> assert "parsed_logs" in state.results
E AssertionError: assert "parsed_logs" in {}
```
One-line fix: "Empty results dict = your loop isn't storing results. Check `state.results[step.output_key] = result`"

Include both green and red examples for each phase (chain, router, parallel, orchestrator) with the most common failure mode for each.

---

## 5. Grading Agent — GitHub Copilot Chat

### Problem

No automated evaluation beyond "tests pass." Students self-report in `report.md` with no verification. Facilitators grade manually.

### Mechanism

The grading agent runs in GitHub Copilot Chat (VS Code / IDE). Students select a model (recommended: Claude Sonnet 4 or later), then ask Copilot to grade their lab.

**Files:**

1. **`.github/copilot-instructions.md`** — Project context for Copilot Chat. Describes the lab structure, both tracks, what students implement, and references the grading prompt.

2. **`grade-lab.prompt.md`** (in repo root) — The complete grading rubric and evaluation instructions. Copilot Chat prompt file that students reference. When a student asks "grade my lab" or opens this prompt file in Copilot Chat, the agent evaluates their work.

### Invocation

Student opens Copilot Chat in their IDE and says:

> "Grade my lab using the rubric in grade-lab.prompt.md"

Or attaches the prompt file directly to the chat context.

### Model Recommendation

The `grade-lab.prompt.md` header will state:

> "For best results, select **Claude Sonnet 4** or later in the Copilot Chat model dropdown. The rubric works with any frontier model but is tested against Sonnet 4."

### Evaluation Rubric — 4 Sections (100 Points)

#### 5.1 Technical Correctness (50 points)

The agent runs (or asks the student to run) the test suite and evaluates:

| Component | Tests | Points |
|-----------|-------|--------|
| Chain | 4 tests | 10 |
| Router | 7 tests | 12 |
| Parallel | 4 tests | 10 |
| Orchestrator | 5 tests | 13 |
| Full suite green (all 20) | — | 5 bonus |

Points are proportional: if 3/4 chain tests pass, award 7.5/10 (round to nearest integer).

#### 5.2 Code Quality (25 points)

The agent reads each pattern file and checks for specific implementation patterns:

**Chain (6 pts):**
- Uses `_format_prompt`/`formatPrompt` helper (not manual string concatenation) — 2 pts
- Has try/except per step (not one big try around the whole loop) — 2 pts
- Returns state at the end of the method — 2 pts

**Router (7 pts):**
- Builds category list dynamically from enum/object (not hardcoded string) — 2 pts
- Uses `_match_category`/`matchCategory` helper — 2 pts
- Checks confidence against threshold before handler selection — 2 pts
- Updates `handler_name` on fallback path — 1 pt

**Parallel (6 pts):**
- Uses `asyncio.gather`/`Promise.allSettled` (not sequential await in a loop) — 3 pts
- Handles exceptions from gather results (checks `isinstance(result, Exception)` or `outcome.status === 'rejected'`) — 2 pts
- Correct priority ordering in aggregate: critical > error > warning > healthy — 1 pt

**Orchestrator (6 pts):**
- Initializes all result variables before try blocks — 2 pts
- All 3 stages wrapped independently in try/except (not nested, not one big try) — 2 pts
- Uses `create_chain_state`/`createChainState` factory (not manual state construction) — 2 pts

#### 5.3 Report Quality (15 points)

The agent reads `report.md` and evaluates:

- All 4 pattern checkboxes marked — 2 pts
- Metrics section filled in with actual numbers (not placeholder `___`) — 3 pts
- All 4 reflection questions answered — 4 pts (1 per question)
- Reflection depth — 6 pts (subjective LLM evaluation):
  - References specific patterns by name (not generic "the patterns")
  - Mentions concrete challenges encountered during implementation
  - Proposes specific production improvements (not vague "make it better")
  - Shows evidence of understanding (why a pattern exists, not just what it does)

#### 5.4 Implementation Style (10 points)

Holistic LLM assessment:

- Consistent style: variable naming, error message format, spacing — 3 pts
- Appropriate use of provided helpers vs. reinventing them — 3 pts
- Clean code: no dead code, commented-out experiments, debugging artifacts — 2 pts
- Evidence of understanding vs. copy-paste — 2 pts. The agent compares student code against the facilitator guide reference solutions. Personalized variations (different error messages, additional logging, alternative prompt wording) score higher than verbatim matches.

### Output Format: `GRADE_REPORT.md`

The agent writes `GRADE_REPORT.md` to the track root directory (`python/` or `node/`).

```markdown
# Lab 2 Grade Report

**Track:** Python | **Date:** 2026-04-05 | **Total: 87/100**

## Technical Correctness (45/50)
| Component | Tests | Result | Points |
|-----------|-------|--------|--------|
| Chain | 4/4 pass | ✓ | 10/10 |
| Router | 7/7 pass | ✓ | 12/12 |
| Parallel | 4/4 pass | ✓ | 10/10 |
| Orchestrator | 4/5 pass | test_report_tracks_stages FAILED | 8/13 |
| Full suite bonus | 19/20 | — | 0/5 |

> Missing "complete" in stages_completed — likely forgot to append
> PipelineStage.COMPLETE.value after compiling the report.

## Code Quality (22/25)
| Pattern | Score | Notes |
|---------|-------|-------|
| Chain | 6/6 | ✓ All patterns correct |
| Router | 5/7 | Categories hardcoded as string literal, not built from enum |
| Parallel | 6/6 | ✓ Uses asyncio.gather correctly |
| Orchestrator | 5/6 | classification variable referenced outside try block scope |

## Report Quality (12/15)
- Checkboxes: 2/2
- Metrics filled: 3/3
- Questions answered: 4/4
- Reflection depth: 3/6 — Answers are brief, reference "the chain pattern"
  but don't explain why sequential execution matters. Production suggestions
  are generic ("add more error handling") rather than specific.

## Implementation Style (8/10)
- Consistency: 3/3
- Helper usage: 3/3
- Clean code: 1/2 — Debugging print statement left in chain.py line 47
- Understanding: 1/2 — Implementations closely match reference solutions
  with minimal personalization. Error messages are identical to guide examples.

---

**Strengths:** Strong technical execution. All core patterns work correctly.
Parallel implementation properly uses asyncio.gather with return_exceptions.

**Areas for improvement:** Router should build categories dynamically from
the IncidentCategory enum. Report reflections would benefit from specific
examples of where the small model struggled and concrete production changes.

*Graded by GitHub Copilot using the AgentForge Lab 2 rubric.*
*Model: Claude Sonnet 4 | Rubric version: 1.0*
```

### Files to Create

1. **`.github/copilot-instructions.md`** — Copilot project context
2. **`grade-lab.prompt.md`** — Full grading rubric as a Copilot Chat prompt file
3. **Add `GRADE_REPORT.md` to `.gitignore`** — grading output shouldn't be committed

---

## 6. Presentation Outline Updates

### Problem

The presentation outline doesn't reflect the new lab structure, differentiated pacing, experiment redesign, or grading agent.

### Changes to `docs/MODULE_2_PRESENTATION_OUTLINE.md`

#### 6.1 Lab Introduction Slide — Update

Add talking points about the new lab structure:
- "This lab is designed for all experience levels. Go at your own pace."
- "If you're stuck, look for the 'If You're Stuck' boxes — they diagnose common problems."
- "If you finish a pattern early, look for the 'Stretch Goal' box to go deeper."
- "Don't just get the tests green — understand why each pattern exists."

#### 6.2 New Slide: "The Lab Grader" — Add After Submission Section

Content:
- When you've completed the lab, open GitHub Copilot Chat
- Select Claude Sonnet 4 (or your preferred model) from the dropdown
- Ask: "Grade my lab using the rubric in grade-lab.prompt.md"
- Review your `GRADE_REPORT.md` — it evaluates:
  - Technical correctness (do tests pass?)
  - Code quality (did you use the right patterns?)
  - Report quality (did you reflect meaningfully?)
  - Implementation style (clean code, understanding vs copy-paste)

Facilitator note: "The grading agent is a teaching tool, not the final grade. Use its output as a conversation starter — 'The agent flagged X in your code, what do you think about that?'"

#### 6.3 Experiment Phase Talking Points — Update

Replace vague "change temperature and explore" with the three structured experiments:
1. Temperature and Confidence — "Watch how randomness affects classification"
2. Break and Recover — "See graceful degradation in action"
3. The Unknown Incident — "What happens with novel input?"

Add expected outcomes for each so facilitators can guide discussion.

#### 6.4 Facilitator Intervention Notes — Update

Add guidance for differentiated pacing:
- "At each phase checkpoint, scan the room. Students who finished early should be working on stretch goals, not idle."
- "Students stuck past the time marker: point them to the 'If You're Stuck' block first. Only intervene directly if the block doesn't resolve it."
- "The most common facilitator mistake is helping too quickly. The struggle is where learning happens. Give them 2-3 minutes with the 'If You're Stuck' guide before stepping in."

#### 6.5 Debrief Slide — Update

Add discussion question about the grading agent:
- "What did the grader catch that you missed?"
- "What would you add to the rubric?"
- "Is automated grading fair? What can it evaluate well, and what can't it?"

---

## 7. File Change Summary

### New Files
| File | Purpose |
|------|---------|
| `.github/copilot-instructions.md` | Copilot Chat project context |
| `grade-lab.prompt.md` | Grading rubric prompt file |

### Modified Files
| File | Changes |
|------|---------|
| `node/tests/patterns.test.js` | +2 tests (error handling, confidence) |
| `docs/LAB_STUDENT_GUIDE_NODE.md` | Expand phases, add bonuses, add rubric |
| `docs/LAB_STUDENT_GUIDE_PYTHON.md` | Add "If You're Stuck", stretch goals, experiments, success examples |
| `python/LAB_ACTION_GUIDE.md` | Add common mistakes, expected output examples, test counts |
| `node/LAB_ACTION_GUIDE.md` | Add common mistakes, expected output examples, test counts |
| `docs/LAB_FACILITATOR_GUIDE.md` | Reference grading agent, update experiment section |
| `docs/MODULE_2_PRESENTATION_OUTLINE.md` | New slides, updated talking points |
| `.gitignore` | Add GRADE_REPORT.md |

### Unchanged Files
All pattern files, LLM client, entry points, data files, and existing tests remain as-is.
