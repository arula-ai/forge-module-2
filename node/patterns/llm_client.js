/**
 * LLM Client — Ollama API wrapper for AgentForge.
 *
 * This module provides two client implementations:
 *   - LLMClient: Makes real HTTP requests to the Ollama /api/chat endpoint.
 *   - CachedLLMClient: Returns pre-built responses using keyword matching.
 *                      Used for offline mode (--cached) and test suites.
 *
 * Students: You do NOT need to modify this file. Use the `chat()` method
 * from whichever client is passed to your pattern classes.
 *
 * API:
 *     const response = await llm.chat("your prompt", { system: "optional" });
 *     response.content      // Raw text from the model
 *     response.durationMs   // How long the call took
 *     response.asJson()     // Parse content as JSON object (throws on invalid)
 */

import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

export class LLMResponse {
  #content;
  #durationMs;

  constructor(content, durationMs) {
    this.#content = content;
    this.#durationMs = durationMs;
  }

  get content() {
    return this.#content;
  }

  get durationMs() {
    return this.#durationMs;
  }

  asJson() {
    let text = this.#content.trim();
    // Strip markdown code fences (```json ... ``` or ``` ... ```)
    text = text.replace(/^```(?:json)?\s*\n?/, '');
    text = text.replace(/\n?```\s*$/, '');
    text = text.trim();
    try {
      return JSON.parse(text);
    } catch (e) {
      throw new Error(`Failed to parse LLM response as JSON: ${e.message}`);
    }
  }
}

export class LLMClient {
  constructor({
    baseUrl = 'http://localhost:11434',
    model = 'qwen3.5:4b',
    temperature = 0.3,
    timeout = 30000,
  } = {}) {
    this.baseUrl = baseUrl.replace(/\/+$/, '');
    this.model = model;
    this.temperature = temperature;
    this.timeout = timeout;
  }

  async chat(prompt, { system = '', temperature = null } = {}) {
    const messages = [];
    if (system) {
      messages.push({ role: 'system', content: system });
    }
    messages.push({ role: 'user', content: prompt });

    const payload = {
      model: this.model,
      messages,
      stream: false,
      options: { temperature: temperature ?? this.temperature },
    };

    const start = performance.now();
    const resp = await fetch(`${this.baseUrl}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      signal: AbortSignal.timeout(this.timeout),
    });

    if (!resp.ok) {
      throw new Error(`Ollama request failed: ${resp.status} ${resp.statusText}`);
    }

    const data = await resp.json();
    const durationMs = performance.now() - start;
    const content = data?.message?.content ?? '';
    return new LLMResponse(content, durationMs);
  }
}

export class CachedLLMClient extends LLMClient {
  #cache;

  constructor(cachePath) {
    super();
    this.#cache = JSON.parse(readFileSync(cachePath, 'utf-8'));
  }

  /**
   * Match the prompt against cached responses using keyword rules.
   * Always returns a valid LLMResponse (never throws). If no rule matches,
   * returns a JSON error object. Results are deterministic.
   */
  async chat(prompt, { system = '' } = {}) {
    const p = prompt.toLowerCase();
    const s = system.toLowerCase();

    const key = this.#match(p, s);
    const content =
      key !== null
        ? JSON.stringify(this.#cache[key])
        : JSON.stringify({ error: 'No cached response matched', status: 'unknown' });
    return new LLMResponse(content, 1.0);
  }

  #match(prompt, system) {
    // Rules 1-4: Classification (prompt contains "classify" + incident keywords)
    if (prompt.includes('classify')) {
      if (['connection pool', 'postgresql', 'hikari'].some((kw) => prompt.includes(kw))) {
        return 'classify_database';
      }
      if (['double charge', 'duplicate', 'overcharge', 'refund'].some((kw) => prompt.includes(kw))) {
        return 'classify_billing';
      }
      if (['503', 'gateway', 'upstream', 'circuit breaker'].some((kw) => prompt.includes(kw))) {
        return 'classify_network';
      }
      if (['password reset', 'email', 'queue depth'].some((kw) => prompt.includes(kw))) {
        return 'classify_general';
      }
    }

    // Rules 5-9: Handler responses (check SYSTEM prompt)
    if (system && (system.includes('specialist') || system.includes('handler'))) {
      if (system.includes('database')) return 'handler_database';
      if (system.includes('billing') || system.includes('payment')) return 'handler_billing';
      if (system.includes('network')) return 'handler_network';
      if (system.includes('email')) return 'handler_email';
      return 'handler_general';
    }

    // Rules 10-12: Chain steps
    if ((prompt.includes('parse') || prompt.includes('extract')) && !prompt.includes('classify')) {
      return 'chain_parse';
    }
    if ((prompt.includes('root cause') || prompt.includes('analyze')) && !prompt.includes('classify')) {
      return 'chain_analyze';
    }
    if (prompt.includes('recommend')) {
      return 'chain_recommend';
    }

    // Rules 13-16: Parallel health checks
    const healthKw = ['health', 'status', 'check', 'assess'];
    if (prompt.includes('memory') && healthKw.some((kw) => prompt.includes(kw))) {
      return 'parallel_memory_check';
    }
    if (prompt.includes('cpu') && healthKw.some((kw) => prompt.includes(kw))) {
      return 'parallel_cpu_check';
    }
    if (prompt.includes('disk') && healthKw.some((kw) => prompt.includes(kw))) {
      return 'parallel_disk_check';
    }
    if (prompt.includes('network') && healthKw.some((kw) => prompt.includes(kw))) {
      return 'parallel_network_check';
    }

    // Rule 17: Fallback
    return null;
  }
}

export function createLLMClient({ cached = false } = {}) {
  if (cached) {
    const cachePath = join(__dirname, '..', '..', 'data', 'cached_responses.json');
    return new CachedLLMClient(cachePath);
  }

  return new LLMClient({
    baseUrl: process.env.OLLAMA_BASE_URL || 'http://localhost:11434',
    model: process.env.MODEL_NAME || 'qwen3.5:4b',
    temperature: parseFloat(process.env.MODEL_TEMPERATURE || '0.3'),
    timeout: parseInt(process.env.REQUEST_TIMEOUT || '30000', 10),
  });
}
