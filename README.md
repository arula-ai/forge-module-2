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
