import assert from 'node:assert/strict';
import { mkdtemp, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import test from 'node:test';
import { createMockApi } from '../examples/mock-api.mjs';
import { runSuite } from '../src/runner.mjs';

function listen(server) {
  return new Promise((resolveListen) => server.listen(0, '127.0.0.1', () => resolveListen(server.address().port)));
}

test('ejecuta assertions, diff, costos y reglas vía API', async (context) => {
  const baseline = createMockApi('baseline');
  const candidate = createMockApi('candidate');
  const [baselinePort, candidatePort] = await Promise.all([listen(baseline), listen(candidate)]);
  context.after(() => { baseline.close(); candidate.close(); });

  const suite = {
    name: 'integration',
    targets: {
      baseline: { baseUrlEnv: 'BASE_URL', tokenEnv: 'TOKEN' },
      candidate: { baseUrlEnv: 'CANDIDATE_URL', tokenEnv: 'TOKEN' }
    },
    cases: [{
      id: 'CASE-1',
      objectType: 'package',
      request: { object: { schema: 'CRM', name: 'PKG_CUSTOMER.GET_STATUS' }, arguments: { customerId: 42 }, transactionMode: 'rollback' },
      assertions: [{ path: '$.data.out.status', operator: 'equals', expected: 'ACTIVE' }],
      compare: {
        functional: { paths: ['$.data'] },
        cost: { metrics: ['$.cost'], thresholds: { '$.cost': 10 } }
      }
    }]
  };
  const report = await runSuite(suite, {
    env: { BASE_URL: `http://127.0.0.1:${baselinePort}`, CANDIDATE_URL: `http://127.0.0.1:${candidatePort}`, TOKEN: 'local-example-token' },
    rulesDirectory: resolve('rules')
  });
  assert.equal(report.status, 'passed');
  assert.equal(report.summary.passed, 1);
  assert.equal('responses' in report.cases[0], false);
  assert.equal('baseline' in report.cases[0].findings.find((finding) => finding.category === 'cost'), true);
  assert.ok(report.cases[0].findings.some((finding) => finding.category === 'cost'));
  assert.ok(report.cases[0].findings.some((finding) => finding.category === 'rule'));
});

test('una regresión funcional falla la suite', async (context) => {
  const baseline = createMockApi('baseline');
  const port = await listen(baseline);
  context.after(() => baseline.close());
  const suite = {
    name: 'assertion-failure',
    targets: { candidate: { baseUrlEnv: 'URL', tokenEnv: 'TOKEN' } },
    cases: [{
      id: 'CASE-FAIL', objectType: 'procedure', request: { arguments: { customerId: 1 } },
      assertions: [{ path: '$.data.out.status', operator: 'equals', expected: 'BLOCKED' }]
    }]
  };
  const report = await runSuite(suite, { env: { URL: `http://127.0.0.1:${port}`, TOKEN: 'local-example-token' } });
  assert.equal(report.status, 'failed');
});
