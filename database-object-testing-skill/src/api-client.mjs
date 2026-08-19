export class DatabaseApiError extends Error {
  constructor(message, details = {}) {
    super(message);
    this.name = 'DatabaseApiError';
    this.details = details;
  }
}

export function createApiClient(target, env = process.env, fetchImpl = globalThis.fetch) {
  const baseUrl = env[target.baseUrlEnv];
  if (!baseUrl) throw new Error(`Falta ${target.baseUrlEnv} para el target ${target.name ?? 'sin nombre'}`);
  const token = target.tokenEnv ? env[target.tokenEnv] : undefined;
  if (target.tokenEnv && !token) throw new Error(`Falta ${target.tokenEnv} para autenticar el target`);
  const timeoutMs = target.timeoutMs ?? 30000;

  async function post(path, body) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);
    try {
      const response = await fetchImpl(new URL(path, baseUrl), {
        method: 'POST',
        headers: {
          'content-type': 'application/json',
          ...(token ? { authorization: `Bearer ${token}` } : {}),
          ...(target.headers ?? {})
        },
        body: JSON.stringify(body),
        signal: controller.signal
      });
      const text = await response.text();
      let payload;
      try { payload = text ? JSON.parse(text) : {}; } catch { payload = { raw: text }; }
      if (!response.ok) {
        throw new DatabaseApiError(`API respondió HTTP ${response.status}`, {
          status: response.status,
          payload
        });
      }
      return payload;
    } catch (error) {
      if (error.name === 'AbortError') throw new DatabaseApiError(`Timeout de ${timeoutMs} ms`);
      throw error;
    } finally {
      clearTimeout(timer);
    }
  }

  const paths = {
    execute: target.paths?.execute ?? '/v1/database/execute',
    explain: target.paths?.explain ?? '/v1/database/explain',
    inspect: target.paths?.inspect ?? '/v1/database/inspect',
    dependencies: target.paths?.dependencies ?? '/v1/database/dependencies'
  };
  return {
    execute: (request) => post(paths.execute, request),
    explain: (request) => post(paths.explain, request),
    inspect: (request) => post(paths.inspect, request),
    dependencies: (request) => post(paths.dependencies, request)
  };
}
