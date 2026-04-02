# Module 2 Lab: Build & Environment Instructions

## AgentForge — Incident Response System

### Lab Overview

Students will build a multi-pattern AI agent system that processes simulated DevOps
incidents using four core agentic patterns: Sequential Chains, Routing, Parallelization,
and Orchestration. The system runs entirely on the student's laptop using Ollama with
the Qwen3.5:4b model (no API keys required).

---

## 1. Prerequisites

### Hardware Requirements

| Spec | Minimum | Recommended |
|------|---------|-------------|
| RAM | 6 GB free | 8 GB free |
| Disk | 5 GB free | 8 GB free |
| CPU | Any x86_64 or ARM64 | 4+ cores |
| GPU | Not required | Any (accelerates inference) |
| OS | macOS 12+, Windows 10+, Ubuntu 20.04+ | Latest stable |

### Software Requirements (Pre-Install)

- **Git** 2.30+
- **Ollama** (latest) — https://ollama.com/download
- **Python Track:** Python 3.11+ and pip
- **Node Track:** Node.js 20+ and npm 10+
- **VS Code** (recommended) with the following extensions:
  - Python (ms-python) OR ESLint + Prettier (for Node track)
  - Ollama extension (optional, for inline model testing)

---

## 2. Ollama Setup (Both Tracks)

### Step 1: Install Ollama

**macOS:**
```bash
# Download and install from https://ollama.com/download
# Or via Homebrew:
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**
```
Download installer from https://ollama.com/download
Run the .exe and follow prompts
```

### Step 2: Start the Ollama Service

```bash
# Start the Ollama server (runs on http://localhost:11434)
ollama serve
```

> **Note:** On macOS, Ollama may auto-start. Check with:
> ```bash
> curl http://localhost:11434/api/tags
> ```
> If you get a JSON response, it's running.

### Step 3: Pull the Lab Model

```bash
# Primary model — Qwen3.5 4B (~3.5 GB download, native tool calling + thinking)
ollama pull qwen3.5:4b

# Verify it works:
ollama run qwen3.5:4b "Respond with exactly: READY"
```

**Expected output:** `READY` (or similar short confirmation)

**If your machine struggles with 4B:**
```bash
# Fallback — Qwen3.5 2B (~2.7 GB download, lighter but still capable)
ollama pull qwen3.5:2b
```

> If using the 2B fallback, set `MODEL_NAME=qwen3.5:2b` in your `.env` file.
> Some prompts may need to be simplified — the facilitator guide has adjusted
> prompts for the smaller model.

### Step 4: Verify the API

```bash
curl http://localhost:11434/api/chat -d '{
  "model": "qwen3.5:4b",
  "messages": [{"role": "user", "content": "Say hello"}],
  "stream": false
}'
```

You should see a JSON response with the model's reply. If so, you're ready.

---

## 3. Python Track Setup

### Step 1: Create Project Directory

```bash
mkdir agentforge-python && cd agentforge-python
python -m venv .venv

# Activate virtual environment
# macOS/Linux:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate
```

### Step 2: Install Dependencies

Create `requirements.txt`:
```
httpx>=0.27.0
rich>=13.7.0
pydantic>=2.6.0
pytest>=8.0.0
pytest-asyncio>=0.23.0
python-dotenv>=1.0.0
```

Install:
```bash
pip install -r requirements.txt
```

### Step 3: Create Environment File

Create `.env`:
```env
OLLAMA_BASE_URL=http://localhost:11434
MODEL_NAME=qwen3.5:4b
MODEL_TEMPERATURE=0.3
REQUEST_TIMEOUT=30
```

### Step 4: Create Project Structure

```bash
mkdir -p patterns tests data

# Create all needed files:
touch patterns/__init__.py
touch patterns/chain.py
touch patterns/router.py
touch patterns/parallel.py
touch patterns/orchestrator.py
touch patterns/llm_client.py
touch tests/__init__.py
touch tests/test_patterns.py
touch agent_forge.py
touch report.md
```

### Step 5: Verify Setup

Create a quick test file `verify_setup.py`:
```python
"""Run this to verify your environment is correctly configured."""
import asyncio
import httpx
from dotenv import load_dotenv
import os

load_dotenv()

async def verify():
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model = os.getenv("MODEL_NAME", "qwen3.5:4b")
    
    print(f"Checking Ollama at {base_url}...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Check Ollama is running
        try:
            resp = await client.get(f"{base_url}/api/tags")
            models = resp.json().get("models", [])
            model_names = [m["name"] for m in models]
            print(f"  Available models: {model_names}")
        except Exception as e:
            print(f"  ERROR: Cannot reach Ollama — {e}")
            print("  Make sure 'ollama serve' is running.")
            return False
        
        # Check our model is available
        if not any(model in name for name in model_names):
            print(f"  ERROR: Model '{model}' not found. Run: ollama pull {model}")
            return False
        
        # Test inference
        print(f"Testing inference with {model}...")
        resp = await client.post(
            f"{base_url}/api/chat",
            json={
                "model": model,
                "messages": [{"role": "user", "content": "Respond with: VERIFIED"}],
                "stream": False,
                "options": {"temperature": 0.0}
            }
        )
        result = resp.json()
        content = result["message"]["content"]
        print(f"  Model response: {content}")
    
    print("\n All checks passed. You're ready for the lab!")
    return True

if __name__ == "__main__":
    asyncio.run(verify())
```

Run it:
```bash
python verify_setup.py
```

**Expected output:**
```
Checking Ollama at http://localhost:11434...
  Available models: ['qwen3.5:4b']
Testing inference with qwen3.5:4b...
  Model response: VERIFIED

 All checks passed. You're ready for the lab!
```

---

## 4. Node.js Track Setup

### Step 1: Create Project Directory

```bash
mkdir agentforge-node && cd agentforge-node
npm init -y
```

### Step 2: Install Dependencies

```bash
npm install chalk@5 ora@8 dotenv

# Dev dependencies
npm install -D vitest
```

### Step 3: Configure package.json

Update your `package.json`:
```json
{
  "name": "agentforge-node",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "start": "node agent_forge.js",
    "test": "vitest run",
    "test:watch": "vitest",
    "verify": "node verify_setup.js"
  }
}
```

### Step 4: Create Environment File

Create `.env`:
```env
OLLAMA_BASE_URL=http://localhost:11434
MODEL_NAME=qwen3.5:4b
MODEL_TEMPERATURE=0.3
REQUEST_TIMEOUT=30000
```

### Step 5: Create Project Structure

```bash
mkdir -p patterns tests data

# Create all needed files:
touch patterns/chain.js
touch patterns/router.js
touch patterns/parallel.js
touch patterns/orchestrator.js
touch patterns/llm_client.js
touch tests/patterns.test.js
touch agent_forge.js
touch report.md
```

### Step 6: Verify Setup

Create `verify_setup.js`:
```javascript
import 'dotenv/config';

const BASE_URL = process.env.OLLAMA_BASE_URL || 'http://localhost:11434';
const MODEL = process.env.MODEL_NAME || 'qwen3.5:4b';

async function verify() {
  console.log(`Checking Ollama at ${BASE_URL}...`);
  
  try {
    // Check Ollama is running
    const tagsResp = await fetch(`${BASE_URL}/api/tags`);
    const tags = await tagsResp.json();
    const modelNames = tags.models?.map(m => m.name) || [];
    console.log(`  Available models: ${modelNames.join(', ')}`);
    
    // Check our model
    if (!modelNames.some(name => name.includes(MODEL.replace(':latest', '')))) {
      console.error(`  ERROR: Model '${MODEL}' not found. Run: ollama pull ${MODEL}`);
      process.exit(1);
    }
    
    // Test inference
    console.log(`Testing inference with ${MODEL}...`);
    const chatResp = await fetch(`${BASE_URL}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: MODEL,
        messages: [{ role: 'user', content: 'Respond with: VERIFIED' }],
        stream: false,
        options: { temperature: 0.0 }
      })
    });
    const result = await chatResp.json();
    console.log(`  Model response: ${result.message.content}`);
    
    console.log('\n All checks passed. You\'re ready for the lab!');
  } catch (err) {
    console.error(`  ERROR: Cannot reach Ollama — ${err.message}`);
    console.error('  Make sure \'ollama serve\' is running.');
    process.exit(1);
  }
}

verify();
```

Run it:
```bash
npm run verify
```

---

## 5. Sample Incident Data

Create `data/incidents.json` in your project directory (both tracks use the same data):

```json
[
  {
    "id": "INC-001",
    "timestamp": "2026-01-15T14:23:00Z",
    "source": "monitoring-agent",
    "severity": "high",
    "title": "Database connection pool exhausted",
    "description": "PostgreSQL connection pool at 100% capacity. Active connections: 200/200. Queue depth: 47. Application threads blocking on connection acquisition. Affected services: user-api, order-api, inventory-api. Started 12 minutes ago. Memory usage normal at 68%. CPU at 34%.",
    "logs": "2026-01-15T14:11:00Z ERROR [HikariPool-1] Connection not available, request timed out after 30000ms\n2026-01-15T14:11:05Z WARN  [user-api] Retry attempt 1/3 for getUserProfile\n2026-01-15T14:11:35Z ERROR [user-api] Retry attempt 3/3 failed for getUserProfile\n2026-01-15T14:15:00Z ERROR [order-api] Cannot acquire connection for processOrder\n2026-01-15T14:18:00Z CRITICAL [monitoring] Connection pool utilization at 100%"
  },
  {
    "id": "INC-002",
    "timestamp": "2026-01-15T09:45:00Z",
    "source": "customer-support",
    "severity": "medium",
    "title": "Customers reporting double charges",
    "description": "Multiple customers report being charged twice for single orders. Affected transactions from the past 2 hours. Payment gateway logs show duplicate webhook deliveries. Approximately 23 affected customers. Total overcharge estimated at $4,750.",
    "logs": "2026-01-15T08:00:00Z INFO  [payment-webhook] Received payment.completed for order_8834\n2026-01-15T08:00:01Z INFO  [payment-webhook] Received payment.completed for order_8834 (duplicate)\n2026-01-15T08:00:01Z INFO  [billing-service] Processing charge for order_8834: $125.00\n2026-01-15T08:00:02Z INFO  [billing-service] Processing charge for order_8834: $125.00\n2026-01-15T09:30:00Z WARN  [support-system] 15 tickets opened regarding double charges"
  },
  {
    "id": "INC-003",
    "timestamp": "2026-01-15T16:05:00Z",
    "source": "health-check",
    "severity": "critical",
    "title": "API gateway returning 503 errors",
    "description": "Primary API gateway reporting 503 Service Unavailable for 40% of requests. Upstream health checks failing for 3 of 5 backend instances. Load balancer circuit breaker triggered. CDN cache serving stale content for static assets. DNS resolution normal. SSL certificates valid.",
    "logs": "2026-01-15T16:00:00Z ERROR [nginx] upstream timed out (110: Connection timed out) while connecting to upstream\n2026-01-15T16:00:30Z WARN  [lb-health] Backend instance-03 failed health check (3/3)\n2026-01-15T16:01:00Z WARN  [lb-health] Backend instance-04 failed health check (2/3)\n2026-01-15T16:02:00Z ERROR [circuit-breaker] Circuit OPEN for backend-pool-1\n2026-01-15T16:03:00Z CRITICAL [gateway] 503 error rate exceeded 30% threshold"
  },
  {
    "id": "INC-004",
    "timestamp": "2026-01-15T11:30:00Z",
    "source": "user-report",
    "severity": "low",
    "title": "Password reset emails not arriving",
    "description": "Users report password reset emails taking over 30 minutes to arrive or not arriving at all. Email service dashboard shows queue depth of 12,000 messages. SMTP relay responding normally. No bounce-backs detected. Started approximately 2 hours ago.",
    "logs": "2026-01-15T09:30:00Z INFO  [email-queue] Queue depth: 500 (normal)\n2026-01-15T10:00:00Z WARN  [email-queue] Queue depth: 3000 (elevated)\n2026-01-15T10:30:00Z WARN  [email-queue] Queue depth: 8000 (critical)\n2026-01-15T11:00:00Z ERROR [email-worker] Worker pool exhausted, 2/8 workers responding\n2026-01-15T11:15:00Z INFO  [email-worker] Worker-03 OOM killed by kernel"
  }
]
```

---

## 6. Cached Responses (Offline Fallback)

If Ollama has issues during the lab, students can use pre-cached model responses.

Create `data/cached_responses.json`:

```json
{
  "classify_database": {
    "category": "technical/database",
    "confidence": 0.95,
    "reasoning": "The incident describes database connection pool exhaustion with specific PostgreSQL metrics. This is a database infrastructure issue requiring DBA and backend engineering response."
  },
  "classify_billing": {
    "category": "billing/payment",
    "confidence": 0.92,
    "reasoning": "The incident involves duplicate payment charges from webhook processing. This requires billing team investigation and customer refund processing."
  },
  "classify_network": {
    "category": "technical/network",
    "confidence": 0.91,
    "reasoning": "The incident shows API gateway 503 errors with upstream timeouts and failed health checks. This is a network/infrastructure issue requiring SRE response."
  },
  "classify_general": {
    "category": "general/email",
    "confidence": 0.88,
    "reasoning": "The incident involves delayed email delivery due to queue buildup and worker failures. This is an application infrastructure issue."
  },
  "chain_parse": {
    "errors_found": 5,
    "error_types": ["timeout", "connection_exhaustion", "retry_failure"],
    "time_range": "14:11:00 - 14:18:00",
    "affected_services": ["user-api", "order-api", "monitoring"]
  },
  "chain_analyze": {
    "root_cause": "Connection pool sized at 200 is insufficient for current load. Connection leak or slow query is preventing connection return to pool.",
    "impact": "Three critical services unable to serve requests. User-facing errors for all database-dependent operations.",
    "severity_assessment": "HIGH — Customer-impacting, revenue-affecting"
  },
  "chain_recommend": {
    "immediate_actions": [
      "Increase connection pool to 300 as temporary fix",
      "Identify and kill long-running queries",
      "Restart affected application instances in rolling fashion"
    ],
    "investigation_steps": [
      "Check for connection leaks in recent deployments",
      "Review slow query log for queries exceeding 5 seconds",
      "Analyze connection lifetime distribution"
    ],
    "prevention": [
      "Implement connection pool monitoring with alerting at 80%",
      "Add connection timeout and validation on borrow",
      "Set up automated connection leak detection"
    ]
  },
  "parallel_memory_check": {
    "status": "healthy",
    "usage_percent": 68,
    "details": "Memory utilization within normal range. No memory leak indicators."
  },
  "parallel_cpu_check": {
    "status": "healthy",
    "usage_percent": 34,
    "details": "CPU utilization low. Not a contributing factor to the incident."
  },
  "parallel_disk_check": {
    "status": "healthy",
    "usage_percent": 45,
    "details": "Disk I/O within normal parameters. No disk-related bottlenecks."
  },
  "parallel_network_check": {
    "status": "warning",
    "details": "Elevated connection count on port 5432. 200 established connections to PostgreSQL. Connection queue detected."
  }
}
```

---

## 7. Troubleshooting Guide

### Common Issues

| Issue | Symptom | Fix |
|-------|---------|-----|
| Ollama not running | `Connection refused` errors | Run `ollama serve` in a separate terminal |
| Model not found | `model not found` in response | Run `ollama pull qwen3.5:4b` |
| Slow responses | >10 seconds per call | Close other apps; try `qwen3.5:2b` instead |
| Out of memory | Process killed / system freeze | Use `qwen3.5:2b`; close Chrome tabs |
| Python venv issues | `ModuleNotFoundError` | Ensure venv is activated: `source .venv/bin/activate` |
| Node import errors | `ERR_MODULE_NOT_FOUND` | Check `"type": "module"` in package.json |
| JSON parse failures | Model returns prose instead of JSON | Lower temperature to 0.1; add "respond ONLY with JSON" to prompt |
| Inconsistent results | Different outputs each run | Set temperature to 0.0 for deterministic output |

### Emergency Fallback: Cached Mode

If Ollama is completely unavailable, both tracks support a `--cached` flag:

**Python:**
```bash
python agent_forge.py --cached
```

**Node:**
```bash
node agent_forge.js --cached
```

This loads responses from `data/cached_responses.json` instead of calling the model,
allowing students to focus on pattern implementation rather than model interaction.

---

## 8. Instructor Lab Build Checklist

Before the session, the instructor should:

```
□ Clone the lab repository and run both tracks end-to-end
□ Verify Ollama + qwen3.5:4b on the instructor machine
□ Test on a low-spec machine (4GB RAM) to find pain points
□ Pre-download model weights to USB drives (for slow networks)
□ Prepare cloud fallback environment (Codespaces / Gitpod)
□ Verify cached_responses.json works in offline mode
□ Run test suites for both Python and Node tracks
□ Review student guide for accuracy after any framework updates
□ Print the troubleshooting table for quick reference during lab
□ Prepare 2 USB drives with offline Ollama installers + model weights
```

### Cloud Fallback URLs
- **GitHub Codespaces:** `https://codespaces.new/arula-ai/cgse-m02-lab`
- **Gitpod:** `https://gitpod.io/#https://github.com/arula-ai/cgse-m02-lab`

These environments come pre-configured with Ollama and the model pre-loaded.
