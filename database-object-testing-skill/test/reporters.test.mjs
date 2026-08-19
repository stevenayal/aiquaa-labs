import assert from 'node:assert/strict';
import { mkdtemp, readFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import test from 'node:test';
import { writeReports } from '../src/reporters.mjs';

test('prepara rutas para los cuatro formatos de informe', async (context) => {
  const directory = await mkdtemp(join(tmpdir(), 'db-test-reports-'));
  context.after(() => rm(directory, { recursive: true, force: true }));
  const report = {
    suite: 'sample', status: 'passed', summary: { total: 1, passed: 1, failed: 0 },
    cases: [{ id: 'CASE-1', objectType: 'view', status: 'passed', durationMs: 2, findings: [] }]
  };
  const paths = await writeReports(report, directory);
  assert.equal(paths.pdf, join(directory, 'db-test-report.pdf'));
  assert.match(await readFile(paths.markdown, 'utf8'), /APROBADOS|aprobados/i);
  assert.match(await readFile(paths.junit, 'utf8'), /<testsuite/);
});
