/**
 * Sequential Chain Pattern — Diagnostic analysis pipeline.
 *
 * The DiagnosticChain runs a series of LLM calls in sequence, where each step
 * builds on the results of the previous one:
 *   1. Parse Logs → extract structured error data
 *   2. Analyze Root Cause → determine what went wrong
 *   3. Generate Recommendations → suggest fixes
 *
 * Students: Implement the execute() method. Everything else is provided.
 */

import chalk from 'chalk';

/**
 * Create a fresh chain state from an incident.
 */
export function createChainState(incident) {
  return {
    incidentId: incident.id,
    rawInput: JSON.stringify(incident),
    logs: incident.logs || '',
    results: {},
    stepsCompleted: [],
    errors: [],
  };
}

/**
 * Build the 3 diagnostic chain steps.
 */
function buildSteps() {
  return [
    {
      name: 'Parse Logs',
      systemPrompt:
        'You are a log analysis expert. Extract structured data from logs. Respond ONLY with JSON.',
      userPromptTemplate:
        'Parse the following incident logs and extract key information.\n\n' +
        'Logs:\n{logs}\n\n' +
        'Respond with ONLY this JSON:\n' +
        '{\n' +
        '  "errors_found": <number>,\n' +
        '  "error_types": ["<type1>", "<type2>"],\n' +
        '  "time_range": "<start> - <end>",\n' +
        '  "affected_services": ["<service1>", "<service2>"]\n' +
        '}',
      outputKey: 'parsed_logs',
    },
    {
      name: 'Analyze Root Cause',
      systemPrompt:
        'You are a root cause analysis expert. Respond ONLY with JSON.',
      userPromptTemplate:
        'Based on the parsed log data, analyze the root cause of this incident.\n\n' +
        'Parsed Logs:\n{parsed_logs}\n\n' +
        'Respond with ONLY this JSON:\n' +
        '{\n' +
        '  "root_cause": "<description of the root cause>",\n' +
        '  "impact": "<description of the impact>",\n' +
        '  "severity_assessment": "<HIGH/MEDIUM/LOW — explanation>"\n' +
        '}',
      outputKey: 'root_cause',
    },
    {
      name: 'Generate Recommendations',
      systemPrompt:
        'You are a DevOps remediation expert. Respond ONLY with JSON.',
      userPromptTemplate:
        'Based on the root cause analysis, recommend actions to resolve ' +
        'and prevent this incident.\n\n' +
        'Root Cause Analysis:\n{root_cause}\n\n' +
        'Respond with ONLY this JSON:\n' +
        '{\n' +
        '  "immediate_actions": ["<action1>", "<action2>"],\n' +
        '  "investigation_steps": ["<step1>", "<step2>"],\n' +
        '  "prevention": ["<measure1>", "<measure2>"]\n' +
        '}',
      outputKey: 'recommendations',
    },
  ];
}

/**
 * Interpolate state values into a prompt template.
 */
function formatPrompt(template, state) {
  let result = template;
  result = result.replace('{logs}', state.logs);
  result = result.replace('{incident_id}', state.incidentId);
  result = result.replace('{raw_input}', state.rawInput);
  for (const [key, value] of Object.entries(state.results)) {
    const replacement = typeof value === 'object' ? JSON.stringify(value, null, 2) : String(value);
    result = result.replace(`{${key}}`, replacement);
  }
  return result;
}

export class DiagnosticChain {
  constructor(llm) {
    this.llm = llm;
    this.steps = buildSteps();
  }

  /**
   * Execute the diagnostic chain: run each step sequentially, passing state through.
   *
   * TODO: Implement the chain execution loop.
   * For each step in this.steps:
   *     // 1. Build the prompt using formatPrompt(step.userPromptTemplate, state)
   *     // 2. Call the LLM: await this.llm.chat(prompt, { system: step.systemPrompt })
   *     // 3. Parse the JSON response using response.asJson()
   *     // 4. Store the result in state.results[step.outputKey]
   *     // 5. Track completion: state.stepsCompleted.push(step.name)
   *     // 6. Handle errors: push to state.errors, log, but don't crash the loop
   */
  async execute(state) {
    throw new Error('Implement the chain execution loop — see pseudocode above');
  }
}

// Re-export helper for use in other modules
DiagnosticChain.formatPrompt = formatPrompt;
