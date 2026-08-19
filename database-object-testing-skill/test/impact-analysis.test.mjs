import assert from 'node:assert/strict';
import test from 'node:test';
import { createMockApi } from '../examples/mock-api.mjs';
import { analyzeColumnImpact, impactInternals } from '../src/impact-analysis.mjs';

function listen(server) {
  return new Promise((resolve) => server.listen(0, '127.0.0.1', () => resolve(server.address().port)));
}

function specification() {
  return {
    name: 'customer-name-impact',
    target: { schema: 'CRM', table: 'CUSTOMER', column: 'DISPLAY_NAME' },
    change: { dataType: 'VARCHAR2', fromLength: 50, toLength: 100, lengthSemantics: 'CHAR' },
    targets: { candidate: { baseUrlEnv: 'URL', tokenEnv: 'TOKEN' } },
    probe: {
      operations: ['INSERT', 'UPDATE'],
      boundaries: ['oldMax', 'oldMaxPlusOne', 'newMax', 'newMaxPlusOne'],
      profiles: [{ name: 'ascii', character: 'A' }]
    }
  };
}

test('demuestra que SP y packages preservan la nueva longitud', async (context) => {
  const server = createMockApi('impact-safe');
  const port = await listen(server);
  context.after(() => server.close());
  const report = await analyzeColumnImpact(specification(), {
    env: { URL: `http://127.0.0.1:${port}`, TOKEN: 'local-example-token' }
  });
  assert.equal(report.status, 'passed');
  assert.equal(report.impact.dependencies.length, 2);
  assert.ok(report.cases.some((item) => item.id.includes('old-max-plus-one')));
});

test('detecta truncamiento en un procedimiento dependiente', async (context) => {
  const server = createMockApi('impact-truncating');
  const port = await listen(server);
  context.after(() => server.close());
  const report = await analyzeColumnImpact(specification(), {
    env: { URL: `http://127.0.0.1:${port}`, TOKEN: 'local-example-token' }
  });
  assert.equal(report.status, 'failed');
  assert.ok(report.cases.some((item) => item.findings.some((finding) => finding.category === 'value-preservation' && !finding.passed)));
  assert.ok(report.cases.some((item) => item.findings.some((finding) => finding.category === 'definition' && !finding.passed)));
});

test('no declara ausencia de impacto con dependencias sin resolver', async (context) => {
  const server = createMockApi('impact-unresolved');
  const port = await listen(server);
  context.after(() => server.close());
  const report = await analyzeColumnImpact(specification(), {
    env: { URL: `http://127.0.0.1:${port}`, TOKEN: 'local-example-token' }
  });
  assert.equal(report.status, 'failed');
  assert.equal(report.impact.unresolved.length, 1);
  assert.ok(report.cases.some((item) => item.id.startsWith('UNRESOLVED::')));
});

test('genera probes exactos con semántica BYTE', () => {
  const value = impactInternals.generateValue(5, 'Ñ', 'BYTE');
  assert.equal(Buffer.byteLength(value, 'utf8'), 5);
  assert.equal(impactInternals.measure(value, 'BYTE'), 5);
});
