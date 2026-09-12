# Guía de uso — playwright-ai-agents-skill

## Instalación

```bash
npx skills add aiquaa-labs/playwright-ai-agents-skill
npx skills add aiquaa-labs/playwright-skill      # genera specs, config, auth, CI
npx skills add aiquaa-labs/course-pr-skill       # entrega por PR de lo generado/reparado
```

Requisitos locales: Node ≥18 y un proyecto Playwright con reporter JSON:

```typescript
// playwright.config.ts
reporter: [
  ['list'],
  ['json',  { outputFile: 'results/playwright-results.json' }],
  ['junit', { outputFile: 'results/playwright-junit.xml' }],
],
use: {
  trace: 'on-first-retry',
  screenshot: 'only-on-failure',
  video: 'retain-on-failure',
},
```

Copiar el classifier y el presupuesto al proyecto:

```bash
cp playwright-ai-agents-skill/scripts/classify-failures.mjs scripts/
cp playwright-ai-agents-skill/examples/.env.ai.example .env.ai
```

---

## Recorrido completo — HU "Transferencia entre cuentas propias"

### 1. Planificar

```
/pw-ia:plan HU-231: como cliente retail quiero transferir entre mis cuentas propias…
```

La skill pregunta nivel de generación (A/B/C/D), seed y Page Objects existentes, confirma y
escribe `specs/transferencias/PLAN_TRANSFERENCIAS.md`. Sin código, sin abrir el navegador si
la historia alcanza. Revisar escenarios, riesgos y contrato `data-testid` con el equipo antes
de seguir.

### 2. Generar

```
/pw-ia:generate specs/transferencias/PLAN_TRANSFERENCIAS.md TRF-01 TRF-02
```

La skill lee el flujo de `playwright-skill`, carga **solo** el plan, `pages/TransfersPage.ts`,
fixtures y tipos, y genera `tests/transferencias/T_TRANSFERENCIA_EXITOSA.spec.ts`. Validar:

```bash
npx tsc --noEmit
npx playwright test --list
npx playwright test tests/transferencias --project chromium
```

Desde acá, el test corre en CI sin IA para siempre.

### 3. Algo falla en CI → clasificar

Descargar `results/playwright-results.json` del artefacto (o `CLASIF_*.json` si el pipeline ya
lo generó) y:

```
/pw-ia:classify
```

```text
tests=10 failed=8 flaky=1 healer=1
TEST_BUG    high   HEAL  …T_TRANSFERENCIA_EXITOSA.spec.ts › transferencia exitosa [chromium]
PRODUCT_BUG medium HUMAN …T_TRANSFERENCIA_EXITOSA.spec.ts › saldo origen se descuenta [chromium]
PRODUCT_BUG medium HUMAN …T_TRANSFERENCIAS_API.spec.ts › POST /api/transfers retorna 201 [api]
NETWORK     high   HUMAN …T_TRANSFERENCIAS_API.spec.ts › GET /api/accounts responde [api]
```

- `HUMAN` + `PRODUCT_BUG` → bug tracker, con el error y el trace del retry.
- `HUMAN` + `ENVIRONMENT`/`NETWORK` → retry o infra.
- `HEAL` → paso 4.

### 4. Reparar con presupuesto

```
/pw-ia:heal
```

Para cada candidato: arma el prompt `[STATIC]`+`[DYNAMIC]`, pide un diff mínimo, lo pasa por el
chequeo mecánico (no toca `expect` de valor, no sale de `tests/ pages/ fixtures/`), da el
comando de verificación y escribe `results/heal/HEAL_TRF_01.md`. Si en 2 intentos no hay fix
válido → `HUMAN_REVIEW_REQUIRED`.

```bash
npx playwright test tests/transferencias/T_TRANSFERENCIA_EXITOSA.spec.ts -g "TRF-01" --project chromium
```

### 5. Entregar

```
/curso:entregar
```

`course-pr-skill` abre el PR con el diff y `HEAL_*.md` como evidencia. Revisión humana
obligatoria.

---

## Pipeline sin IA

```
/pw-ia:pipeline
```

Genera `Y_<NOMBRE>_playwright_ai.yml` desde `examples/Y_EXAMPLE_playwright_ai.yml`:

1. **Test Impact Analysis** — en PR, `git diff` contra la rama destino → tags afectados
   (`src/payments/*` → `@pagos|@ledger|@cuentas`) + `@smoke`. En `main`/nightly → suite
   completa. Cambio de `package.json`/`playwright.config.ts` → suite completa.
2. `npx playwright test --grep "<tags>"` con `continueOnError`.
3. `classify-failures.mjs` con `condition: always()` → `CLASIF_*.json` en artefactos.
4. JUnit a Azure Test Plans.

Mantener el mapa ruta→tag del step 1 sincronizado con los tags de los `T_*.spec.ts`.

---

## Presupuesto

```
/pw-ia:budget
```

| Variable | Default | Qué limita |
|---|---|---|
| `AI_MAX_HEAL_ATTEMPTS` | 2 | intentos del Healer por test (incluye escalamientos de tier) |
| `AI_MAX_CALLS` | 3 | llamadas al modelo por test |
| `AI_MAX_TOKENS` | 40000 | tokens in+out por test |
| `AI_BUDGET_PER_TEST` | — | moneda del proveedor, definir con tarifa real |
| `AI_DEFAULT_TIER` | economico | tier inicial |

Ajustar con datos reales — ver `references/metrics.md`.

---

## Extender el classifier

Si un mensaje recurrente cae en `UNKNOWN` (wrappers propios, `expect(x, 'mensaje custom')`):

1. Agregar la regla en `RULES` de `scripts/classify-failures.mjs`, en la posición de prioridad
   correcta, con `id`, `category`, `confidence`, `pattern`.
2. Agregar la fila en `references/failure-taxonomy.md` con el mismo `id` y orden.
3. Agregar un caso en `examples/playwright-results.sample.json` y regenerar
   `examples/CLASIF_EJEMPLO.json`.

`confidence: 'high'` en una regla `TEST_BUG` habilita Healer automático — justificarlo en
"Decisiones de diseño" de la taxonomía.

---

## Preguntas frecuentes

**¿Puedo usar Playwright MCP?** Sí, para exploración autónoma de UI desconocida o healing
complejo. No como forma estándar de generar cientos de tests ni nunca para ejecutar.

**¿Y los Test Agents oficiales de Playwright (planner/generator/healer)?** Compatibles: esta
skill aporta lo que no traen por defecto — classifier determinístico previo, presupuesto,
blacklist de reglas de negocio y entrega por PR. Guardar sus planes con prefijo `PLAN_` en
`specs/`.

**¿El Healer puede ajustar un monto que cambió por una nueva regla?** No. Cambios de reglas de
negocio los hace QA a mano, con la historia que lo justifica.

**¿Qué pasa con los tests flaky?** Van a `flaky[]` en `CLASIF_*.json`. Un humano revisa el
trace del retry; el Healer no los toca.
