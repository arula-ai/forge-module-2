# /autowork - Fully Autonomous Development Loop

Runs a complete autonomous development loop that works through all open issues, using the correct domain expertise, following the full workflow, until all issues are completed.

## CARDINAL RULE: NEVER STOP AUTONOMOUSLY

You MUST continue working issue after issue without pausing, asking for confirmation, or waiting for user input. The only valid exit conditions are:

1. **No more open issues** — `gh issue list --state open` returns empty
2. **Explicit user command** — user types "stop", "pause", or interrupts the session
3. **Unrecoverable blocker** — after 3 retries an issue cannot be completed (skip it, log it, continue to next)

**Everything else — finish an issue, merge a PR, hit an error, need context — keep going.**

Do NOT:
- Stop after completing one issue and wait
- Ask "should I continue?" or "ready for the next one?"
- Pause between issues for any reason
- Output a session summary and stop (only output summary when truly done or explicitly stopped)

After merging a PR: immediately fetch the next open issue and start working it.

## Usage
```
/autowork                           # Work all open issues
/autowork --label tier-2-python     # Work only Python track issues
/autowork --label tier-3-node       # Work only Node track issues
/autowork --dry-run                 # Show plan without executing
/autowork --max-issues 5            # Limit to 5 issues per session
/autowork --resume                  # Resume interrupted session
```

## Model Routing

Each phase of the autowork loop should use the model best suited to the cognitive demands of that phase. Use the `model` parameter on Agent tool calls and subagents to enforce this.

### Phase-to-Model Matrix

| Phase | Model | Rationale |
|-------|-------|-----------|
| **Issue parsing & planning** | `opus` | Deep comprehension of requirements, acceptance criteria, and cross-issue dependencies |
| **Implementation (high complexity)** | `opus` | LLM client, test suite — core infrastructure with subtle keyword matching and fixture design |
| **Implementation (standard complexity)** | `sonnet` | Pattern scaffolding, entry points, config files — well-patterned work |
| **Test writing** | `sonnet` | Structured, pattern-driven; follows established test conventions |
| **Lint/format fixes** | `haiku` | Mechanical fixes |
| **PR review (`/review-pr`)** | `opus` | Requires judgment: correctness, completeness, student experience quality |
| **Review fix implementation** | `sonnet` | Targeted, scoped changes |
| **Commit message generation** | `haiku` | Formulaic — scope, summary, issue ref |

### Complexity-Based Routing

| Domain | Complexity | Model |
|--------|-----------|-------|
| `llm-client` | high | opus |
| `testing` | high | opus |
| `pattern-chain` | standard | sonnet |
| `pattern-router` | standard | sonnet |
| `pattern-parallel` | standard | sonnet |
| `pattern-orchestrator` | standard | sonnet |
| `scaffolding` | standard | sonnet |
| `docs` | standard | sonnet |

## Complete Autonomous Loop

```
┌─────────────────────────────────────────────────────────────┐
│                    AUTOWORK MAIN LOOP                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────┐    ┌──────────────┐    ┌───────────────┐  │
│  │ Get Next    │───>│ Route to     │───>│ Load Domain   │  │
│  │ Issue       │    │ Domain       │    │ Context       │  │
│  └─────────────┘    └──────────────┘    └───────────────┘  │
│         │                                       │           │
│         v                                       v           │
│  ┌─────────────┐    ┌──────────────┐    ┌───────────────┐  │
│  │ Create      │<───│ Read Spec &  │<───│ Parse Issue   │  │
│  │ Branch      │    │ CLAUDE.md    │    │ Criteria      │  │
│  └─────────────┘    └──────────────┘    └───────────────┘  │
│         │                                                   │
│         v                                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              IMPLEMENTATION LOOP                     │   │
│  │  ┌─────────┐   ┌─────────┐   ┌─────────┐           │   │
│  │  │ Code    │──>│ Test    │──>│ Validate│──┐        │   │
│  │  └─────────┘   └─────────┘   └─────────┘  │        │   │
│  │       ^                           │       │        │   │
│  │       └───────────────────────────┘       │        │   │
│  │              (until all criteria met)     │        │   │
│  └───────────────────────────────────────────┼────────┘   │
│                                              │             │
│         ┌────────────────────────────────────┘             │
│         v                                                   │
│  ┌─────────────┐    ┌──────────────┐    ┌───────────────┐  │
│  │ Push &      │───>│ Create PR    │───>│ /review-pr    │  │
│  │ Commit      │    │              │    │ (MANDATORY)   │  │
│  └─────────────┘    └──────────────┘    └───────────────┘  │
│                                                │             │
│                                    ┌───────────┼───────┐     │
│                                    │ APPROVED  │ CHANGES│     │
│                                    v           v       │     │
│                             ┌───────────┐ ┌────────┐  │     │
│                             │ Merge PR  │ │Fix &   │──┘     │
│                             │           │ │Re-push │        │
│                             └───────────┘ └────────┘        │
│                                    │                         │
│                                    v                         │
│                             ┌───────────────────────────┐   │
│                             │ More open issues?         │   │
│                             │  YES → loop back to start │   │
│                             │  NO  → print summary, exit│   │
│                             └───────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Detailed Algorithm

### Phase 1: Issue Selection
```python
def get_next_issue(args):
    issues = gh_issue_list(state="open")

    # Filter by args
    if args.label:
        issues = filter_by_label(issues, args.label)

    # Priority ordering by tier label
    tier_order = [
        "tier-1-foundation",
        "tier-2-python",
        "tier-3-node",
        "tier-4-polish",
    ]

    # Within a tier, order by dependency (LLM client first, then patterns, then tests/entry)
    component_order = [
        "llm-client",
        "pattern-chain",
        "pattern-router",
        "pattern-parallel",
        "pattern-orchestrator",
        "scaffolding",
        "testing",
        "docs",
    ]

    # Within a component, sort by issue number (lower first)
    return sort_by(issues, tier_order, component_order, issue_number)[0]
```

### Phase 2: Domain Routing
```python
def route_to_domain(issue):
    labels = extract_labels(issue)

    DOMAIN_MATRIX = {
        "tier-2-python": {
            "stack": "python+asyncio+httpx+rich+pytest",
            "validate": "cd python && python -m pytest tests/ -v",
            "docs": ["CLAUDE.md", "docs/superpowers/specs/2026-04-02-agentforge-lab-design.md"],
            "conventions": {
                "async": True,
                "naming": "snake_case",
                "http_client": "httpx",
                "terminal_ui": "rich",
                "testing": "pytest + pytest-asyncio",
                "data_path": "../data/",
            },
        },
        "tier-3-node": {
            "stack": "node+esm+fetch+chalk+vitest",
            "validate": "cd node && npx vitest run",
            "docs": ["CLAUDE.md", "docs/superpowers/specs/2026-04-02-agentforge-lab-design.md"],
            "conventions": {
                "async": True,
                "naming": "camelCase",
                "module_type": "ESM (type: module)",
                "http_client": "native fetch",
                "terminal_ui": "chalk + ora",
                "testing": "vitest",
                "data_path": "../data/",
            },
        },
    }

    for label in labels:
        if label in DOMAIN_MATRIX:
            return DOMAIN_MATRIX[label]

    # Default: Python track
    return DOMAIN_MATRIX["tier-2-python"]
```

### Phase 3: Implementation
```python
def implement_issue(issue, domain):
    # Create branch
    branch = f"issue/{issue.number}-{slugify(issue.title)}"
    git_checkout_new_branch(branch, "origin/main")

    # Select implementation model based on labels
    impl_model = select_implementation_model(issue.labels)

    # Read context
    read("CLAUDE.md")
    read("docs/superpowers/specs/2026-04-02-agentforge-lab-design.md")

    # Parse acceptance criteria from issue body checkboxes
    criteria = parse_checkboxes(issue.body)

    for criterion in criteria:
        implement_criterion(criterion, domain, model=impl_model)
        git_commit(f"feat: {criterion.summary}\n\nRefs: #{issue.number}")

    # Final validation
    run_validation(domain["validate"])

    return all_criteria_complete(criteria)
```

### Phase 4: Completion
```python
def complete_issue(issue, branch, domain):
    # Push and create PR
    git_push(branch)

    pr = gh_pr_create(
        title=f"{issue.title}",
        body=f"Closes #{issue.number}\n\n{generate_summary()}",
        base="main",
        head=branch
    )

    # MANDATORY: Expert PR Review before merge
    review = run_pr_review(pr.number, model="opus")

    if review.verdict == "APPROVED":
        gh_pr_merge(pr.number, method="squash", delete_branch=True)
    elif review.verdict == "REQUEST CHANGES":
        for finding in review.findings:
            fix_finding(finding, domain, model="sonnet")
            git_commit(f"fix: address review — {finding.summary}")
            git_push(branch)
        review = run_pr_review(pr.number, model="opus")
        if review.verdict == "APPROVED":
            gh_pr_merge(pr.number, method="squash", delete_branch=True)
        else:
            raise ReviewFailure(f"PR #{pr.number} still failing after fixes")

    git_checkout("main")
    git_pull()

    # IMMEDIATELY loop back — do NOT stop, do NOT ask, do NOT summarise.
    next_issue = get_next_issue(args)
    if next_issue:
        implement_issue(next_issue, route_to_domain(next_issue))
    else:
        print_session_summary()
```

## Stack-Specific Validation

### Python Track
```bash
cd python && python -m pytest tests/ -v
```

### Node Track
```bash
cd node && npx vitest run
```

## Domain-Specific Behaviors

### When Working on Python Pattern Issues
- Use `dataclass` or `@dataclass` for all data structures
- Async-first: all LLM calls use `async/await`
- Use `rich.console.Console` for terminal output
- Use `from __future__ import annotations` if needed for type hints
- Prompt templates use Python `str.format_map()` style: `{variable_name}`
- Error handling: catch `Exception`, log with `console.print`, append to state errors list

### When Working on Node Pattern Issues
- Use plain objects or classes (no TypeScript)
- ESM throughout: `import/export`, no `require`
- Use `chalk` for colored output (v5 ESM import)
- Use `performance.now()` for timing
- Use `Promise.allSettled()` for parallel pattern (not `Promise.all()`)
- Prompt templates use template literals or manual string replacement

### When Working on LLM Client Issues
- `CachedLLMClient` keyword matching is CRITICAL for test determinism — see spec Section 2 for the full 17-rule algorithm
- Classification matching uses INCIDENT-SPECIFIC keywords (e.g., "connection pool" for database), NOT category names (because all categories are listed in every classify prompt)
- Handler matching inspects the SYSTEM prompt parameter (not user prompt) for specialist domain keywords
- Match rules are case-insensitive, numbered, and MUST be evaluated in exact spec order — first match wins
- Must handle markdown code fences in `as_json()` / `asJson()`
- Handler responses use separate cached entries (handler_database, handler_billing, etc.)

### When Working on Test Suite Issues
- All tests MUST use `CachedLLMClient` — no Ollama dependency
- Tests should FAIL with `NotImplementedError`/`Error` until students implement patterns
- Tests should PASS when reference solutions from facilitator guide are applied
- Use fixtures to wire up cached client → patterns → orchestrator

## Session Output

```
╔══════════════════════════════════════════════════════════════╗
║                    AUTOWORK SESSION REPORT                    ║
╠══════════════════════════════════════════════════════════════╣
║ Started: 2026-MM-DD HH:MM:SS                                 ║
║ Ended:   2026-MM-DD HH:MM:SS                                 ║
║ Duration: Xh Ym                                               ║
╠══════════════════════════════════════════════════════════════╣
║ Issues Completed: N                                           ║
║ PRs Created: N                                                ║
║ PRs Merged: N                                                 ║
║ Total Commits: N                                              ║
╠══════════════════════════════════════════════════════════════╣
║ COMPLETED ISSUES:                                             ║
║  #NN: Issue title                    PR #N  MERGED (domain)   ║
║  #NN: Issue title                    PR #N  MERGED (domain)   ║
╠══════════════════════════════════════════════════════════════╣
║ REMAINING ISSUES: N                                           ║
║ BLOCKERS: None                                                ║
╚══════════════════════════════════════════════════════════════╝
```

## Error Handling

```
IF test failure:
    Analyze error output
    Fix implementation
    Re-run tests
    MAX 3 retries per criterion, then skip with blocker note

IF import failure:
    Check file paths — both tracks use relative imports from patterns/
    Verify __init__.py exists (Python) or ESM exports correct (Node)

IF JSON parse failure in cached client:
    Check keyword matching logic — prompt may not match expected patterns
    Verify cached_responses.json has the expected keys

IF pattern stub still raises NotImplementedError:
    The implementation is incomplete — this is expected behavior for student stubs
    Tests SHOULD fail until students implement the patterns
```

## Resumption

If interrupted, the loop can resume:
```
/autowork --resume
```

This will:
1. Check for in-progress feature branches (`git branch | grep issue/`)
2. Identify which issue the branch corresponds to
3. Read the issue to determine remaining criteria
4. Resume implementation from the last committed criterion
5. Continue the loop after completing the current issue
