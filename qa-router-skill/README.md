# qa-router-skill

> Skill para agentes de IA — powered by [aiquaa](https://aiquaa.com/)

**Router de consumo del stack QA.** Decide en qué nivel de costo se ejecuta cada operación y
digiere los artefactos pesados de testing antes de que entren al contexto del modelo. Sin
proveedores externos y sin servidores MCP: solo Python stdlib, bash y subagentes nativos.

Implementa el patrón *shunt* relevado en [`docs/router-qa-relevamiento.md`](../docs/router-qa-relevamiento.md).

---

## El problema

Las otras skills del stack generan y corren suites. Sus **resultados** son el mayor consumidor
de contexto: un `.jtl` de una corrida de carga pesa cientos de MB, un JSON de Newman varios MB,
un reporte de Playwright otro tanto. Leerlos crudos es imposible o carísimo — y el 99% de ese
volumen no aporta nada a la decisión que hay que tomar.

```
$ python3 extractors/jtl_digest.py results/R_CARGA.jtl --baseline results/R_BASELINE.jtl

JMETER · R_CARGA.jtl · 2026-09-07T17:53Z
MUESTRAS: 600 · errores 20 (3.33%) · duración 60s · throughput 10.0/s
LATENCIA (ms): p50 172 · p90 731 · p95 835 · p99 974 · max 1229
TOP 4 SAMPLERS POR p95:
  POST /api/v1/sql/select · n=150 · p95 967ms · p99 1117ms · max 1229ms
  POST /api/v1/payments · n=150 · p95 590ms · p99 667ms · max 677ms
ERRORES (20 en 2 clusters):
  POST /api/v1/payments · 500 · ×16 · Test failed: code expected to equal 200
  POST /api/v1/sql/select · 500 · ×4 · Test failed: code expected to equal 200
VS BASELINE (R_BASELINE.jtl): p95 +167ms · errores 0.00% → 3.33%
CRUDO: results/R_CARGA.jtl (59.2 KB)
```

59,2 KB → 766 B (**98,7%** menos) sin perder un solo dato accionable. En un `.jtl` real de
200 MB el digest sigue pesando lo mismo.

---

## Los tres tiers

| Tier | Quién ejecuta | Para qué | Costo |
|---|---|---|---|
| **0** | Extractor determinístico (Python stdlib / bash) | Artefactos parseables: `.jtl`, Newman, JUnit/NUnit, Playwright, `.jmx`, colecciones, OpenAPI, Azure DevOps, diffs | 0 tokens de LLM |
| **1** | Subagente `haiku` con contexto aislado | Texto que necesita comprensión: suites heredadas, logs de CI, boilerplate | Bajo — el archivo no entra al contexto principal |
| **2** | Sesión principal | Decidir, diagnosticar, editar con precisión | El que ya se paga |

La adaptación clave respecto del patrón original: en QA los artefactos pesados son
**máquina-parseables**, así que el worker barato casi siempre es un script — mejor ratio que un
modelo barato, costo cero, y salida reproducible y auditable.

---

## Instalación

```bash
npx skills add aiquaa-labs/qa-router-skill
npx skills add aiquaa-labs/qa-router-skill -a cursor
npx skills add aiquaa-labs/qa-router-skill -a windsurf
```

Requisitos: `python3` (stdlib solamente, sin `pip install`) y `jq` para el hook. Sin `jq` los
extractores funcionan igual; solo se pierde el bloqueo automático.

Para activar el enforcement: `/router:instalar` — pide confirmación, hace merge idempotente en
`.claude/settings.json` y preserva los hooks que ya haya.

---

## Comandos

| Comando | Acción |
|---------|--------|
| `/router:digest <archivo>` | Detecta el tipo y corre su extractor. El comando de todos los días |
| `/router:instalar` | Instala el hook `PreToolUse` (con confirmación) |
| `/router:estado` | Umbral, hook, extractores disponibles |
| `/router:leer <glob>` | Delega a `qa-bulk-reader` (tier 1) |
| `/router:escribir <spec> --reference <archivo>` | Delega a `qa-code-writer` (tier 1) |
| `/router:costo` | Ahorro acumulado desde el ledger |
| `/router:off` \| `/router:on` | Escape hatch |

---

## Extractores

| Extractor | Entrada | Devuelve |
|---|---|---|
| `router_digest.py` | cualquiera | Dispatcher — detecta y delega (`--list`) |
| `jtl_digest.py` | `.jtl` de JMeter | Percentiles, error%, throughput, top samplers, clusters. `--baseline` compara |
| `newman_digest.py` | JSON de Newman | Totales + 100% de los fallos agrupados |
| `junit_digest.py` | JUnit / NUnit3 XML | Totales + fallos con mensaje y stack |
| `pw_digest.py` | reporte JSON de Playwright | Fallos con `archivo:línea`, retries, flaky |
| `jmx_digest.py` | `.jmx` | Thread groups, samplers, assertions, variables |
| `collection_digest.py` | colección Postman v2.1 | Árbol + tests por request + requests sin tests |
| `openapi_digest.py` | OpenAPI JSON | Endpoints filtrables por `--tag`/`--grep` |
| `az_digest.py` | JSON de Azure DevOps | Solo los campos de `metrics-spec.md` |
| `diff_digest.sh` | rango git o `.diff` | Rutas, +/-, extensiones, hunks. Sin cuerpos |
| `ledger_report.py` | ledger | Ahorro acumulado por tipo |

Salidas: `0` OK · `2` uso incorrecto · `3` formato no reconocido → delegar a tier 1.
Un extractor nunca devuelve un digest parcial.

---

## El hook

```
BLOQUEADO por qa-router: 'results/R_CARGA.jtl' (204 MB) es un artefacto QA con extractor tier 0.
Corré en su lugar:  python3 .../extractors/router_digest.py "results/R_CARGA.jtl"
Devuelve el contenido accionable — el 100% de los fallos cuando los hay — en ~50 líneas.
Si el extractor falla (exit 3), delegá al subagente qa-bulk-reader.
Bypass puntual: QA_ROUTER_OFF=1
```

Una regla escrita en un `SKILL.md` es una sugerencia y se erosiona en sesiones largas; un
bloqueo no. El guard **permite** siempre `Read` con `offset`/`limit`, `grep`/`wc` acotados y la
ejecución de los propios extractores, y se auto-desactiva si falta `jq` — nunca rompe una
sesión. El escape hatch (`QA_ROUTER_OFF=1`, `QA_ROUTER_MIN_LINES`) está siempre disponible.

---

## Integración con el stack

| Skill | Qué le aporta el router |
|---|---|
| `jmeter-skill` | `.jtl` nunca se carga crudo — el peor ofensor del stack |
| `postman-newman-skill` | `/postman:fix` parte del digest, no del JSON |
| `playwright-skill` | Triage de fallos con `archivo:línea` y conteo de flaky |
| `flaui-skill` / `hurl-skill` | `TestResult.xml` / reporte JUnit vía `junit_digest.py` |
| `qa-orchestrator-skill` | Intake de `/qa:analizar` sin cargar el diff al contexto caro |
| `qa-productivity-skill` | Payloads de `az` proyectados a los campos de `metrics-spec.md` |
| `sandbox-skill` | OpenAPI filtrado por grupo |

`qa-orchestrator` decide **qué** probar · `qa-router` **quién ejecuta y a qué costo** ·
`caveman` **cómo se ve la salida** · `token-optimization` los **hábitos**. No se pisan.

---

## Cuánto ahorra, de verdad

En artefactos, **95–99%** — es aritmética de parseo, no una estimación. En una sesión QA
completa, **40–70%**: el razonamiento, los gates y la generación siguen en tier 2 y no
desaparecen. El ledger reporta tokens estimados (`bytes ÷ 4`), nunca una medición del
tokenizer, y lo dice en su propia salida.

---

## Tests

```bash
bash test/test_extractors.sh   # 24 asserts, sin dependencias
```

Corre contra fixtures propios y contra artefactos reales de `jmeter-skill`,
`postman-newman-skill`, `flaui-skill` y `qa-productivity-skill`.

---

## Licencia

MIT — ver [LICENSE](../postman-newman-skill/LICENSE).
