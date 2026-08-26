# Heurística de profundidad de validación (métrica 3)

No hay un solver genérico que determine si un test "valida de verdad" — la heurística reusa las
convenciones de nombre de archivo que ya usa el stack `aiquaa-labs` (mismo espíritu
determinístico que `qa-orchestrator-skill/references/signal-mapping.md`: reglas primero, juicio
del modelo solo para desempatar casos ambiguos, nunca como clasificador primario).

## Regla de negocio que esto implementa

> Un caso automatizado que solo valida un código de respuesta HTTP 200 sin verificar el
> resultado real de negocio (por ejemplo, el estado correspondiente en base de datos) no debe
> contarse como automatización de calidad, aunque figure como "caso automatizado" en el sistema.

## Paso 1 — ubicar el archivo de test desde el diff del PR

A partir de la lista de archivos cambiados en el PR (`az devops invoke --area git --resource
pullrequestiterationchanges`), matchear por prefijo:

| Prefijo / patrón | Skill de origen |
|---|---|
| `H_*.hurl` | `hurl-skill` |
| `T_*.spec.ts` | `playwright-skill` |
| `F_*.feature` + `S_*.steps.ts` | `bdd-skill` |
| `C_*.json` (colección) + request scripts `pm.test()` | `postman-newman-skill` |
| `N_*_Tests.cs` / `S_*_Steps.cs` (FlaUI) | `flaui-skill` |

Si el PR no contiene ningún archivo con estos prefijos: clasificar el caso como **Sin
evidencia** — no intentar adivinar cuál archivo "podría ser" el test por similitud de nombre.

## Paso 2 — grep de señal superficial vs. profunda

### `H_*.hurl` (hurl-skill)

- **Superficial:** el entry tiene una línea `HTTP 200` (o el código esperado) y no tiene bloque
  `[Asserts]`, o el bloque `[Asserts]` solo contiene `status ==`.
- **Profunda:** el bloque `[Asserts]` incluye al menos un `jsonpath "$..."` sobre el body, o hay
  un entry posterior contra `POST /api/v1/sql/select` (patrón de verificación en BD del
  `sandbox-skill`) encadenado al mismo caso.

### `T_*.spec.ts` (playwright-skill)

- **Superficial:** el único `expect(...)` relevante al resultado del caso es sobre
  `response.status()` (o equivalente `expect(response.ok()).toBeTruthy()`), sin más
  aserciones sobre el body ni sobre estado en BD.
- **Profunda:** hay al menos un `expect(...)` adicional sobre un campo del body de la respuesta,
  o una llamada de verificación en base de datos (mismo patrón `sql/select` del `sandbox-skill`)
  después de la acción.

### `F_*.feature` / `S_*.steps.ts` (bdd-skill)

- **Superficial:** el escenario solo tiene un step tipo "Then el código de respuesta debería
  ser X" (o equivalente en inglés "the response code should be X"), sin ningún step adicional de
  verificación de resultado.
- **Profunda:** hay un step adicional tipo "Then … en la base de datos" / "And el registro
  debería existir con estado …" que efectivamente verifica negocio, no solo transporte HTTP.

### `C_*.json` / `E_*.json` (postman-newman-skill)

- **Superficial:** el único test relevante en el request es
  `pm.response.to.have.status(...)` (o `pm.test("status", ...)` sobre el código), sin
  `pm.expect(jsonData...)` sobre el body.
- **Profunda:** hay al menos un `pm.expect(jsonData...)` (o `pm.response.to.have.jsonBody(...)`)
  sobre un campo del body, o un request encadenado de verificación en BD.

## Paso 3 — clasificación final por caso

Cada caso auditado recibe exactamente una etiqueta:

- **Profunda** — cuenta como automatización de calidad en el informe.
- **Superficial** — sigue contando como "automatizado" en la métrica 1 (Azure DevOps lo marca
  así), pero se reporta por separado como no-calidad. Es la señal que expone inflación de
  números — nunca se oculta ni se redondea hacia arriba.
- **Sin evidencia** — el archivo no se pudo localizar o no matchea ninguno de los prefijos
  conocidos. Se reporta como dato faltante explícito.

## Cuándo el juicio del modelo entra (segunda pasada, nunca primera)

Si el grep de un archivo no cae limpio en superficial ni profundo (ej. un `[Asserts]` con una
expresión no estándar, o un step Gherkin con fraseo distinto a los patrones listados), releer el
fragmento con criterio antes de marcar "Sin evidencia" — pero documentar en el informe que esa
clasificación puntual fue por lectura del modelo, no por regla determinística, para que quede
auditable.

## Ejemplos worked

Ver `examples/az-git-pr-diff-shallow.md` (clasifica Superficial) y
`examples/az-git-pr-diff-profundo.md` (clasifica Profunda) para el recorrido completo aplicado a
un diff real de PR.
