#!/usr/bin/env node
/**
 * AgentForge — Incident Response System (Node.js Track)
 *
 * Main entry point. Students do NOT modify this file.
 *
 * Usage:
 *     node agent_forge.js                    # Process all incidents
 *     node agent_forge.js --incident INC-001 # Process single incident
 *     node agent_forge.js --cached           # Use cached responses (offline mode)
 */

import 'dotenv/config';
import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import chalk from 'chalk';
import { createLLMClient } from './patterns/llm_client.js';
import { DiagnosticChain } from './patterns/chain.js';
import { IncidentRouter } from './patterns/router.js';
import { ParallelHealthChecker } from './patterns/parallel.js';
import { IncidentOrchestrator } from './patterns/orchestrator.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

function loadIncidents() {
  const path = join(__dirname, '..', 'data', 'incidents.json');
  return JSON.parse(readFileSync(path, 'utf-8'));
}

function parseArgs() {
  const args = process.argv.slice(2);
  const result = { incident: null, cached: false };
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--incident' && args[i + 1]) {
      result.incident = args[++i];
    } else if (args[i] === '--cached') {
      result.cached = true;
    }
  }
  return result;
}

async function main() {
  const args = parseArgs();

  // Banner
  console.log(chalk.cyan('╔══════════════════════════════════════════════╗'));
  console.log(chalk.cyan('║') + chalk.bold.cyan(' AgentForge — Incident Response System      ') + chalk.cyan('║'));
  console.log(chalk.cyan('║') + chalk.dim(' Module 2: Core Agentic Patterns             ') + chalk.cyan('║'));
  console.log(chalk.cyan('╚══════════════════════════════════════════════╝'));
  console.log();

  // Load incidents
  let incidents = loadIncidents();

  if (args.incident) {
    incidents = incidents.filter((inc) => inc.id === args.incident);
    if (incidents.length === 0) {
      console.log(chalk.red(`Error: Incident '${args.incident}' not found.`));
      const all = loadIncidents();
      console.log(chalk.dim(`Available: ${all.map((i) => i.id).join(', ')}`));
      process.exit(1);
    }
  }

  // Create LLM client
  const llm = createLLMClient({ cached: args.cached });
  const mode = args.cached ? 'cached' : 'live';
  console.log(chalk.dim(`Mode: ${mode} | Incidents: ${incidents.length}\n`));

  // Wire up patterns
  const chain = new DiagnosticChain(llm);
  const router = new IncidentRouter(llm);
  const checker = new ParallelHealthChecker(llm);
  const orchestrator = new IncidentOrchestrator(router, checker, chain);

  // Process incidents
  const start = performance.now();
  const results = [];
  const errors = [];

  for (const incident of incidents) {
    console.log(chalk.bold('='.repeat(60)));
    console.log(chalk.bold.cyan(`Processing: ${incident.id} — ${incident.title}`));
    console.log(chalk.dim(`Severity: ${incident.severity} | Source: ${incident.source}`));

    try {
      const report = await orchestrator.processIncident(incident);
      results.push(report);
    } catch (e) {
      console.log(chalk.red(`Failed to process ${incident.id}: ${e.message}`));
      errors.push(`${incident.id}: ${e.message.slice(0, 100)}`);
    }
  }

  const totalMs = performance.now() - start;

  // Summary
  console.log(chalk.bold('='.repeat(60)));
  const borderColor = errors.length > 0 ? chalk.yellow : chalk.green;
  console.log(borderColor('┌─ Session Summary ─────────────────────────┐'));
  console.log(borderColor(`│ Incidents processed: ${results.length}/${incidents.length}`));
  console.log(borderColor(`│ Total time: ${Math.round(totalMs)}ms`));
  console.log(borderColor(`│ Errors: ${errors.length}`));
  console.log(borderColor('└───────────────────────────────────────────┘'));

  if (errors.length > 0) {
    for (const err of errors) {
      console.log(chalk.red(`  • ${err}`));
    }
  }
}

main().catch((err) => {
  console.error(chalk.red(`Fatal error: ${err.message}`));
  process.exit(1);
});
