import { DatabaseApiError, createApiClient } from './api-client.mjs';
import { getPath, resolveEnv, setPath } from './json.mjs';

const DEFAULT_BOUNDARIES = ['oldMax', 'oldMaxPlusOne', 'newMax', 'newMaxPlusOne'];

export async function analyzeColumnImpact(specification, options = {}) {
  validateSpecification(specification);
  const env = options.env ?? process.env;
  const targetConfig = specification.targets?.candidate ?? specification.targetApi;
  const client = createApiClient({ ...targetConfig, name: 'candidate' }, env, options.fetchImpl);
  const discovery = await client.dependencies({
    target: specification.target,
    change: specification.change,
    operations: specification.probe?.operations ?? ['INSERT', 'UPDATE'],
    includeObjectTypes: specification.discovery?.includeObjectTypes ?? ['procedure', 'package', 'trigger', 'view']
  });
  if (!Array.isArray(discovery.dependencies)) throw new Error('La API de dependencias debe devolver dependencies[]');

  const cases = [];
  const profiles = specification.probe?.profiles ?? [{ name: 'ascii', character: 'A' }];
  const boundaries = resolveBoundaries(specification.change, specification.probe?.boundaries);
  const requiredOperations = specification.probe?.operations ?? ['INSERT', 'UPDATE'];

  for (const dependency of discovery.dependencies) {
    cases.push(dependencyCoverageCase(dependency, requiredOperations, specification.change));
    for (const invocation of dependency.invocations ?? []) {
      for (const profile of profiles) {
        for (const boundary of boundaries) {
          cases.push(await executeProbe({ client, dependency, invocation, profile, boundary, specification, env }));
        }
      }
    }
  }

  if (!discovery.dependencies.length) {
    cases.push({
      id: 'DEPENDENCY-DISCOVERY', objectType: 'table', status: 'failed', durationMs: 0,
      findings: [{ category: 'dependency', passed: false, message: 'La API no encontró dependencias; no es posible afirmar ausencia de impacto.' }]
    });
  }
  for (const unresolved of discovery.unresolved ?? []) {
    cases.push({
      id: `UNRESOLVED::${unresolved.id ?? unresolved.name ?? cases.length}`,
      objectType: unresolved.objectType ?? 'unknown', status: 'failed', durationMs: 0,
      findings: [{
        category: 'dependency', passed: false,
        message: `Dependencia no resoluble: ${unresolved.reason ?? unresolved.message ?? unresolved.id ?? 'sin detalle'}`
      }]
    });
  }
  const passed = cases.filter((item) => item.status === 'passed').length;
  return {
    schemaVersion: 1,
    suite: specification.name,
    metadata: {
      ...(specification.metadata ?? {}),
      change: `${specification.target.schema}.${specification.target.table}.${specification.target.column}: ${specification.change.fromLength} -> ${specification.change.toLength} ${specification.change.lengthSemantics ?? 'CHAR'}`
    },
    generatedAt: new Date().toISOString(),
    status: passed === cases.length ? 'passed' : 'failed',
    summary: { total: cases.length, passed, failed: cases.length - passed },
    impact: {
      target: specification.target,
      change: specification.change,
      dependencies: discovery.dependencies.map(summarizeDependency),
      unresolved: discovery.unresolved ?? [],
      discoveredAt: discovery.discoveredAt
    },
    cases
  };
}

function dependencyCoverageCase(dependency, requiredOperations, change) {
  const invocations = dependency.invocations ?? [];
  const findings = [{ category: 'dependency', passed: true, message: `Referencia detectada hacia la tabla core: ${dependency.id}` }];
  for (const operation of requiredOperations) {
    if (!(dependency.operations ?? []).includes(operation)) continue;
    const covered = invocations.some((invocation) => invocation.operation === operation);
    findings.push({ category: 'coverage', passed: covered, message: `${operation}: ${covered ? 'invocación disponible' : 'sin invocación de prueba'}` });
  }
  for (const invocation of invocations) {
    if (Number.isFinite(invocation.effectiveLength)) {
      findings.push({
        category: 'definition',
        passed: invocation.effectiveLength >= change.toLength,
        message: `${invocation.id}: longitud efectiva ${invocation.effectiveLength}; nueva longitud ${change.toLength}`
      });
    } else {
      findings.push({ category: 'definition', passed: false, severity: 'warning', message: `${invocation.id}: longitud efectiva no informada por la API` });
    }
    if ((invocation.transformations ?? []).some((item) => /substr|truncate|cast/i.test(item))) {
      findings.push({ category: 'definition', passed: false, message: `${invocation.id}: transformación potencialmente truncante` });
    }
  }
  const failed = findings.some((finding) => !finding.passed && finding.severity !== 'warning');
  return {
    id: `${dependency.id}::COVERAGE`, objectType: dependency.object?.type ?? 'unknown',
    status: failed ? 'failed' : 'passed', durationMs: 0, findings
  };
}

async function executeProbe({ client, dependency, invocation, profile, boundary, specification, env }) {
  const started = performance.now();
  const semantics = specification.change.lengthSemantics ?? 'CHAR';
  const value = generateValue(boundary.length, profile.character, semantics);
  const request = resolveEnv(setPath(invocation.request, invocation.valuePath, value), env);
  request.transactionMode = 'rollback';
  const expectedAccepted = boundary.length <= specification.change.toLength;
  const findings = [];
  try {
    const response = await client.execute(request);
    if (!expectedAccepted) {
      findings.push({ category: 'impact-probe', passed: false, message: `${boundary.label}: la operación aceptó ${boundary.length} cuando debía rechazarla` });
    } else {
      findings.push({ category: 'impact-probe', passed: true, message: `${boundary.label}: operación aceptada con ${boundary.length}` });
      const persisted = getPath(response, invocation.resultPath);
      findings.push({
        category: 'value-preservation',
        passed: typeof persisted === 'string' && persisted === value,
        message: typeof persisted === 'string' && persisted === value
          ? `${boundary.label}: valor preservado sin truncamiento`
          : `${boundary.label}: valor ausente, transformado o truncado`,
        expectedLength: measure(value, semantics),
        actualLength: typeof persisted === 'string' ? measure(persisted, semantics) : undefined
      });
    }
  } catch (error) {
    const expectedRejection = !expectedAccepted && error instanceof DatabaseApiError && error.details?.status >= 400 && error.details?.status < 500;
    findings.push({
      category: 'impact-probe', passed: expectedRejection,
      message: expectedRejection
        ? `${boundary.label}: rechazo esperado para ${boundary.length}`
        : `${boundary.label}: fallo inesperado: ${error.message}`
    });
  }
  const failed = findings.some((finding) => !finding.passed);
  return {
    id: `${dependency.id}::${invocation.id}::${profile.name}::${boundary.label}`,
    objectType: dependency.object?.type ?? 'unknown', status: failed ? 'failed' : 'passed',
    durationMs: Math.round(performance.now() - started), findings
  };
}

function resolveBoundaries(change, names = DEFAULT_BOUNDARIES) {
  const values = {
    oldMax: { label: 'old-max', length: change.fromLength },
    oldMaxPlusOne: { label: 'old-max-plus-one', length: change.fromLength + 1 },
    newMax: { label: 'new-max', length: change.toLength },
    newMaxPlusOne: { label: 'new-max-plus-one', length: change.toLength + 1 }
  };
  return names.map((name) => {
    if (!values[name]) throw new Error(`Frontera desconocida: ${name}`);
    return values[name];
  });
}

function generateValue(length, character = 'A', semantics = 'CHAR') {
  if ([...character].length !== 1) throw new Error('Cada perfil debe usar un único carácter Unicode');
  if (semantics === 'CHAR') return character.repeat(length);
  if (semantics !== 'BYTE') throw new Error(`lengthSemantics no soportada: ${semantics}`);
  const bytes = Buffer.byteLength(character, 'utf8');
  const repeats = Math.floor(length / bytes);
  let value = character.repeat(repeats);
  while (Buffer.byteLength(value, 'utf8') < length) value += 'A';
  return value;
}

function measure(value, semantics) {
  return semantics === 'BYTE' ? Buffer.byteLength(value, 'utf8') : [...value].length;
}

function summarizeDependency(dependency) {
  return {
    id: dependency.id,
    object: dependency.object,
    operations: dependency.operations ?? [],
    invocations: (dependency.invocations ?? []).map(({ id, operation, effectiveLength, transformations }) => ({ id, operation, effectiveLength, transformations }))
  };
}

function validateSpecification(specification) {
  if (!specification?.name || !specification.target || !specification.change) throw new Error('El análisis necesita name, target y change');
  if (!specification.targets?.candidate && !specification.targetApi) throw new Error('El análisis necesita targets.candidate o targetApi');
  for (const field of ['schema', 'table', 'column']) if (!specification.target[field]) throw new Error(`target necesita ${field}`);
  for (const field of ['fromLength', 'toLength']) if (!Number.isInteger(specification.change[field])) throw new Error(`change necesita ${field} entero`);
  if (specification.change.toLength <= specification.change.fromLength) throw new Error('Esta versión especializada requiere una ampliación: toLength > fromLength');
}

export const impactInternals = { generateValue, measure, resolveBoundaries };
