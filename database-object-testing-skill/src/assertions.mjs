import { getPath, stableStringify } from './json.mjs';

const operators = {
  equals: (actual, expected) => stableStringify(actual) === stableStringify(expected),
  notEquals: (actual, expected) => stableStringify(actual) !== stableStringify(expected),
  contains: (actual, expected) => Array.isArray(actual)
    ? actual.some((item) => stableStringify(item) === stableStringify(expected))
    : String(actual).includes(String(expected)),
  matches: (actual, expected) => new RegExp(expected).test(String(actual)),
  greaterThan: (actual, expected) => Number(actual) > Number(expected),
  greaterThanOrEqual: (actual, expected) => Number(actual) >= Number(expected),
  lessThan: (actual, expected) => Number(actual) < Number(expected),
  lessThanOrEqual: (actual, expected) => Number(actual) <= Number(expected),
  exists: (actual, expected = true) => expected ? actual !== undefined : actual === undefined
};

export function evaluateAssertions(payload, assertions = []) {
  return assertions.map((assertion) => {
    const actual = getPath(payload, assertion.path);
    const operation = assertion.operator ?? 'equals';
    const evaluate = operators[operation];
    if (!evaluate) return { ...assertion, passed: false, actual, error: `Operador desconocido: ${operation}` };
    try {
      return { ...assertion, passed: evaluate(actual, assertion.expected), actual };
    } catch (error) {
      return { ...assertion, passed: false, actual, error: error.message };
    }
  });
}
