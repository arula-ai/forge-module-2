/**
 * Parallel Fan-Out Pattern — Run multiple health checks concurrently.
 *
 * The ParallelHealthChecker fans out 4 independent health checks in parallel
 * and aggregates results into an overall health report:
 *   - Memory Analysis
 *   - CPU Analysis
 *   - Disk I/O Analysis
 *   - Network Analysis
 *
 * Students: Implement runAllChecks() and aggregate(). Everything else is provided.
 */

import chalk from 'chalk';

/**
 * Build the 4 health check definitions.
 */
function buildChecks() {
  return [
    {
      name: 'Memory Analysis',
      subsystem: 'memory',
      promptTemplate:
        'Assess the memory health status for this incident.\n\n' +
        'Incident: {title}\n' +
        'Description: {description}\n\n' +
        'Check the memory utilization and report any concerns.\n' +
        'Respond with ONLY this JSON:\n' +
        '{\n' +
        '  "status": "healthy|warning|critical",\n' +
        '  "usage_percent": <number>,\n' +
        '  "details": "<description>"\n' +
        '}',
    },
    {
      name: 'CPU Analysis',
      subsystem: 'cpu',
      promptTemplate:
        'Assess the cpu health status for this incident.\n\n' +
        'Incident: {title}\n' +
        'Description: {description}\n\n' +
        'Check the CPU utilization and report any concerns.\n' +
        'Respond with ONLY this JSON:\n' +
        '{\n' +
        '  "status": "healthy|warning|critical",\n' +
        '  "usage_percent": <number>,\n' +
        '  "details": "<description>"\n' +
        '}',
    },
    {
      name: 'Disk I/O Analysis',
      subsystem: 'disk',
      promptTemplate:
        'Assess the disk health status for this incident.\n\n' +
        'Incident: {title}\n' +
        'Description: {description}\n\n' +
        'Check the disk I/O and storage utilization.\n' +
        'Respond with ONLY this JSON:\n' +
        '{\n' +
        '  "status": "healthy|warning|critical",\n' +
        '  "usage_percent": <number>,\n' +
        '  "details": "<description>"\n' +
        '}',
    },
    {
      name: 'Network Analysis',
      subsystem: 'network',
      promptTemplate:
        'Assess the network health status for this incident.\n\n' +
        'Incident: {title}\n' +
        'Description: {description}\n\n' +
        'Check the network connectivity and report any concerns.\n' +
        'Respond with ONLY this JSON:\n' +
        '{\n' +
        '  "status": "healthy|warning|critical",\n' +
        '  "details": "<description>"\n' +
        '}',
    },
  ];
}

/**
 * Run a single health check against the LLM.
 */
async function runSingleCheck(llm, check, incident) {
  const prompt = check.promptTemplate
    .replace('{title}', incident.title || 'N/A')
    .replace('{description}', incident.description || 'N/A');

  const start = performance.now();
  const response = await llm.chat(prompt, {
    system:
      'You are a system health check analyzer. Assess the health status of the specified subsystem. Respond ONLY with JSON.',
  });
  const durationMs = performance.now() - start;

  const data = response.asJson();
  return {
    name: check.name,
    subsystem: check.subsystem,
    status: data.status || 'unknown',
    details: data.details || 'No details available',
    durationMs: Math.round(durationMs * 10) / 10,
  };
}

export class ParallelHealthChecker {
  constructor(llm) {
    this.llm = llm;
    this.checks = buildChecks();
  }

  /**
   * Run all health checks concurrently and return aggregated report.
   *
   * TODO: Implement parallel health check execution.
   *     // 1. Create a promise for each check: runSingleCheck(this.llm, check, incident)
   *     // 2. Run ALL concurrently with Promise.allSettled(promises)
   *     // 3. Process results: if status is 'rejected', create a result with status="error"
   *     // 4. Display results with status icons
   *     // 5. Return this.aggregate(results, totalMs)
   */
  async runAllChecks(incident) {
    throw new Error('Implement runAllChecks — see pseudocode above');
  }

  /**
   * Aggregate individual check results into an overall health report.
   *
   * TODO: Implement result aggregation.
   *     // 1. Collect all statuses from results
   *     // 2. Determine overall status (priority: critical > error > warning > healthy)
   *     // 3. Build summary string
   *     // 4. Return { results, overallStatus, totalDurationMs, summary }
   */
  aggregate(results, totalMs) {
    throw new Error('Implement aggregate — see pseudocode above');
  }
}

// Export the helper for use in tests or other modules
ParallelHealthChecker.runSingleCheck = runSingleCheck;
