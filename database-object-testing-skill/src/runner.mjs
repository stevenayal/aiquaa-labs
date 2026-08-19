import { createApiClient } from './api-client.mjs';
import { evaluateAssertions } from './assertions.mjs';
import { compareCosts, compareFunctional } from './comparison.mjs';
import { resolveEnv } from './json.mjs';
import { evaluateRules, loadRules } from './rules.mjs';

export async function runSuite(suite, options = {}) {
  validateSuite(suite);
  const env = options.env ?? process.env;
  const rules = options.rulesDirectory ? await loadRules(options.rulesDirectory) : [];
  const clients = Object.fromEntries(Object.entries(suite.targets).map(([key, target]) => [key, createApiClient({ ...target, name: key }, env, options.fetchImpl)]));
  const results = [];
  for (const testCase of suite.cases) results.push(await runCase(testCase, suite, clients, rules, env));
  const passed = results.filter((item) => item.status === 'passed').length;
  return {
    schemaVersion: 1,
    suite: suite.name,
    metadata: suite.metadata ?? {},
    generatedAt: new Date().toISOString(),
    status: passed === results.length ? 'passed' : 'failed',
    summary: { total: results.length, passed, failed: results.length - passed },
    cases: results
  };
}

async function runCase(testCase, suite, clients, rules, env) {
  const started = performance.now();
  const findings = [];
  const responses = {};
  const plans = {};
  try {
    const request = resolveEnv(testCase.request, env);
    for (const targetName of ['baseline', 'candidate']) {
      if (clients[targetName]) responses[targetName] = await clients[targetName].execute(request);
    }
    const evaluated = evaluateAssertions(responses.candidate ?? responses.baseline, testCase.assertions);
    findings.push(...evaluated.map((item) => ({ ...item, category: 'assertion', message: `${item.path} ${item.operator ?? 'equals'}` })));

    if (responses.baseline && responses.candidate && testCase.compare?.functional !== false) {
      findings.push(...compareFunctional(responses.baseline, responses.candidate, testCase.compare?.functional).map((item) => ({ ...item, category: 'functional-diff', message: `Diferencia en ${item.path}` })));
    }

    if (responses.baseline && responses.candidate && testCase.compare?.cost) {
      for (const targetName of ['baseline', 'candidate']) plans[targetName] = await clients[targetName].explain(request);
      findings.push(...compareCosts(plans.baseline, plans.candidate, testCase.compare.cost).map((item) => ({ ...item, category: 'cost', message: `Costo ${item.metric}` })));
    }

    if (rules.length) {
      let source = request.statement ?? '';
      if (testCase.request.object) {
        const inspected = await (clients.candidate ?? clients.baseline).inspect({ object: testCase.request.object });
        source = inspected.source ?? inspected.ddl ?? source;
      }
      findings.push(...evaluateRules(rules, { objectType: testCase.objectType, source }).map((item) => ({ ...item, category: 'rule' })));
    }
  } catch (error) {
    findings.push({ category: 'execution', passed: false, message: error.message, details: error.details });
  }
  const failed = findings.some((finding) => !finding.passed && (finding.category !== 'rule' || finding.severity === 'error'));
  const reportedFindings = findings.map((finding) => {
    if (suite.reporting?.includeEvidence) return finding;
    const { actual, expected, details, ...safeFinding } = finding;
    if (finding.category === 'cost') return safeFinding;
    const { baseline, candidate, ...withoutComparedData } = safeFinding;
    return withoutComparedData;
  });
  return {
    id: testCase.id,
    objectType: testCase.objectType,
    status: failed ? 'failed' : 'passed',
    durationMs: Math.round(performance.now() - started),
    findings: reportedFindings,
    ...(suite.reporting?.includeResponses ? { responses } : {}),
    plans
  };
}

function validateSuite(suite) {
  if (!suite?.name) throw new Error('La suite necesita name');
  if (!suite.targets?.candidate && !suite.targets?.baseline) throw new Error('La suite necesita al menos un target');
  if (!Array.isArray(suite.cases) || !suite.cases.length) throw new Error('La suite necesita cases');
  const ids = new Set();
  for (const testCase of suite.cases) {
    if (!testCase.id || !testCase.objectType || !testCase.request) throw new Error('Cada caso necesita id, objectType y request');
    if (ids.has(testCase.id)) throw new Error(`ID de caso duplicado: ${testCase.id}`);
    ids.add(testCase.id);
  }
}
