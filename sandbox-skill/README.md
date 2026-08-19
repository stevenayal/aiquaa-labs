# sandbox-skill

Contrato del entorno de práctica **aiquaa Sandbox** — API REST, endpoints de SQL crudo y front
web usados en el curso de automatización de pruebas de aiquaa. No genera archivos de prueba;
es el contexto que consultan `postman-newman-skill`, `hurl-skill`, `playwright-skill`, `bdd-skill`
y `jmeter-skill` para no inventar endpoints, campos ni tablas.

## Instalación

```bash
npx skills add aiquaa-labs/sandbox-skill
```

## Entorno

| Pieza | URL |
|-------|-----|
| API | `https://aiquaa-sandbox-api.vercel.app` |
| Docs | `https://aiquaa-sandbox-api.vercel.app/docs` |
| Spec OpenAPI | `https://aiquaa-sandbox-api.vercel.app/api/v1/docs` |

## Contenido

- `skills/sandbox/SKILL.md` — auth (`x-api-key`), envelope de respuesta, rate limit (30/min),
  precedencia de parámetros, datos sembrados.
- `references/api-contract.md` — 32 endpoints con campos exactos.
- `references/sql-endpoint.md` — `POST /api/v1/sql/select` y `/sql/update`, guardrails,
  patrones de verificación API → BD.
- `references/web-testids.md` — convención `data-testid` del front de práctica.
- `references/grupos.md` — los 10 grupos del curso → módulo → endpoints → tablas.

→ [Guía de uso](./docs/uso.md)

## Licencia

MIT
