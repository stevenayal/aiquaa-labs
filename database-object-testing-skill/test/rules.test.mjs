import assert from 'node:assert/strict';
import { resolve } from 'node:path';
import test from 'node:test';
import { evaluateRules, loadRules } from '../src/rules.mjs';

test('carga reglas Markdown y detecta COMMIT', async () => {
  const rules = await loadRules(resolve('rules'));
  assert.ok(rules.length >= 2);
  const results = evaluateRules(rules, { objectType: 'procedure', source: 'BEGIN INSERT INTO X VALUES (1); COMMIT; END;' });
  assert.equal(results.find((result) => result.id === 'DB-TRANS-001').passed, false);
});
