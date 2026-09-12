# archify-skill — CLAUDE.md

## Project

Skill de diagramación técnica para aiquaa-labs. Vive en `Z:\Proyectos\aiquaa-labs\archify-skill`.
Motor **vendorizado** de [tt-a1i/archify](https://github.com/tt-a1i/archify) v2.16.0 (MIT).
No es una skill QA de primera línea — es soporte: diagramar arquitectura de suites,
pipelines CI, flujos de datos bajo prueba, ciclos de vida de defectos.

## Structure

```
skills/archify/          ← variante online  (webfont vía CDN)
skills/archify-offline/  ← variante offline (cero peticiones externas)
bin/                     ← CLI: archify.mjs, preview.mjs, visual-check.mjs
renderers/               ← compiladores por tipo + shared/
schemas/                 ← JSON Schema por tipo + common
assets/template.html         ← template online
assets/template.offline.html ← template offline (generado, ver abajo)
examples/                ← 14 specs JSON de referencia (solo forma, no hechos)
references/              ← contratos de autoría, entrega, viewer + upstream-SKILL.md
delta/ recipes/ brand-marks/ migrations/ scripts/
```

## Vendorizado — qué significa acá

Copia congelada dentro del repo. **No hay `npm install`.** `package.json` solo declara
devDependencies (ajv, parse5, saxes, simple-icons) que no se usan en la ruta de ejecución.
Requisito único: **Node ≥18**.

Descartado del upstream: `test/` (1.7M) y los 5 HTML de ejemplo (3.5M). Total vendorizado: 2.5M.

## Parche local sobre el upstream — 3 archivos

Upstream hardcodea `assets/template.html` en dos lugares. Para servir dos variantes desde
un solo runtime se agregó:

| Archivo | Cambio |
|---|---|
| `renderers/shared/template-path.mjs` | **nuevo** — resuelve el template según `ARCHIFY_TEMPLATE` |
| `renderers/shared/cli.mjs:29` | usa `resolveTemplatePath(skillRoot)` (lectura funcional) |
| `bin/archify.mjs:1224` | usa `resolveTemplatePath(skillRoot)` (check de `doctor`) |

`ARCHIFY_TEMPLATE` acepta `online` (default), `offline`, o una ruta explícita. Sigue la
misma convención que el `ARCHIFY_REPO_ROOT` del upstream.

**Al sincronizar con upstream hay que reaplicar este parche.** Son 3 puntos, todos marcados
con el comentario `aiquaa-labs vendor patch`.

## Regenerar el template offline

`assets/template.offline.html` es `assets/template.html` menos el bloque de Google Fonts
(preconnect + link + noscript, líneas ~33-42), reemplazado por un comentario. Si actualizás
el upstream, regeneralo y verificá:

```bash
grep -oE 'https?://[a-zA-Z0-9./_?&=;+-]+' assets/template.offline.html | grep -v 'w3.org'
```

Salida vacía = correcto. `w3.org` es el namespace XML de SVG, no una descarga.

## Key rules

- Comandos siempre desde `archify-skill/` — `skillRoot` se resuelve como el padre de `bin/`
- `ARCHIFY_UPDATE_CHECK_DISABLED=1` siempre — la copia está congelada, el chequeo no sirve
- Variante offline: además `ARCHIFY_TEMPLATE=offline`, y `brands capture <url>` prohibido
- Aceptación showcase = **9/9 checks, 0 errores, 0 warnings**. 4 checks es validación básica
- `deliver` con exit ≠ 0 nunca se reporta como éxito
- Una validación final que pasa congela el candidato — no editarlo después
- `deliver` prueba el artefacto; `visual-check` prueba el navegador; la revisión perceptual
  necesita una persona. Son tres afirmaciones distintas, nunca mezclarlas
- Skills: editar solo los `SKILL.md`. El runtime vendorizado no se toca salvo re-sync

## Licencia

MIT. `LICENSE` y la atribución en el frontmatter de ambos SKILL.md se conservan.
Upstream: tt-a1i/archify · basado en Cocoon-AI/architecture-diagram-generator (MIT, v1.0).
