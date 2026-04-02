/**
 * Orchestrator Pattern — Compose all patterns into a full incident response pipeline.
 *
 * The IncidentOrchestrator runs 3 stages in sequence:
 *   1. Classification & Routing (Router pattern)
 *   2. Parallel Health Checks (Parallel pattern)
 *   3. Diagnostic Chain (Chain pattern)
 *
 * Then compiles an IncidentReport with results from all stages.
 *
 * Students: Implement processIncident(). Everything else is provided.
 */

import chalk from 'chalk';
import { createChainState } from './chain.js';

export const PipelineStage = {
  CLASSIFYING: 'classifying',
  HEALTH_CHECK: 'health_check',
  DIAGNOSING: 'diagnosing',
  COMPLETE: 'complete',
};

/**
 * Create an empty incident report.
 */
function createReport(incident) {
  return {
    incidentId: incident.id,
    title: incident.title || 'Unknown',
    classification: {},
    handlerResponse: {},
    healthReport: {},
    diagnosticChain: {},
    totalDurationMs: 0,
    stagesCompleted: [],
    errors: [],
  };
}

/**
 * Display the final report in the terminal.
 */
function displayReport(report) {
  console.log();

  // Classification
  if (report.classification && report.classification.category) {
    const cls = report.classification;
    const confidence = cls.confidence != null ? `${Math.round(cls.confidence * 100)}%` : 'N/A';
    console.log(chalk.bold.cyan('  Classification:'), `${cls.category} (confidence: ${confidence})`);
    console.log(chalk.cyan('  Handler:'), cls.handler || 'N/A');
  }

  // Handler response
  if (report.handlerResponse && report.handlerResponse.summary) {
    const hr = report.handlerResponse;
    console.log(chalk.cyan('  Assessment:'), hr.summary);
    console.log(chalk.cyan('  Priority:'), `${hr.priority || 'N/A'} | Escalation: ${hr.escalationNeeded ? 'Yes' : 'No'}`);
  }

  // Health report
  if (report.healthReport && report.healthReport.results) {
    const overall = (report.healthReport.overallStatus || 'unknown').toUpperCase();
    console.log(chalk.bold.cyan('\n  Health Status:'), overall);
    for (const r of report.healthReport.results) {
      const icons = { healthy: chalk.green('✓'), warning: chalk.yellow('⚠'), critical: chalk.red('✗'), error: chalk.red('!') };
      const icon = icons[r.status] || '?';
      console.log(`    ${icon} ${r.name}: ${(r.details || '').slice(0, 60)} (${Math.round(r.durationMs || 0)}ms)`);
    }
  }

  // Diagnostic chain
  if (report.diagnosticChain && Object.keys(report.diagnosticChain).length > 0) {
    console.log(chalk.bold.cyan('\n  Diagnostics:'));
    for (const [key, value] of Object.entries(report.diagnosticChain)) {
      const summary = typeof value === 'object' ? JSON.stringify(value).slice(0, 100) : String(value).slice(0, 100);
      console.log(`    ${chalk.dim(key + ':')} ${summary}`);
    }
  }

  // Summary
  console.log(
    chalk.bold(`\n  Total time: ${Math.round(report.totalDurationMs)}ms`) +
      ` | Stages: ${report.stagesCompleted.length}` +
      ` | Errors: ${report.errors.length}`
  );

  if (report.errors.length > 0) {
    for (const err of report.errors) {
      console.log(chalk.red(`  ⚠ ${err}`));
    }
  }

  const borderColor = report.errors.length > 0 ? chalk.yellow : chalk.green;
  console.log(borderColor(`\n  ── 📋 ${report.incidentId}: ${report.title} ──`));
  console.log(borderColor(`  Pipeline complete — ${report.stagesCompleted.length} stages\n`));
}

export class IncidentOrchestrator {
  constructor(router, healthChecker, diagnosticChain) {
    this.router = router;
    this.healthChecker = healthChecker;
    this.diagnosticChain = diagnosticChain;
  }

  /**
   * Run the full incident response pipeline.
   *
   * TODO: Implement the orchestration pipeline.
   *     // Initialize: start timer, empty arrays for stagesCompleted and errors,
   *     //             empty objects for classification, handlerResponse, healthReport, chainResults
   *
   *     // Stage 1: Classification & Routing
   *     // 1. Call this.router.route(incident)
   *     // 2. Extract classification: { category, confidence, reasoning, handler }
   *     // 3. Extract handlerResponse: { handler, summary, priority, escalationNeeded }
   *     // 4. Push PipelineStage.CLASSIFYING to stagesCompleted
   *     // 5. Wrap in try/catch — on failure, push error, don't stop pipeline
   *
   *     // Stage 2: Parallel Health Checks
   *     // 6. Call this.healthChecker.runAllChecks(incident)
   *     // 7. Extract healthReport with results array and overallStatus
   *     // 8. Push PipelineStage.HEALTH_CHECK to stagesCompleted
   *     // 9. Wrap in try/catch
   *
   *     // Stage 3: Diagnostic Chain
   *     // 10. Create chain state: createChainState(incident)
   *     // 11. Call this.diagnosticChain.execute(state)
   *     // 12. Extract chainResults from state.results
   *     // 13. Push PipelineStage.DIAGNOSING, merge chain errors
   *     // 14. Wrap in try/catch
   *
   *     // Stage 4: Compile Report
   *     // 15. Push PipelineStage.COMPLETE
   *     // 16. Build report object with all collected data
   *     // 17. Call displayReport(report)
   *     // 18. Return report
   */
  async processIncident(incident) {
    throw new Error('Implement processIncident — see pseudocode above');
  }
}

// Export helpers for external use
IncidentOrchestrator.displayReport = displayReport;
IncidentOrchestrator.createReport = createReport;
