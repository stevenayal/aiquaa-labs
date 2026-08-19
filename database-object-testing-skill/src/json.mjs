import { readFile } from 'node:fs/promises';

export async function readJson(path) {
  try {
    return JSON.parse(await readFile(path, 'utf8'));
  } catch (error) {
    throw new Error(`No se pudo leer JSON ${path}: ${error.message}`, { cause: error });
  }
}

export function stableStringify(value) {
  if (Array.isArray(value)) return `[${value.map(stableStringify).join(',')}]`;
  if (value && typeof value === 'object') {
    return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${stableStringify(value[key])}`).join(',')}}`;
  }
  return JSON.stringify(value);
}

export function getPath(value, path) {
  if (!path || path === '$') return value;
  const parts = path.replace(/^\$\.?/, '').replace(/\[(\d+)\]/g, '.$1').split('.').filter(Boolean);
  let current = value;
  for (const part of parts) {
    if (current === null || current === undefined || !(part in Object(current))) return undefined;
    current = current[part];
  }
  return current;
}

export function resolveEnv(value, env = process.env) {
  if (typeof value === 'string') {
    return value.replace(/\$\{ENV:([A-Z0-9_]+)\}/g, (_, name) => {
      if (!(name in env)) throw new Error(`Falta la variable de entorno ${name}`);
      return env[name];
    });
  }
  if (Array.isArray(value)) return value.map((item) => resolveEnv(item, env));
  if (value && typeof value === 'object') {
    return Object.fromEntries(Object.entries(value).map(([key, item]) => [key, resolveEnv(item, env)]));
  }
  return value;
}
