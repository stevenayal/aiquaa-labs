#!/usr/bin/env node
import { resolve } from 'node:path';
import { readJson } from './json.mjs';
import { writeReports } from './reporters.mjs';
import { loadRules } from './rules.mjs';
import { runSuite } from './runner.mjs';

function args(argv) {
  const [command, ...rest] = argv;
  const options = {};
  for (let index = 0; index < rest.length; index += 2) {
    const key = rest[index]?.replace(/^--/, '');
    if (!key || !rest[index + 1]) throw new Error(`Argumento inválido: ${rest[index] ?? ''}`);
    options[key] = rest[index + 1];
  }
  return { command, options };
}

async function main() {
  const { command, options } = args(process.argv.slice(2));
  if (command === 'validate-rules') {
    const rules = await loadRules(resolve(options.rules ?? 'rules'));
    console.log(`Reglas válidas: ${rules.length}`);
    return;
  }
  if (command !== 'run' || !options.suite) {
    console.error('Uso: db-object-test run --suite <suite.json> [--rules rules] [--output results]');
    console.error('     db-object-test validate-rules --rules <directorio>');
    process.exitCode = 2;
    return;
  }
  const suite = await readJson(resolve(options.suite));
  const report = await runSuite(suite, { rulesDirectory: options.rules ? resolve(options.rules) : undefined });
  await writeReports(report, resolve(options.output ?? 'results'));
  console.log(`${report.status.toUpperCase()}: ${report.summary.passed}/${report.summary.total} casos aprobados`);
  process.exitCode = report.status === 'passed' ? 0 : 1;
}

main().catch((error) => {
  console.error(error.message);
  process.exitCode = 2;
});
