import { mkdir, writeFile } from 'node:fs/promises';
import { join } from 'node:path';

function escapeXml(value) {
  return String(value).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;');
}

export async function writeReports(report, outputDirectory) {
  await mkdir(outputDirectory, { recursive: true });
  const paths = {
    json: join(outputDirectory, 'db-test-report.json'),
    markdown: join(outputDirectory, 'db-test-report.md'),
    junit: join(outputDirectory, 'db-test-junit.xml'),
    pdf: join(outputDirectory, 'db-test-report.pdf')
  };
  await Promise.all([
    writeFile(paths.json, `${JSON.stringify(report, null, 2)}\n`),
    writeFile(paths.markdown, markdown(report)),
    writeFile(paths.junit, junit(report))
  ]);
  return paths;
}

function markdown(report) {
  const lines = [
    `# Informe de pruebas de objetos de base de datos`, '',
    `- Suite: ${report.suite}`, `- Estado: **${report.status.toUpperCase()}**`,
    `- Casos: ${report.summary.total}; aprobados: ${report.summary.passed}; fallidos: ${report.summary.failed}`, '',
    '| Caso | Objeto | Estado | Hallazgos |', '|---|---|---:|---:|'
  ];
  for (const item of report.cases) {
    const failures = item.findings.filter((finding) => !finding.passed).length;
    lines.push(`| ${item.id} | ${item.objectType} | ${item.status} | ${failures} |`);
  }
  lines.push('');
  for (const item of report.cases.filter((entry) => entry.status === 'failed')) {
    lines.push(`## ${item.id}`, '');
    for (const finding of item.findings.filter((entry) => !entry.passed)) {
      lines.push(`- **${finding.category}**: ${finding.message ?? finding.path ?? finding.metric ?? finding.error}`);
    }
    lines.push('');
  }
  return `${lines.join('\n')}\n`;
}

function junit(report) {
  const failures = report.cases.filter((item) => item.status === 'failed').length;
  const cases = report.cases.map((item) => {
    const failed = item.findings.filter((finding) => !finding.passed);
    const failure = failed.length ? `<failure message="${escapeXml(`${failed.length} hallazgo(s)`)}">${escapeXml(JSON.stringify(failed, null, 2))}</failure>` : '';
    return `  <testcase classname="database-object" name="${escapeXml(item.id)}" time="${item.durationMs / 1000}">${failure}</testcase>`;
  }).join('\n');
  return `<?xml version="1.0" encoding="UTF-8"?>\n<testsuite name="${escapeXml(report.suite)}" tests="${report.cases.length}" failures="${failures}">\n${cases}\n</testsuite>\n`;
}
