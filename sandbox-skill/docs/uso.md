# Guía de uso — sandbox-skill

## Instalación

```bash
npx skills add aiquaa-labs/sandbox-skill
```

Para agentes específicos:

```bash
npx skills add aiquaa-labs/sandbox-skill -a cursor
npx skills add aiquaa-labs/sandbox-skill -a windsurf
npx skills add aiquaa-labs/sandbox-skill -a cline
```

## Qué es

No genera archivos. Es el **contrato compartido** del entorno de práctica del curso —
la API `aiquaa-sandbox-api` y el front `aiquaa-sandbox-web`. Las skills `postman-newman`, `hurl`,
`playwright`, `bdd` y `jmeter` la consultan para no inventar endpoints, campos o tablas.

## Cuándo se activa

Automáticamente cuando el usuario menciona el sandbox, `x-api-key`, `qa_training`, o cualquiera
de los 10 grupos del curso. También al pedir explícitamente "consultá el contrato del sandbox".

## Contenido

| Archivo | Qué responde |
|---------|--------------|
| `skills/sandbox/SKILL.md` | auth, envelope, rate limit, precedencia de params, datos sembrados |
| `references/api-contract.md` | los 32 endpoints con campos exactos |
| `references/sql-endpoint.md` | endpoints SQL, guardrails, patrones de verificación en BD |
| `references/web-testids.md` | convención `data-testid` del front |
| `references/grupos.md` | grupo → módulo → endpoints → tablas |

## Obtener una API key

La entrega el docente por alumno — nunca se comparte una key entre varios (rompe el rate limit
individual de 30 req/min y mezcla el audit log). Guardarla en variable de entorno, nunca en un
archivo versionado.
