import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const reporterPath = fileURLToPath(new URL('../reporter/database_report.py', import.meta.url));

export function generatePdfReport({ inputPath, outputPath, python = process.env.DBTEST_PYTHON }) {
  const executable = python ?? (process.platform === 'win32' ? 'python' : 'python3');
  return new Promise((resolve, reject) => {
    const child = spawn(executable, [reporterPath, '--results', inputPath, '--output', outputPath], {
      stdio: ['ignore', 'pipe', 'pipe']
    });
    let stdout = '';
    let stderr = '';
    child.stdout.on('data', (chunk) => { stdout += chunk; });
    child.stderr.on('data', (chunk) => { stderr += chunk; });
    child.on('error', (error) => reject(new Error(
      `No se pudo iniciar Python (${executable}). Definir DBTEST_PYTHON o usar --python. ${error.message}`,
      { cause: error }
    )));
    child.on('close', (code) => {
      if (code === 0) resolve({ outputPath, stdout: stdout.trim() });
      else reject(new Error(`No se pudo generar el PDF: ${stderr.trim() || stdout.trim() || `exit ${code}`}`));
    });
  });
}
