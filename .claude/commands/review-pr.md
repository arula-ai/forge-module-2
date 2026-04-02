# /review-pr — Expert PR Review Before Merge

Performs a comprehensive, expert-level code review of a pull request against its linked GitHub issue. This command MUST be run before any PR is auto-merged to ensure code quality, test coverage, and completeness.

**Zero-tolerance policy:** ALL findings (blockers, warnings, and suggestions) must be resolved before a PR can be approved. Only `info` observations are non-blocking.

## Usage
```
/review-pr                    # Review current branch's PR
/review-pr <pr-number>        # Review specific PR by number
```

## Review Process

```
┌──────────────────────────────────────────────────────────────┐
│                    PR REVIEW PIPELINE                         │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  1. CONTEXT GATHERING                                         │
│     ├── Read PR description and linked issue                  │
│     ├── Parse ALL acceptance criteria from issue               │
│     ├── List all changed files (git diff)                      │
│     └── Identify domain/track from labels                      │
│                                                               │
│  2. COMPLETENESS CHECK (vs. Issue)                             │
│     ├── Map each acceptance criterion to implementation         │
│     ├── Flag missing criteria as BLOCKER                       │
│     ├── Flag partial criteria as BLOCKER                        │
│     └── Verify no unrelated changes snuck in                   │
│                                                               │
│  3. CODE QUALITY REVIEW                                        │
│     ├── Architecture: follows CLAUDE.md conventions?           │
│     ├── Naming: snake_case (Python) / camelCase (Node)?        │
│     ├── Error handling: proper, not swallowed?                 │
│     ├── DRY: no unnecessary duplication?                       │
│     ├── Complexity: appropriate for the task?                  │
│     ├── Over-engineering: doing more than asked?               │
│     └── Student experience: is this clear and learnable?       │
│                                                               │
│  4. STUB & TODO SCAN                                           │
│     ├── Student TODO stubs MUST raise NotImplementedError/Error│
│     ├── TODO stubs MUST have pseudocode skeleton comments       │
│     ├── No other untracked TODO/FIXME without issue ref        │
│     └── Provided code MUST NOT contain stubs                   │
│                                                               │
│  5. TEST COVERAGE                                              │
│     ├── Test count matches spec (20 Python / 18 Node)?         │
│     ├── Tests use CachedLLMClient (no Ollama dependency)?      │
│     ├── Tests are deterministic?                               │
│     ├── Tests cover all pattern methods?                       │
│     └── Stack-specific validation passes?                      │
│                                                               │
│  6. SPEC CONFORMANCE                                           │
│     ├── Matches design spec exactly?                           │
│     ├── Data structures match spec (field names, types)?       │
│     ├── API matches spec (method signatures, return types)?    │
│     ├── Keyword matching logic matches spec?                   │
│     └── Prompt templates are well-crafted for Qwen3.5:4b?     │
│                                                               │
│  7. STUDENT EXPERIENCE CHECK                                   │
│     ├── TODO stubs are clear and well-guided?                  │
│     ├── Pseudocode comments are numbered and actionable?       │
│     ├── Provided code is readable and well-documented?         │
│     ├── imports/exports are clean and obvious?                 │
│     └── Terminal output is informative and visually appealing? │
│                                                               │
│  8. VERDICT                                                    │
│     ├── APPROVED — zero findings across all checks             │
│     └── REQUEST CHANGES — any finding at any severity          │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

## Detailed Algorithm

### Step 1: Context Gathering
```python
def gather_context(pr_number):
    pr = gh_pr_view(pr_number)
    issue_number = extract_issue_number(pr.body)  # "Closes #XX"
    issue = gh_issue_view(issue_number)
    criteria = parse_checkboxes(issue.body)
    changed_files = git_diff("main...HEAD", name_only=True)
    track = identify_track(issue.labels)  # "python" or "node"
    return {pr, issue, criteria, changed_files, track}
```

### Step 2: Completeness Check
```python
def check_completeness(criteria, changed_files):
    results = []
    for criterion in criteria:
        evidence = find_implementation_evidence(criterion, changed_files)
        if evidence.strong:
            results.append(("PASS", criterion, evidence.files))
        elif evidence.partial:
            results.append(("WARNING", criterion, f"Partial: {evidence.notes}"))
        else:
            results.append(("BLOCKER", criterion, "NOT IMPLEMENTED"))
    return results
```

### Step 3: Code Quality Review

For EACH changed file, review against these criteria:

**Python Track:**
- `dataclass` for all data structures (ChainState, ChainStep, etc.)
- Async-first: `async def` for all LLM-calling methods
- `rich.console.Console` for terminal output
- Proper error handling (try/except, append to errors list)
- Type hints on all public methods
- `from __future__ import annotations` if using forward references
- Keyword matching in CachedLLMClient is case-insensitive and top-to-bottom

**Node Track:**
- ESM throughout (`import/export`, `"type": "module"`)
- `chalk` v5 for colors (ESM import)
- `performance.now()` for timing
- `Promise.allSettled()` for parallel pattern
- `AbortSignal.timeout()` for fetch timeouts
- Proper error handling (try/catch)

### Step 4: Stub & TODO Scan

**Required for student TODO stubs:**
- `raise NotImplementedError("...")` (Python) or `throw new Error("...")` (Node)
- Pseudocode skeleton as numbered comments above the raise/throw
- Docstring explaining what the method should do

**BLOCK merge:**
- Student TODO method that doesn't raise/throw (silent no-op)
- Missing pseudocode skeleton
- Empty implementation body
- Untracked `TODO`/`FIXME` in provided (non-student) code

### Step 5: Test Coverage

Run stack-specific validation:

| Track | Validation Command |
|-------|-------------------|
| Python | `cd python && python -m pytest tests/ -v` |
| Node | `cd node && npx vitest run` |

Tests SHOULD fail with `NotImplementedError`/`Error` — that's correct behavior for student stubs.

### Step 6: Spec Conformance

Read `docs/superpowers/specs/2026-04-02-agentforge-lab-design.md` and verify:
- Data structure field names match exactly
- Method signatures match exactly
- CachedLLMClient keyword matching rules match Section 2
- Prompt templates are appropriate for Qwen3.5:4b (explicit JSON instructions, low ambiguity)
- Test count and names match Section 4

### Step 7: Student Experience Check

This is a TEACHING lab. The code must be:
- **Clear**: A student can read the provided code and understand what it does
- **Well-documented**: Docstrings on all classes and public methods
- **Consistent**: Naming, style, and patterns are uniform across all pattern files
- **Guiding**: TODO stubs tell students WHAT to do without telling them HOW

## Review Report Format

```
╔══════════════════════════════════════════════════════════════╗
║                    PR REVIEW REPORT                          ║
╠══════════════════════════════════════════════════════════════╣
║ PR: #<number> — <title>                                      ║
║ Issue: #<number> — <title>                                   ║
║ Branch: <branch-name>                                        ║
║ Files Changed: <count>                                       ║
║ Track: <python|node>                                         ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║ ── COMPLETENESS vs ISSUE ────────────────────────────────    ║
║ PASS Criterion 1: description                  [file.py:42]  ║
║ PASS Criterion 2: description                  [file.py:87]  ║
║ BLOCKER Criterion 3: description               NOT FOUND     ║
║                                                              ║
║ ── CODE QUALITY ─────────────────────────────────────────    ║
║ PASS Architecture: follows CLAUDE.md conventions             ║
║ PASS Naming: consistent with track conventions               ║
║                                                              ║
║ ── STUB/TODO SCAN ──────────────────────────────────────     ║
║ PASS Student stubs raise NotImplementedError                 ║
║ PASS Pseudocode skeletons present                            ║
║                                                              ║
║ ── TEST COVERAGE ────────────────────────────────────────    ║
║ PASS 20 tests defined                                        ║
║ PASS Tests use CachedLLMClient                               ║
║                                                              ║
║ ── SPEC CONFORMANCE ─────────────────────────────────────    ║
║ PASS Data structures match spec                              ║
║ PASS Method signatures match spec                            ║
║                                                              ║
║ ── STUDENT EXPERIENCE ───────────────────────────────────    ║
║ PASS Code is clear and well-documented                       ║
║ PASS TODO stubs are actionable                               ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║ VERDICT: APPROVED                                            ║
║ Findings: 0                                                  ║
╚══════════════════════════════════════════════════════════════╝
```

## Severity Levels

| Level | Meaning | Blocks Merge? |
|-------|---------|---------------|
| BLOCKER | Must fix. Missing feature, spec mismatch, broken test, bad student experience. | YES |
| WARNING | Must fix. Missing docstring, inconsistent style, unclear TODO stub. | YES |
| SUGGESTION | Must fix. Optimization, better prompt wording, improved error message. | YES |
| INFO | Observation only. No action needed. | NO |

## Integration with /autowork

The `/autowork` command MUST call `/review-pr` before merging ANY pull request. If review verdict is:
- **APPROVED** → merge PR (squash merge, delete branch)
- **REQUEST CHANGES** → fix all findings, re-review, then merge if approved

## Review Principles

1. **Completeness is king** — every acceptance criterion must be demonstrably met
2. **Spec is the source of truth** — code must match the design spec exactly
3. **Student experience matters** — this is a teaching lab, not just working code
4. **Tests prove it works** — tests must use CachedLLMClient and be deterministic
5. **Fix everything** — blockers, warnings, and suggestions must all be resolved
6. **Both tracks are equal** — same level of quality for Python and Node
