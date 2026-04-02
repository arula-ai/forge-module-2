# Module 2: Core Agentic Patterns — Instructor Presentation Outline

## CGSE-Advanced | Session Duration: 4 Hours | Delivery: Hybrid

---

## Pre-Session Setup Checklist

```
□ Verify Ollama is running on instructor machine: ollama serve
□ Pull model: ollama pull qwen3.5:4b
□ Test both Python and Node demo environments end-to-end
□ Open fallback cached responses in /data/cached_responses/
□ Pre-load terminal with 'rich' formatted output visible for wow factor
□ Verify student environment access (poll in Slack 30 min prior)
□ Queue up the "incident simulation" demo data
□ Have Architecture diagrams ready in Excalidraw/Miro
```

---

## Session Arc & Emotional Journey

```
Curiosity → Understanding → Confidence → Ambition
   ↓             ↓              ↓            ↓
 "Whoa,      "Ah, that's    "I just     "What if I
  agents       how they       built       combined
  can do       work!"         one!"       all four?"
  THAT?"
```

---

## Slide-by-Slide Outline

### — OPENING BLOCK (20 minutes) —

#### Slide 1: Title & Session Contract
**Title:** Core Agentic Patterns — From Single Prompts to Autonomous Systems

**Speaker Notes:**
> Welcome back. Last session you mastered RIFCC and learned that AI is a tool,
> not a replacement. Today we break that tool open and learn how to build
> *systems* of AI — agents that reason, route, parallelize, and orchestrate.
> By the end of today, you will have a working multi-agent incident response
> system running entirely on your laptop. No cloud. No API keys. No excuses.

**On-Screen:**
- 4 learning objectives (below)
- Session timeline visual
- "What you'll build today" screenshot of the final terminal output

---

#### Slide 2: Learning Objectives

| # | Objective | Bloom Level |
|---|-----------|-------------|
| 1 | Implement a sequential processing chain that passes state between steps | Apply |
| 2 | Build an intent router that classifies input and delegates to specialized handlers | Apply |
| 3 | Design a parallel fan-out system that executes multiple tasks concurrently | Apply |
| 4 | Orchestrate multiple agentic patterns into a unified system with error handling | Create |

**Speaker Notes:**
> These four patterns are the atoms of every agent system you'll ever encounter.
> ChatGPT plugins? Routing + tool use. GitHub Copilot Workspace? Chains + parallel.
> AutoGen, CrewAI, LangGraph — all combinations of these four building blocks.

---

#### Slide 3: The Agentic Spectrum

**Visual: Horizontal spectrum diagram**

```
Simple Prompt → Structured Prompt → Chain → Router → Parallel → Orchestrator → Full Agent
     ↑                  ↑               ↑        ↑         ↑            ↑
  Module 1          Module 1        TODAY    TODAY     TODAY        TODAY
```

**Speaker Notes:**
> In Module 1 you lived on the left side of this spectrum. Today we cross
> the threshold into agentic territory. The key insight: agents aren't magic.
> They're just well-structured patterns of LLM calls with state management
> and control flow. Software engineering fundamentals — applied to AI.

---

#### Slide 4: Why Local Models Matter

**Key Points:**
- Production agents often need to run in constrained environments
- Cost control: a 4B local model costs $0 per call
- Privacy: data never leaves the machine
- Latency: no network round-trip
- Today's lab uses **Qwen3.5:4b** via **Ollama** — runs on 6GB RAM, with native tool calling and thinking mode

**Speaker Notes:**
> We're deliberately using a small local model today. Two reasons.
> First, it forces you to write better prompts — you can't rely on
> GPT-4 brute force. Second, this is realistic. In production, you'll
> often run routing and classification on small models to save cost,
> reserving large models for complex generation. This is called the
> "model cascade" pattern — we'll cover it in Module 10.
>
> Qwen 3.5 is a great lab model because it has native tool calling
> and thinking mode built in — exactly the capabilities we need
> for agentic patterns. And at 4 billion parameters, it runs
> comfortably on any modern laptop.

**DEMO MOMENT:** Show Ollama pulling and running qwen3.5:4b live.
```bash
ollama run qwen3.5:4b "What are the four core agentic patterns?"
```
> Look at that response time. Sub-second. On my laptop. No API key. Let's build.

---

### — PATTERN 1: SEQUENTIAL CHAINS (35 minutes) —

#### Slide 5: What Is a Chain?

**Visual: Assembly line diagram**

```
[Input] → [Step 1: Parse] → [Step 2: Analyze] → [Step 3: Decide] → [Step 4: Format] → [Output]
              ↓                    ↓                   ↓                  ↓
           state_v1             state_v2            state_v3           state_v4
```

**Definition:** A chain executes a fixed sequence of steps where each step's output becomes the next step's input. State accumulates through the pipeline.

**Speaker Notes:**
> The chain is the simplest agentic pattern. Think of it like a Unix pipeline:
> `cat log.txt | grep ERROR | sort | uniq -c | sort -rn`. Each step transforms
> the data and passes it forward. The power comes from specialization — each
> step has its own prompt, its own role, its own constraints.

---

#### Slide 6: Chain Architecture Deep-Dive

**Key Concepts:**
1. **State Object** — Accumulated data flowing through the chain
2. **Step Interface** — Consistent contract (input → output)
3. **Error Boundaries** — Each step can fail independently
4. **Observability** — Log at each transition point

**Code Pattern (pseudocode):**
```
class Chain:
    steps: List[Step]

    execute(input) → output:
        state = input
        for step in steps:
            state = step.process(state)    # Transform
            log(step.name, state)          # Observe
        return state
```

**Speaker Notes:**
> Notice the interface. Every step takes state in, returns state out.
> This is the Strategy pattern from Gang of Four — same interface,
> different implementations. The chain doesn't care what each step does
> internally, it just manages the flow. This is critical for testability.

---

#### Slide 7: Live Coding — Building a Diagnostic Chain

**DEMO (10 minutes):**
Build a 3-step chain that processes a server log:
1. **Parse** — Extract error messages and timestamps
2. **Classify** — Categorize the error type (memory, network, disk, application)
3. **Recommend** — Suggest remediation steps

**Show:**
- The chain running step by step with rich terminal output
- State accumulating between steps
- What happens when Step 2 fails (error propagation)

**Instructor Tip:**
> Build this live, but have the completed version ready. Start with just
> Step 1 working, then add Step 2 live. This shows the iterative process.
> Deliberately make a mistake in the prompt (forget to specify JSON output)
> and debug it live — students learn more from failures.

---

#### Slide 8: Chain Anti-Patterns

| Anti-Pattern | Why It Fails | Better Approach |
|-------------|--------------|-----------------|
| Mega-prompt (everything in one call) | Unreliable, hard to debug | Split into focused steps |
| No state validation between steps | Silent corruption | Validate schema at each boundary |
| Ignoring step failures | Cascade of garbage | Fail fast with meaningful errors |
| Hardcoded step order | Inflexible | Configuration-driven step registry |

**Speaker Notes:**
> The most common mistake I see: developers try to do everything in one
> massive prompt. "Analyze this log, find the errors, classify them,
> suggest fixes, and format as JSON." With a small model, that fails
> catastrophically. With a large model, it works 80% of the time —
> which is worse, because you ship it and then it fails in production.

---

### ☕ BREAK (10 minutes)

---

### — PATTERN 2: ROUTING (35 minutes) —

#### Slide 9: The Router Pattern

**Visual: Traffic intersection diagram**

```
                    ┌→ [Technical Handler] → response
[Input] → [Router] ─┤→ [Billing Handler]  → response
                    └→ [General Handler]   → response
```

**Definition:** A router classifies incoming requests and delegates them to specialized handlers. Each handler is optimized for its domain.

**Speaker Notes:**
> Routing is everywhere in software — HTTP routers, message queues,
> load balancers. The agentic router does the same thing but uses an
> LLM for classification instead of regex or rules. The beauty: it
> handles ambiguity and natural language that rule-based systems can't.

---

#### Slide 10: Classification Strategies

**Three Approaches (increasing sophistication):**

1. **Prompt-Based Classification**
   - Ask the LLM to classify directly
   - Simple, but uses a full LLM call
   - Best for: complex, nuanced routing

2. **Embedding + Similarity**
   - Embed the input, compare to category embeddings
   - Fast, cheap, no LLM call needed
   - Best for: high-volume, clear categories

3. **Hybrid (Lab Approach)**
   - Fast keyword check first (zero-cost)
   - LLM classification for ambiguous cases
   - Best for: production systems

**Speaker Notes:**
> In today's lab, we use prompt-based classification because it's the
> clearest to understand. But I want you to know: in production, you'd
> almost certainly use a hybrid approach. Route 60% of requests with
> simple keyword matching, and only call the LLM for the ambiguous 40%.
> That cuts your inference cost by more than half.

---

#### Slide 11: Live Coding — Intent Router

**DEMO (10 minutes):**
Build a router that classifies incident reports:

```
"Database connection pool exhausted" → technical/database
"Customer charged twice for subscription" → billing/refund
"How do I reset my password?" → general/account
"Server CPU at 98% and climbing" → technical/infrastructure
```

**Show:**
- The classification prompt with confidence scores
- Fallback to default handler when confidence < threshold
- How to add a new route without changing existing code (Open/Closed Principle)

---

#### Slide 12: Router Design Decisions

**Discussion Prompt (5 minutes — think-pair-share):**

> Your router is 95% accurate. The 5% misroutes send billing issues
> to the technical team and vice versa. What's the business impact?
> How would you handle this?

**Expected Discussion Points:**
- Confidence thresholds and escalation to human
- Misroute detection via handler feedback
- A/B testing router prompt variations
- Logging and monitoring classification accuracy

---

### — PATTERN 3: PARALLELIZATION (35 minutes) —

#### Slide 13: The Parallel Fan-Out Pattern

**Visual: Fork-join diagram**

```
              ┌→ [Check A: Memory]  ──┐
[Input] → [Fan-Out]→ [Check B: CPU]    ──┤→ [Aggregator] → [Result]
              ├→ [Check C: Disk]    ──┤
              └→ [Check D: Network] ──┘
```

**Definition:** Execute multiple independent LLM calls concurrently, then aggregate results. Trades compute for latency.

**Speaker Notes:**
> Sequential execution of 4 checks at 500ms each = 2 seconds.
> Parallel execution of 4 checks = ~500ms. Same cost, 4x faster.
> This is the most impactful pattern for user-facing latency.

---

#### Slide 14: Concurrency in Python vs Node

**Side-by-side comparison:**

| Aspect | Python (asyncio) | Node.js (Promise.all) |
|--------|------------------|----------------------|
| Syntax | `asyncio.gather(*tasks)` | `Promise.all(tasks)` |
| Error handling | `return_exceptions=True` | `.allSettled()` |
| Timeouts | `asyncio.wait_for()` | `Promise.race([task, timeout])` |
| Cancellation | `task.cancel()` | `AbortController` |

**Speaker Notes:**
> Both languages handle this beautifully. Python's asyncio and Node's
> event loop are both perfect for I/O-bound concurrency — which is exactly
> what LLM calls are. Choose your language based on your team, not the pattern.

---

#### Slide 15: Live Coding — Parallel Diagnostics

**DEMO (10 minutes):**
Run 4 diagnostic checks in parallel:
- Memory analysis
- CPU analysis
- Disk analysis
- Network analysis

**Show:**
- All 4 spinners running simultaneously in the terminal
- Results arriving in non-deterministic order
- Aggregation into a unified report
- What happens when one check times out (graceful degradation)

---

#### Slide 16: Parallel Pattern Pitfalls

**Critical Warnings:**

1. **Rate Limiting** — 4 parallel calls = 4x rate limit consumption
2. **Token Budget** — Parallel calls share the same budget
3. **Result Consistency** — Non-deterministic ordering requires careful aggregation
4. **Error Isolation** — One failure shouldn't kill all branches
5. **Resource Contention** — Local model can only process one request at a time!

**Speaker Notes:**
> That last point is crucial for today's lab. Ollama processes requests
> sequentially by default. So "parallel" with a local model means
> concurrent I/O waiting, not true parallel inference. In production
> with API-based models, you get real parallelism. With local models,
> you'd need multiple model instances or a batching server.
> This is a great lesson in understanding your runtime constraints.

---

### 🍽 LUNCH BREAK (45 minutes)

---

### — PATTERN 4: ORCHESTRATION (30 minutes) —

#### Slide 17: The Orchestrator Pattern

**Visual: Conductor + orchestra diagram**

```
                          ┌→ [Router]
[Input] → [Orchestrator] ─┤→ [Chain]     → [Orchestrator] → [Output]
               ↑          └→ [Parallel]        ↑
               │                               │
               └──── State Manager ────────────┘
```

**Definition:** An orchestrator composes chains, routers, and parallel patterns into a complete system, managing global state, error recovery, and execution flow.

**Speaker Notes:**
> This is where it all comes together. The orchestrator is like a
> conductor — it doesn't play any instrument, but it decides who plays
> when, how loud, and what to do when someone hits a wrong note.
> In code terms: it manages the control flow, state, and error handling
> across all the other patterns.

---

#### Slide 18: Orchestrator State Machine

**Visual: State diagram**

```
[RECEIVED] → [CLASSIFYING] → [ROUTING] → [DIAGNOSING] → [RECOMMENDING] → [COMPLETE]
     ↓             ↓              ↓            ↓               ↓
  [FAILED]     [FAILED]      [FAILED]     [FAILED]        [FAILED]
                                               ↓
                                          [ESCALATED]
```

**Key Design Decisions:**
- What state needs to persist between patterns?
- When do you retry vs. escalate vs. fail?
- How do you maintain an audit trail?
- What's the timeout budget across the full pipeline?

---

#### Slide 19: Production Considerations

**The "Real World" Slide:**

| Concern | Lab Implementation | Production Implementation |
|---------|-------------------|--------------------------|
| Model | Qwen3.5:4b local | Model cascade (small→large) |
| State | In-memory dict | Redis / database |
| Errors | Print + raise | Structured logging + alerting |
| Timeout | 30s total | Per-step budgets with circuit breaker |
| Scaling | Single process | Queue + workers |
| Testing | Unit tests | Unit + integration + eval suite |

**Speaker Notes:**
> Today's lab is intentionally simple in infrastructure so you can
> focus on the patterns. But I want you to see the gap between lab
> and production. Module 9 (Governance) and Module 10 (Performance)
> will close this gap.

---

### — LAB INTRODUCTION (15 minutes) —

#### Slide 20: Lab Brief — "AgentForge: Incident Response System"

**The Scenario:**
> You are building an AI-powered incident response system for a DevOps team.
> When an incident is reported, your system must:
> 1. **Route** the incident to the right specialist (database, network, application)
> 2. **Chain** a diagnostic pipeline (parse → classify → analyze → recommend)
> 3. **Parallelize** health checks across multiple subsystems
> 4. **Orchestrate** the full response from intake to resolution report

**What They'll Build:**

Show screenshot/recording of the finished system running:
- Beautiful terminal output with colored status indicators
- Real-time progress as each pattern executes
- Final incident report generated

**Speaker Notes:**
> This is designed to feel like building a real product. The terminal
> output isn't just pretty — it's observability. In production, those
> status lines become structured logs. Those timing numbers become
> metrics. Those error messages become alerts. You're building
> production habits from day one.

---

#### Slide 21: Lab Structure & Timing

```
Phase 1 (20 min): Environment setup + verify Ollama
Phase 2 (15 min): Build the Sequential Chain
Phase 3 (15 min): Build the Router
Phase 4 (15 min): Build the Parallel Checker
Phase 5 (15 min): Build the Orchestrator
Phase 6 (10 min): Run full system + experiments
Phase 7 (10 min): Run tests + submission
Buffer:  (10 min): Troubleshooting / bonus challenges
```

**Instructor Tip:**
> Walk the room during Phase 1. Environment issues must be resolved
> in the first 20 minutes or they cascade. Have the cloud backup
> environment URL ready for anyone whose local setup fails.

---

#### Slide 22: Choose Your Track

**Two fully equivalent implementations:**

| | Python Track | Node.js Track |
|-|-------------|---------------|
| Runtime | Python 3.11+ | Node.js 20+ |
| Async | asyncio | async/await + Promise.all |
| HTTP Client | httpx | fetch (native) |
| Terminal UI | rich | chalk + ora |
| Testing | pytest + pytest-asyncio | vitest |
| Package Mgr | pip / venv | npm |

> Pick the language you'll use in production. Both tracks cover
> identical patterns and produce identical results.

---

### — LAB WORK TIME (90 minutes) —

#### Slide 23: Lab In Progress

**On-screen during lab:** Timer + current phase + help queue link

**Circulation Strategy:**
```
0–20 min:  Focus on setup stragglers. Pair anyone stuck with a neighbor.
20–35 min: Check chain implementations. Common issue: JSON parsing.
35–50 min: Check routers. Common issue: classification prompt too vague.
50–65 min: Check parallel. Common issue: async/await mistakes.
65–80 min: Check orchestrators. Help with state management.
80–90 min: Encourage experiments. Suggest bonus challenges.
```

**Bonus Challenges (for fast finishers):**
1. Add a "severity scoring" step to the chain
2. Implement retry logic with exponential backoff on the router
3. Add a timeout mechanism to the parallel checks
4. Create a new incident type and handler

---

### — DEBRIEF & WRAP-UP (30 minutes) —

#### Slide 24: Code Review — Patterns in the Wild

**Interactive Discussion:**
Pull up 2-3 student implementations (ask for volunteers) and compare approaches.

**Discussion Questions:**
1. "How did you handle the case where the router wasn't confident?"
2. "What happened when you changed the model temperature?"
3. "Did anyone's parallel checks return in a surprising order?"
4. "What would break first if you pointed this at GPT-4 instead of a local model?"

---

#### Slide 25: Pattern Composition Matrix

**When to Use What:**

| Scenario | Primary Pattern | Why |
|----------|----------------|-----|
| Multi-step document processing | Chain | Order matters, state accumulates |
| Customer support triage | Router | Different domains need different expertise |
| System health monitoring | Parallel | Independent checks, latency-critical |
| Full incident response | Orchestrator | Multiple patterns coordinated |
| Code review automation | Chain + Parallel | Sequential analysis, parallel file processing |
| Content moderation | Router + Chain | Classify first, then process by type |

---

#### Slide 26: Connecting to Module 3

**Preview: Reflection and Self-Improvement**

> Today's agents execute a fixed plan. But what if an agent could
> evaluate its own output and decide to try again? What if it could
> learn from its mistakes within a single session?

**Teaser Demo:** Run today's orchestrator → get a mediocre result → show a Module 3 "reflection loop" that critiques and improves the output automatically.

---

#### Slide 27: Key Takeaways

1. **Chains** give you predictable, debuggable multi-step processing
2. **Routers** enable specialization without monolithic prompts
3. **Parallel execution** trades compute for latency
4. **Orchestrators** compose patterns into production systems
5. **Small models are powerful** when you write focused, constrained prompts
6. **Every pattern maps to classic software engineering** — Strategy, Observer, Command, Mediator

---

#### Slide 28: Assignment & Next Session

**Due before Module 3:**
- [ ] Complete lab (all tests passing)
- [ ] Write 200-word reflection in `report.md`
- [ ] Submit PR with your implementation
- [ ] (Bonus) Try swapping Qwen3.5 for Gemma3:4b or Qwen3:4b and note differences

**Pre-reading for Module 3:**
- Chapter 3: Reflection Patterns (Gulli)
- Blog post: "Constitutional AI in Practice" (link in Slack)

---

## Appendix: Instructor Resources

### Timing Cheat Sheet (total: 240 min)

| Block | Duration | Clock Time (9 AM start) |
|-------|----------|------------------------|
| Opening | 20 min | 9:00–9:20 |
| Pattern 1: Chains | 35 min | 9:20–9:55 |
| Break | 10 min | 9:55–10:05 |
| Pattern 2: Routing | 35 min | 10:05–10:40 |
| Pattern 3: Parallel | 35 min | 10:40–11:15 |
| Lunch | 45 min | 11:15–12:00 |
| Pattern 4: Orchestration | 30 min | 12:00–12:30 |
| Lab Intro | 15 min | 12:30–12:45 |
| Lab Work | 90 min | 12:45–2:15 |
| Debrief | 30 min | 2:15–2:45 |

### Backup Plans

| Failure | Response |
|---------|----------|
| Ollama won't install | Use cloud Ollama endpoint (backup URL in Slack) |
| Model download too slow | Pre-loaded USB drives at front of room |
| Model gives bad output | Switch to cached responses in /data/ |
| Student laptop too slow | Pair programming with neighbor |
| Network down entirely | Run from pre-cached mode (instructions in build guide) |

### Demo Scripts Location
```
/demos/module-02/
  01-simple-chain.py
  02-router-demo.py
  03-parallel-demo.py
  04-orchestrator-full.py
  cached_responses/  (for offline mode)
```
