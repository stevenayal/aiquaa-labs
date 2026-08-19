---
name: sandbox
description: >
  Contrato del entorno de práctica aiquaa Sandbox — API REST de 30 endpoints,
  endpoints de SQL crudo para verificación en base de datos, front web con
  data-testid y los 10 grupos del curso de automatización. Provee URLs, headers
  de autenticación (x-api-key), envelope de respuesta, códigos de error, rate
  limit y datos sembrados, para que cualquier agente genere pruebas contra el
  sandbox sin inventar campos.
  Usar cuando el usuario mencione "sandbox", "aiquaa-sandbox-api", "API del curso",
  "entorno de práctica", "x-api-key", "qa_training", "grupo 1..10", o pida
  automatizar contra https://aiquaa-sandbox-api.vercel.app.
  Auto-activa como contexto de las skills postman-newman, hurl, playwright, bdd y jmeter.
---

Sandbox contract. Claude read facts. No invent fields. Terse output.

---

## Qué es el sandbox

Entorno de práctica del curso de automatización de aiquaa. Dos aplicaciones desplegadas:

| Pieza | URL | Para qué |
|-------|-----|----------|
| API REST + SQL | `https://aiquaa-sandbox-api.vercel.app` | pruebas de API, BD y rendimiento |
| Docs OpenAPI 3.1 | `https://aiquaa-sandbox-api.vercel.app/docs` | contrato navegable (Scalar) |
| Spec JSON | `https://aiquaa-sandbox-api.vercel.app/api/v1/docs` | fuente para generar colecciones |
| Front web | repo `aiquaa-sandbox-web` (dev `http://localhost:3001`) | pruebas E2E de navegador |

Local: API en `http://localhost:3000`, front en `http://localhost:3001`.

**Regla número uno: no inventar campos.** Todo nombre de campo, endpoint o tabla
sale de este documento o de `/api/v1/docs`. Si algo no está acá, pedirlo — no asumirlo.

---

## Autenticación — `x-api-key`

```
x-api-key: sbx_alumno01_xxxxxxxxxxxx
```

- Header **`x-api-key`** en toda petición. **No hay JWT, no hay OAuth, no hay cookies.**
- La key es un string estático, **sin expiración**. Se revoca poniendo `active = false`.
- Key faltante, desconocida o inactiva → **401 `UNAUTHORIZED`** con el mismo mensaje genérico.
- Sin auth: solo `/`, `/docs` y `/api/v1/docs`.

⚠️ **`POST /api/v1/auth/login` NO es el login de la API.** Es login *de negocio*: recibe un
`email`, valida que exista un usuario activo y registra un evento en `sesiones`. No devuelve
token. No hay columna de password en ninguna tabla. La API se autentica **solo** con `x-api-key`.

Nunca hardcodear la key en archivos versionados. Siempre variable de entorno / colección:
`{{apiKey}}` (Postman), `{{apiKey}}` (Hurl), `process.env.SANDBOX_API_KEY` (Playwright/BDD),
`${__P(apiKey)}` (JMeter).

---

## Envelope de respuesta

Éxito — **siempre** envuelto en `data`:

```json
{ "data": { "id": 1, "nombre": "Ana Torres" } }
```

Los endpoints de SQL agregan `rowCount`:

```json
{ "data": [ { "id": 1 } ], "rowCount": 1 }
```

Error — **siempre** envuelto en `error`:

```json
{ "error": { "code": "VALIDATION_ERROR", "message": "...", "details": "..." } }
```

| `code` | HTTP | Cuándo |
|--------|------|--------|
| `UNAUTHORIZED` | 401 | key faltante, inválida o inactiva |
| `RATE_LIMITED` | 429 | superó 30 req/min |
| `VALIDATION_ERROR` | 400 | zod rechazó el body/query, o regla de negocio |
| `EXECUTION_ERROR` | 400 | Postgres rechazó la sentencia (mensaje crudo de PG) |
| `NOT_FOUND` | 404 | recurso inexistente |
| `INTERNAL_ERROR` | 500 | falla inesperada |

Assertion base para cualquier prueba: éxito → existe `data`; fallo → existe `error.code`.

---

## Rate limit — 30 req / 60 s por API key

Ventana deslizante, contada **por API key**, aplicada a **todos** los endpoints autenticados.

Respuesta 429 con headers:

```
Retry-After: <segundos>
X-RateLimit-Limit: 30
X-RateLimit-Remaining: 0
X-RateLimit-Reset: <timestamp>
```

Impacto por tipo de prueba — **decirlo siempre antes de generar**:

| Tipo | Impacto |
|------|---------|
| Funcional (Postman/Hurl) | una colección de más de 30 requests corridas sin pausa empieza a dar 429 |
| BDD | cada verificación en BD consume una petición extra — contarlas |
| E2E web | el front hace varias llamadas por pantalla — el límite llega rápido |
| Rendimiento | con una sola key, 30 req/min es el techo real; ver `jmeter` y su sección de rate limit |

Solo `/`, `/docs` y `/api/v1/docs` están fuera del límite.

---

## Precedencia de parámetros

El handler mezcla los inputs así:

```
{ ...query, ...body, ...pathParams }
```

**El path gana siempre.** El body pisa al query. Consecuencia práctica: en
`PATCH /api/v1/usuarios/{id}/kyc`, mandar `"id": 99` en el body **no** hace nada — vale el del path.
Es un buen caso de prueba negativa para enseñar precedencia.

Segundo detalle: los endpoints POST/PATCH también aceptan sus campos por **query string**.

---

## Datos sembrados — deterministas

`npm run db:seed` hace `TRUNCATE ... RESTART IDENTITY CASCADE` y siembra siempre lo mismo:

| Tabla | Filas |
|-------|-------|
| usuarios | 18 |
| sesiones | 43 |
| cuentas | 24 |
| transferencias | 25 |
| facturas | 24 |
| pagos | 12 |
| tarjetas | 20 |
| notificaciones | 30 |
| ordenes | 30 |
| items_orden | 50 |
| reservas | 20 |
| movimientos | 32 |
| roles | 4 (`admin`, `soporte`, `auditor`, `operador`) |
| usuario_roles | 11 |
| tickets | 27 |

Fixtures negativos listos para usar: **los usuarios con id 4, 8 y 13 tienen `activo = false`.**
Sirven para probar `POST /api/v1/auth/login` → 400, sin crear datos.

Emails de ejemplo: `ana.torres@example.com` … `sergio.campos@example.com`.

⚠️ **Las escrituras no están aisladas por alumno.** Todos comparten el mismo dataset:
`POST /api/v1/ordenes`, `/tarjetas`, `/usuarios` insertan filas reales, y `sql/update` modifica
las existentes. Los datos se van ensuciando hasta el próximo `db:seed` — que además **reinicia
los ids**, así que ningún test debe depender de un id fijo creado por otro alumno.
Escribir pruebas que creen su propio dato y lo referencien por variable.

---

## Referencias

| Archivo | Contenido |
|---------|-----------|
| `references/api-contract.md` | los 32 endpoints con campos exactos |
| `references/sql-endpoint.md` | `sql/select` y `sql/update`: body, guardrails, patrones |
| `references/web-testids.md` | convención `data-testid` del front + rutas |
| `references/grupos.md` | Grupo 1..10 → módulo → endpoints → tablas |

---

## Context Intake — antes de generar pruebas contra el sandbox

Preguntar, una a la vez:

1. **¿Qué grupo / módulo?** (1..10 — ver `references/grupos.md`). Define endpoints y tablas.
2. **¿API, web, BD o rendimiento?** Define qué skill acompaña.
3. **¿Tenés tu `x-api-key`?** Sin key no corre nada. La entrega el docente.
4. **¿Local o desplegado?** `http://localhost:3000` vs `https://aiquaa-sandbox-api.vercel.app`.
5. **¿Verificás en BD?** Si sí → `references/sql-endpoint.md` y avisar del costo en rate limit.

Confirmar antes de generar:

```
CONTEXTO SANDBOX:
  GRUPO:      <n> — <módulo>
  BASE URL:   <url>
  ENDPOINTS:  <lista>
  TABLAS:     <tablas qa_training a verificar o "sin verificación en BD">
  AUTH:       x-api-key vía variable de entorno
  RATE LIMIT: 30 req/min — <n> peticiones estimadas por corrida
```

---

## Boundaries

Esta skill **no genera archivos de prueba** — provee el contrato.
La generación la hacen `postman-newman`, `hurl`, `playwright`, `bdd` o `jmeter`.
No inventa endpoints, campos ni tablas fuera de lo documentado acá.
No expone ni pide credenciales de base de datos — el alumno solo usa `x-api-key`.
