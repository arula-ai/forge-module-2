#!/usr/bin/env node
/**
 * Run this to verify your environment is correctly configured.
 */

import 'dotenv/config';

const baseUrl = process.env.OLLAMA_BASE_URL || 'http://localhost:11434';
const model = process.env.MODEL_NAME || 'qwen3.5:4b';

console.log(`Checking Ollama at ${baseUrl}...`);

try {
  // Check Ollama is running
  const tagsResp = await fetch(`${baseUrl}/api/tags`);
  const tagsData = await tagsResp.json();
  const modelNames = (tagsData.models || []).map((m) => m.name);
  console.log(`  Available models: ${JSON.stringify(modelNames)}`);

  // Check our model is available
  if (!modelNames.some((name) => name.includes(model))) {
    console.log(`  ERROR: Model '${model}' not found. Run: ollama pull ${model}`);
    process.exit(1);
  }

  // Test inference
  console.log(`Testing inference with ${model}...`);
  const chatResp = await fetch(`${baseUrl}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      model,
      messages: [{ role: 'user', content: 'Respond with: VERIFIED' }],
      stream: false,
      options: { temperature: 0.0 },
    }),
  });
  const chatData = await chatResp.json();
  console.log(`  Model response: ${chatData.message.content}`);

  console.log('\nAll checks passed. You\'re ready for the lab!');
} catch (e) {
  console.log(`  ERROR: Cannot reach Ollama — ${e.message}`);
  console.log('  Make sure \'ollama serve\' is running.');
  process.exit(1);
}
