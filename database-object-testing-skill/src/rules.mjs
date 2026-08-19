import { readdir, readFile } from 'node:fs/promises';
import { join } from 'node:path';

const BLOCK = /```dbtest-rule\s*([\s\S]*?)```/g;

export async function loadRules(directory) {
  const entries = await readdir(directory, { withFileTypes: true });
  const files = entries.filter((entry) => entry.isFile() && entry.name.endsWith('.md')).map((entry) => join(directory, entry.name));
  const rules = [];
  for (const file of files) {
    const markdown = await readFile(file, 'utf8');
    for (const match of markdown.matchAll(BLOCK)) {
      let rule;
      try { rule = JSON.parse(match[1]); } catch (error) {
        throw new Error(`Bloque dbtest-rule inválido en ${file}: ${error.message}`);
      }
      validateRule(rule, file);
      rules.push({ ...rule, file });
    }
  }
  return rules;
}

function validateRule(rule, file) {
  for (const field of ['id', 'message', 'mode', 'pattern']) {
    if (!rule[field]) throw new Error(`Regla de ${file} sin campo obligatorio: ${field}`);
  }
  if (!['require', 'forbid'].includes(rule.mode)) throw new Error(`Regla ${rule.id}: mode debe ser require o forbid`);
  try { new RegExp(rule.pattern, rule.flags ?? 'i'); } catch (error) {
    throw new Error(`Regla ${rule.id}: expresión regular inválida: ${error.message}`);
  }
}

export function evaluateRules(rules, { objectType, source = '' }) {
  return rules
    .filter((rule) => !rule.appliesTo?.length || rule.appliesTo.includes('*') || rule.appliesTo.includes(objectType))
    .map((rule) => {
      const matched = new RegExp(rule.pattern, rule.flags ?? 'i').test(source);
      return {
        id: rule.id,
        severity: rule.severity ?? 'warning',
        message: rule.message,
        passed: rule.mode === 'require' ? matched : !matched,
        file: rule.file
      };
    });
}
