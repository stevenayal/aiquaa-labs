---
name: qa-router
description: >
  Router de consumo para el stack QA. Decide en qué nivel de costo se ejecuta
  cada operación: extractor determinístico (tier 0, cero tokens de LLM),
  subagente barato con contexto aislado (tier 1), o la sesión principal
  (tier 2, solo razonamiento). Digiere artefactos QA pesados — .jtl de JMeter,
  JSON de Newman, JUnit/NUnit XML, reportes de Playwright, .jmx, colecciones
  Postman, OpenAPI, payloads de Azure DevOps, diffs de PR — a digests de ~50
  líneas que conservan el 100% de los fallos. Instala un hook PreToolUse que
  bloquea la lectura cruda de esos artefactos. No depende de ningún proveedor
  externo ni de servidores MCP.
  Usar cuando el usuario mencione "optimizar tokens", "router", "digest",
  "resultados de la corrida", "analizar el .jtl", "por qué falló la suite",
  "el reporte de newman", "el contexto se llena", o cuando esté por leerse
  cualquier archivo de resultados de una herramienta de testing.
  Auto-activa antes de leer un artefacto de resultados de cualquier skill del
  stack.
---

Artefacto pesado nunca entra crudo. Extractor primero, subagente después, sesión principal solo para decidir.

---

## ¿Qué es esta skill?

Las skills de `aiquaa-labs` generan y corren suites; sus **resultados** son el mayor
consumidor de contexto del stack. Un `.jtl` de una corrida de carga pesa cientos de MB, un
JSON de Newman varios MB, un reporte de Playwright otro tanto. Leerlos crudos es imposible o
carísimo, y el 99% de ese volumen no aporta nada a la decisión que hay que tomar.

Esta skill implementa el patrón *shunt* (ver `docs/router-qa-relevamiento.md` en la raíz del
repo) adaptado a QA: separa el trabajo por **costo**, no por tema. La diferencia con el
original es que en QA los artefactos pesados son máquina-parseables, así que el "worker
barato" casi siempre es un script — costo cero, salida determinística y auditable — y no otro
modelo.

**No decide qué probar** (eso es `qa-orchestrator-skill`) ni **cómo se ve la respuesta** (eso
es `caveman`). Decide **quién ejecuta y a qué costo**.

---

## Comandos

| Comando | Acción |
|---------|--------|
| `/router:digest <archivo>` | Detecta el tipo y corre su extractor tier 0. Es el comando que se usa el 90% del tiempo. |
| `/router:instalar` | Instala el hook `PreToolUse` en `.claude/settings.json` del proyecto. **Pide confirmación explícita** — modifica configuración del usuario. |
| `/router:estado` | Umbral vigente, hook instalado sí/no, extractores disponibles, tier activo. |
| `/router:leer <glob>` | Delega al subagente `qa-bulk-reader` (tier 1). El contenido no entra a este contexto. |
| `/router:escribir <spec> --reference <archivo>` | Delega a `qa-code-writer` (tier 1). Sin `--reference` no corre. |
| `/router:costo` | Ahorro acumulado desde el ledger (`.qa-router/ledger.jsonl`). |
| `/router:off` \| `/router:on` | Escape hatch por sesión (`QA_ROUTER_OFF=1`). |

---

## Decisión de tier — tabla operativa

Correr esta tabla **antes** de leer cualquier archivo. Tabla completa con rutas y matchers en
`references/routing-policy.md`.

| Condición | Tier | Qué hacer |
|---|---|---|
| `.jtl`, `.jmx`, `*newman*.json`, `*postman_collection.json`, `*junit*.xml`, `*TestResult.xml`, reporte JSON de Playwright, OpenAPI, payload de `az`, `.har` | **0** | `python3 extractors/router_digest.py <archivo>` |
| Diff de PR o rango git | **0** | `extractors/diff_digest.sh <base>..<head>` |
| Archivo de texto > **400 líneas** sin extractor | **1** | Subagente `qa-bulk-reader` |
| Más de 3 búsquedas independientes sobre el repo | **1** | Subagente `qa-bulk-reader` |
| Log de CI / stdout largo de pipeline | **1** | Subagente `qa-log-triage` (después del extractor, si aplica) |
| Boilerplate desde un patrón existente | **1** | Subagente `qa-code-writer`, con `--reference` obligatorio |
| Todo lo demás | **2** | Sesión principal |

### Qué NUNCA baja de tier 2

Límite duro, sin excepción:

- Edición quirúrgica por número de línea.
- Semántica de asserts, valores esperados, nombres de campo/tabla, credenciales de entorno.
- Diagnóstico de causa raíz de un fallo.
- Decisión de ruteo ambigua de `qa-orchestrator`, veredicto del informe consolidado.
- Cualquier gate human-in-the-loop, y el escaneo de secretos como decisión (el *match* es
  tier 0; qué hacer con él es tier 2).

---

## Extractores tier 0

Todos: `python3 extractors/<x>.py <archivo> [opciones]`. Solo stdlib, sin dependencias nuevas.

| Extractor | Entrada | Devuelve |
|---|---|---|
| `router_digest.py` | cualquiera | Dispatcher — detecta el tipo y delega. `--list` para ver los soportados |
| `jtl_digest.py` | `.jtl` CSV de JMeter | p50/p90/p95/p99, error%, throughput, top samplers, clusters de error. `--baseline <jtl>` compara degradación |
| `newman_digest.py` | JSON de Newman | Totales + 100% de los fallos agrupados + cluster dominante |
| `junit_digest.py` | JUnit o NUnit3 XML | Totales + fallos con mensaje y primera línea de stack |
| `pw_digest.py` | reporte JSON de Playwright | Fallos con archivo:línea, retries y conteo de flaky |
| `jmx_digest.py` | `.jmx` | Thread groups, samplers, assertions, variables, CSV data set, salida |
| `collection_digest.py` | colección Postman v2.1 | Árbol de requests + tests por request + requests sin tests |
| `openapi_digest.py` | OpenAPI JSON | Tabla de endpoints. `--tag`/`--grep` para traer solo los del grupo |
| `az_digest.py` | JSON de Azure DevOps | Proyección de los campos de `metrics-spec.md`. `--fields a,b,c` |
| `diff_digest.sh` | rango git o `.diff` | Archivos, +/-, extensiones y cabeceras de hunk. Sin cuerpos |
| `ledger_report.py` | ledger | Ahorro acumulado por tipo de artefacto |

**Códigos de salida:** `0` digest OK · `2` uso incorrecto o archivo inexistente ·
`3` formato no reconocido → **delegar a tier 1**, nunca leer el crudo como consuelo.

Regla dura: un extractor que falla a mitad de camino **sale 3 y no imprime nada**. Nunca
devuelve un digest parcial como si fuera completo.

---

## Enforcement — el hook

La política escrita se erosiona en sesiones largas; el bloqueo no. `/router:instalar` agrega a
`.claude/settings.json`:

```json
{ "hooks": { "PreToolUse": [ { "matcher": "Read|Bash",
  "hooks": [ { "type": "command",
    "command": "$CLAUDE_PROJECT_DIR/qa-router-skill/hooks/qa-router-guard.sh" } ] } ] } }
```

El guard bloquea (`exit 2`) y en el mismo mensaje nombra la alternativa exacta. **Permite**
siempre: `Read` con `offset`/`limit`, `grep`/`wc` acotados, y la ejecución de los propios
extractores. Detalle completo y troubleshooting en `references/hooks-setup.md`.

Escape hatch, siempre disponible: `QA_ROUTER_OFF=1` o `QA_ROUTER_MIN_LINES=<n>`. Un bloqueo
sin salida se vuelve un obstáculo el día que el extractor falla — el escape hatch no es
opcional.

---

## Integración con el resto del stack

| Skill | Cuándo llamar al router |
|---|---|
| `jmeter-skill` | Siempre antes de analizar un `.jtl` — `/jmeter:report` nunca carga el crudo |
| `postman-newman-skill` | `/postman:fix` parte del digest de Newman, no del JSON |
| `playwright-skill` | Triage de fallos: `pw_digest.py` y después `qa-log-triage` si hace falta |
| `flaui-skill` | `TestResult.xml` de NUnit vía `junit_digest.py` |
| `hurl-skill` | Reporte JUnit vía `junit_digest.py` |
| `qa-orchestrator-skill` | Intake de `/qa:analizar`: `diff_digest.sh` o `qa-diff-scout` antes de puntuar |
| `qa-productivity-skill` | Payloads de `az` vía `az_digest.py` |
| `sandbox-skill` | OpenAPI vía `openapi_digest.py --tag <grupo>` |
| `token-optimization-skill` | Sigue siendo el criterio de hábitos; el router es su enforcement |

---

## Medición

Cada extractor anota en `.qa-router/ledger.jsonl`: `bytes_raw`, `bytes_digest`, `ratio` y
`tokens_saved_est`. `/router:costo` agrega el total.

**El ahorro en tokens es una estimación (bytes ÷ 4), no una medición del tokenizer**, y se
reporta siempre como tal. En artefactos la reducción medida es de 95–99%; en una sesión QA
completa el ahorro realista es 40–70%, porque el razonamiento y los gates siguen en tier 2 y
no desaparecen. Ver `references/cost-ledger-schema.md`.

---

## Fallos comunes y fixes

| Síntoma | Causa | Fix |
|---------|-------|-----|
| El extractor sale 3 sobre un archivo válido | Formato distinto al esperado (ej. `.jtl` en XML en vez de CSV) | El mensaje de stderr dice cuál es. Reconfigurar la herramienta, o delegar a `qa-bulk-reader` |
| El hook bloquea algo legítimo | Umbral bajo para ese archivo | `QA_ROUTER_MIN_LINES=<n>` para la sesión, o `QA_ROUTER_OFF=1` puntual. No editar el guard |
| El hook no bloquea nada | Falta `jq`, o `CLAUDE_PROJECT_DIR` no apunta al repo | `/router:estado` lo diagnostica. Sin `jq` el guard se auto-desactiva (nunca rompe la sesión) |
| El digest no muestra un fallo que sí existe | Los clusters se cortaron por `QA_ROUTER_MAX_CLUSTERS` | La línea "… N clusters más" lo dice. Subir la variable, o filtrar el crudo con `grep` acotado |
| `/router:costo` dice que no hay ledger | Nunca se corrió un extractor, o `QA_ROUTER_LEDGER=off` | Correr un digest primero |
| El subagente devuelve prosa en vez de bullets | Se lo invocó sin su contrato | Los contratos están en `agents/*.md` — invocar por nombre, no reescribir el prompt |

---

## Auto-Clarity

Salir de cualquier modo comprimido para: hallazgos de secretos, explicación de un bloqueo del
hook al usuario, y la confirmación de `/router:instalar` (modifica configuración del proyecto).

## Boundaries

NO decide qué skill usar ni qué probar — eso es `qa-orchestrator-skill`.
NO genera `.feature`/`.spec.ts`/`.jmx`/colecciones — eso es la skill de cada herramienta.
NO instala servidores MCP ni depende de ningún proveedor externo.
NO modifica `.claude/settings.json` sin confirmación explícita del usuario.
NO delega a tier 0/1 nada de la lista "NUNCA baja de tier 2".
NO devuelve un digest parcial: si el parseo falla, sale 3 y lo dice.
NO oculta fallos para ahorrar: los digests listan el 100% de los fallos, agrupados.
"stop qa-router" o `/router:off`: volver a lectura directa sin ruteo.
