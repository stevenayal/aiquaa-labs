import path from 'node:path';

/**
 * aiquaa-labs vendor patch.
 *
 * Upstream Archify hardcodes `assets/template.html`. This repo ships two
 * templates from one vendored runtime:
 *
 *   assets/template.html          online  — async Google Fonts link (JetBrains Mono)
 *   assets/template.offline.html  offline — zero external requests
 *
 * `ARCHIFY_TEMPLATE` selects one. Values: "online" (default), "offline", or an
 * explicit path. Follows the same env-var convention as ARCHIFY_REPO_ROOT.
 */
export function resolveTemplatePath(skillRoot) {
  const requested = (process.env.ARCHIFY_TEMPLATE || '').trim();
  if (!requested || requested === 'online') return path.join(skillRoot, 'assets/template.html');
  if (requested === 'offline') return path.join(skillRoot, 'assets/template.offline.html');
  return path.isAbsolute(requested) ? requested : path.resolve(skillRoot, requested);
}
