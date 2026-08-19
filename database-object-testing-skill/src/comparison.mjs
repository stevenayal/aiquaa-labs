import { getPath, stableStringify } from './json.mjs';

function normalized(value, unordered) {
  if (!unordered || !Array.isArray(value)) return value;
  return [...value].sort((a, b) => stableStringify(a).localeCompare(stableStringify(b)));
}

export function compareFunctional(baseline, candidate, config = {}) {
  const paths = config.paths ?? ['$.data'];
  return paths.map((path) => {
    const before = normalized(getPath(baseline, path), config.unorderedRows ?? true);
    const after = normalized(getPath(candidate, path), config.unorderedRows ?? true);
    return { path, passed: stableStringify(before) === stableStringify(after), baseline: before, candidate: after };
  });
}

export function compareCosts(baseline, candidate, config = {}) {
  const thresholds = config.thresholds ?? {};
  const metrics = config.metrics ?? Object.keys(thresholds);
  return metrics.map((metric) => {
    const before = Number(getPath(baseline, metric));
    const after = Number(getPath(candidate, metric));
    const limitPercent = Number(thresholds[metric] ?? 0);
    if (!Number.isFinite(before) || !Number.isFinite(after)) {
      return { metric, passed: false, error: 'Métrica ausente o no numérica', baseline: before, candidate: after };
    }
    const changePercent = before === 0 ? (after === 0 ? 0 : Infinity) : ((after - before) / before) * 100;
    return { metric, passed: changePercent <= limitPercent, baseline: before, candidate: after, changePercent, limitPercent };
  });
}
