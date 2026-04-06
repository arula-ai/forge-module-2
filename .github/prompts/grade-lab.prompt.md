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
| Chain | [N]/4 pass | [details] | [N]/10 |
| Router | [N]/7 pass | [details] | [N]/12 |
| Parallel | [N]/4 pass | [details] | [N]/10 |
| Orchestrator | [N]/5 pass | [details] | [N]/13 |
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
