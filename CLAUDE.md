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
- `CachedLLMClient` keyword matching: uses incident-specific content keywords (NOT category names) for classification, system prompt inspection for handler responses, and context keywords for chain/parallel. See spec Section 2 for the full 17-rule matching algorithm. Rules are numbered and must be evaluated in exact order.

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
