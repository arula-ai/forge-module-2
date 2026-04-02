# AgentForge — Module 2 Lab

This is a teaching lab where students implement 4 agentic AI patterns (Chain, Router, Parallel, Orchestrator) in an incident response system.

## Structure

- `python/` — Python track (Python 3.11+, async with httpx)
- `node/` — Node.js track (Node 20+, ESM with native fetch)
- `data/` — Shared incident data and cached LLM responses

## What Students Implement

Students implement core methods marked with `raise NotImplementedError` (Python) or `throw new Error` (Node):

- **Chain:** `execute()` — loop through steps, call LLM, accumulate state
- **Router:** `classify()` + `route()` — classify incident, delegate to handler
- **Parallel:** `run_all_checks()` + `_aggregate()` — fan-out checks, aggregate results
- **Orchestrator:** `process_incident()` — compose all 3 patterns into a pipeline

## Testing

- Python: `cd python && python -m pytest tests/ -v` (20 tests)
- Node: `cd node && npx vitest run` (20 tests)
- All tests use `CachedLLMClient` — no Ollama dependency

## Grading

See `grade-lab.prompt.md` for the complete grading rubric. Students can ask you to grade their lab using that rubric.
