# Política de ruteo — tabla completa

Referencia normativa del `qa-router`. El `SKILL.md` trae la versión condensada.

## Tier 0 — extractor determinístico (0 tokens de LLM)

Se dispara por **nombre de archivo** o, para JSON, por sus claves de primer nivel. El tamaño
no entra en la decisión: si hay extractor, se usa siempre — leer 200 líneas crudas de un
`.jtl` tampoco tiene sentido cuando el digest da la respuesta completa.

| Matcher | Extractor | Detección |
|---|---|---|
| `*.jtl`, `*jtl*.csv` | `jtl_digest.py` | nombre |
| `*.jmx` | `jmx_digest.py` | nombre |
| `*.xml` con raíz `<testsuites>`/`<testsuite>` | `junit_digest.py` | nombre + raíz |
| `*.xml` con raíz `<test-run>` o con `<test-case>` | `junit_digest.py` (modo NUnit) | nombre + raíz |
| `*postman_collection.json`, o JSON con `{info, item}` | `collection_digest.py` | nombre o claves |
| JSON con `{run, collection}` | `newman_digest.py` | claves |
| JSON con `suites` + (`config` o `stats`) | `pw_digest.py` | claves |
| JSON con `paths` + (`openapi` o `swagger`) | `openapi_digest.py` | claves |
| JSON con `pullRequests`/`resultsByTest`/`value`/`runs`/`workItems` | `az_digest.py` | claves |
| rango git, `*.diff`, `*.patch` | `diff_digest.sh` | invocación explícita |

`.har` está reconocido por el guard (se bloquea la lectura cruda) pero **todavía no tiene
extractor** — el dispatcher sale 3 y manda a tier 1. Es la primera extensión pendiente.

## Tier 1 — subagente con contexto aislado (`model: haiku`)

| Situación | Agente | Por qué no es tier 0 |
|---|---|---|
| Archivo de texto > `QA_ROUTER_MIN_LINES` (400) sin extractor | `qa-bulk-reader` | Requiere comprensión, no parseo |
| Suite `.feature`/steps/page objects heredada | `qa-bulk-reader` | ídem |
| > 3 búsquedas independientes sobre el repo | `qa-bulk-reader` | El costo está en la acumulación, no en un archivo |
| Log de CI, stdout de pipeline, stack traces | `qa-log-triage` | Texto libre sin esquema |
| Boilerplate desde patrón existente | `qa-code-writer` | Generación, no lectura |
| Diff grande sin `diff_digest.sh` disponible | `qa-diff-scout` | Fallback del extractor |

Precondición de `qa-code-writer`: `--reference <archivo>` **obligatorio**. Sin patrón de
referencia el agente devuelve `FALTA REFERENCIA` y no escribe nada. Es la regla que evita
que un modelo barato invente convenciones.

## Tier 2 — sesión principal

Todo lo que no cae arriba, más la lista de exclusión dura:

1. Ediciones quirúrgicas con número de línea.
2. Semántica de asserts, valores esperados, nombres de campos y tablas, credenciales.
3. Diagnóstico de causa raíz.
4. Ruteo ambiguo de `qa-orchestrator`, veredicto del informe consolidado.
5. Gates human-in-the-loop.
6. Qué hacer ante un secreto detectado (el *match* es tier 0; la decisión es tier 2).

## Umbrales

| Variable | Default | Para qué |
|---|---|---|
| `QA_ROUTER_MIN_LINES` | 400 | Umbral de líneas para tier 1. Los `SKILL.md` del stack rondan 200–300 líneas y deben seguir siendo lectura directa |
| `QA_ROUTER_MAX_CLUSTERS` | 12 | Variedad de clusters impresos. No recorta el conteo total de fallos |
| `QA_ROUTER_MAX_ROWS` | 15 | Filas en listados largos (`--all`, payloads de `az`) |
| `QA_ROUTER_LEDGER` | `.qa-router/ledger.jsonl` | Ruta del ledger; `off` lo desactiva |
| `QA_ROUTER_OFF` | `0` | `1` desactiva el guard por completo |
| `QA_ROUTER_HOME` | `$CLAUDE_PROJECT_DIR/qa-router-skill` | Dónde vive la skill, si se instaló en otra ruta |

Si `p50 de latencia del subagente > tiempo ahorrado`, subir `QA_ROUTER_MIN_LINES` a 600 antes
de desactivar el router. Tier 0 no tiene este problema: es más rápido que leer el archivo.
