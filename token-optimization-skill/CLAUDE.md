# token-optimization-skill — CLAUDE.md

## Project

Skill de proceso para reducir consumo de tokens en sesiones de Claude del curso de
automatización aiquaa. Owned by aiquaa-labs. No genera archivos — es una capa de criterio
sobre qué herramienta usar primero y cuándo comprimir salida.

## Structure

```
skills/token-optimization/  ← skill principal (criterio de herramienta + compresión)
docs/                        ← guía de uso en español, con ejemplos antes/después
```

Sin `examples/` ni `references/` — a diferencia del resto del stack, esta skill no produce
archivos de salida (`.json`, `.hurl`, `.jmx`, etc.), solo cambia comportamiento del agente.

## Key rules

- No vendorea `caveman` — lo referencia y linkea a
  `postman-newman-skill/skills/caveman/SKILL.md`. Evita una tercera copia del mismo contenido
  en el repo (ya vive ahí y en su fork upstream, JuliusBrussee/caveman).
- codegraph y engram son servidores MCP, no paquetes npm — la skill documenta buenas
  prácticas de uso, nunca instala ni configura servidores MCP.
- Degradación elegante: si codegraph/engram no están disponibles en la sesión del alumno, la
  skill sigue funcionando con `Grep`/`Glob`/`Read` normales — nunca bloquea el trabajo.
- Nunca sacrifica corrección por ahorro de tokens: código, commits, PRs y contenido técnico
  siempre van completos (mismo límite que `caveman`).
