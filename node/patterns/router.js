/**
 * Intent Router Pattern — Classify incidents and route to specialist handlers.
 *
 * The IncidentRouter:
 *   1. Classifies an incident into a category (database, network, billing, etc.)
 *   2. Routes to a specialist handler based on the classification
 *   3. Falls back to a general handler if confidence is low
 *
 * Students: Implement classify() and route(). Everything else is provided.
 */

import chalk from 'chalk';

/** Categories for incident classification. */
export const IncidentCategory = {
  DATABASE: 'technical/database',
  NETWORK: 'technical/network',
  BILLING: 'billing/payment',
  EMAIL: 'general/email',
  OTHER: 'general/other',
};

const ALL_CATEGORIES = Object.values(IncidentCategory);

/**
 * Normalize a free-text category string to an IncidentCategory value.
 *
 * 1. Lowercase and strip whitespace
 * 2. Exact match against enum values
 * 3. Substring matching: database, network, billing/payment, email
 * 4. Default to OTHER
 */
export function matchCategory(raw) {
  const normalized = raw.toLowerCase().trim();

  // Exact match
  if (ALL_CATEGORIES.includes(normalized)) return normalized;

  // Substring matching
  if (normalized.includes('database')) return IncidentCategory.DATABASE;
  if (normalized.includes('network')) return IncidentCategory.NETWORK;
  if (normalized.includes('billing') || normalized.includes('payment')) return IncidentCategory.BILLING;
  if (normalized.includes('email')) return IncidentCategory.EMAIL;

  return IncidentCategory.OTHER;
}

/**
 * Run a handler against an incident.
 */
export async function handleIncident(llm, handler, incident) {
  const prompt =
    `Analyze this incident and provide your specialist assessment.\n\n` +
    `Title: ${incident.title || 'N/A'}\n` +
    `Description: ${incident.description || 'N/A'}\n` +
    `Severity: ${incident.severity || 'unknown'}\n` +
    `Logs:\n${incident.logs || 'No logs available'}\n\n` +
    `Respond with ONLY this JSON:\n` +
    `{\n` +
    `  "handler": "${handler.name}",\n` +
    `  "summary": "<one sentence assessment>",\n` +
    `  "priority": "<low|medium|high|critical>",\n` +
    `  "escalation_needed": <true|false>\n` +
    `}`;

  const response = await llm.chat(prompt, { system: handler.systemPrompt });
  const data = response.asJson();
  return {
    handler: data.handler || handler.name,
    summary: data.summary || 'No summary provided',
    priority: data.priority || 'medium',
    escalationNeeded: data.escalation_needed ?? false,
  };
}

/**
 * Build the 5 specialist handlers.
 */
function buildHandlers() {
  return {
    [IncidentCategory.DATABASE]: {
      name: 'Database Specialist',
      category: IncidentCategory.DATABASE,
      systemPrompt:
        'You are a database incident specialist. Analyze database-related incidents and provide actionable recommendations. Respond ONLY with JSON.',
    },
    [IncidentCategory.NETWORK]: {
      name: 'Network Specialist',
      category: IncidentCategory.NETWORK,
      systemPrompt:
        'You are a network infrastructure specialist. Analyze network and gateway incidents and provide remediation steps. Respond ONLY with JSON.',
    },
    [IncidentCategory.BILLING]: {
      name: 'Billing Specialist',
      category: IncidentCategory.BILLING,
      systemPrompt:
        'You are a billing and payment incident specialist. Analyze billing-related incidents and provide refund/resolution recommendations. Respond ONLY with JSON.',
    },
    [IncidentCategory.EMAIL]: {
      name: 'Email Specialist',
      category: IncidentCategory.EMAIL,
      systemPrompt:
        'You are an email systems specialist. Analyze email delivery incidents and provide resolution steps. Respond ONLY with JSON.',
    },
    [IncidentCategory.OTHER]: {
      name: 'General Specialist',
      category: IncidentCategory.OTHER,
      systemPrompt:
        'You are a general incident response specialist. Provide initial triage and recommendations. Respond ONLY with JSON.',
    },
  };
}

export class IncidentRouter {
  constructor(llm, { confidenceThreshold = 0.6 } = {}) {
    this.llm = llm;
    this.confidenceThreshold = confidenceThreshold;
    this.handlers = buildHandlers();
    this.fallbackHandler = this.handlers[IncidentCategory.OTHER];
  }

  /**
   * Classify an incident into a category using the LLM.
   *
   * TODO: Implement incident classification.
   *     // 1. Build list of valid categories from IncidentCategory
   *     // 2. Construct prompt with incident title, description, severity
   *     // 3. Ask LLM to classify — request JSON with: category, confidence (0-1), reasoning
   *     // 4. Parse response, match category using matchCategory()
   *     // 5. Look up handler from this.handlers (fallback to this.fallbackHandler)
   *     // 6. Return { category, confidence, reasoning, handlerName }
   */
  async classify(incident) {
    throw new Error('Implement classify — see pseudocode above');
  }

  /**
   * Classify an incident and route to the appropriate handler.
   *
   * TODO: Implement routing logic.
   *     // 1. Call this.classify(incident) to get classification
   *     // 2. If confidence >= this.confidenceThreshold, select matching handler
   *     // 3. If confidence < threshold, use this.fallbackHandler
   *     // 4. Call handleIncident(this.llm, handler, incident)
   *     // 5. Return { routeResult, handlerResponse }
   */
  async route(incident) {
    throw new Error('Implement route — see pseudocode above');
  }
}
