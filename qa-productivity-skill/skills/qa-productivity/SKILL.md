---
name: qa-productivity
description: >
  Extrae de Azure DevOps (Test Plans, Pipelines, Pull Requests) el estado real
  de automatización del equipo de QA — no solo cantidad de casos entregados,
  sino calidad verificable: % de automatización real filtrado a API/Web,
  evidencia de que la automatización corre en pipeline, profundidad de
  validación (HTTP 200 vs. resultado real de negocio), estabilidad en el
  tiempo (flakiness) y volumen mensual por persona. Produce un informe
  auditable por persona/equipo. Nunca infla ni infiere: si un dato no está
  disponible en Azure DevOps, se reporta como "sin evidencia", no se estima.
  Usar cuando el usuario mencione "productividad de QA", "métricas de
  automatización", "medir adopción de IA en QA", "informe de Azure DevOps",
  "cuántos casos automatizó cada persona", "automatización real vs. inflada",
  "evidencia de ejecución en pipeline", "tests inestables/flaky", o pida un
  scorecard de calidad de automatización para una reunión de liderazgo.
  Auto-activa para cualquier extracción o consolidación de métricas de
  productividad QA desde Azure DevOps, en modo real (`az login`) o en modo
  ejemplo (fixtures de `examples/`, sin credenciales).
---

QA productivity scorecard from Azure DevOps. Claude shells `az`, filters API/Web only, scores 5 metrics, emits auditable report. Never guesses a filter convention or fills a gap. Terse output. No fluff.

---

## ¿Qué es esta skill?

El equipo de QA mide hoy solo **cantidad** de casos automatizados entregados. Eso permite que
alguien entregue automatizaciones de baja calidad (ej. solo valida `HTTP 200`, sin verificar el
resultado real de negocio) para cumplir la meta, sin impacto real en cobertura. Esta skill saca
de Azure DevOps las 5 señales que sí distinguen automatización real de "teatro de cantidad", y
las consolida en un informe por persona/equipo, auditable.

**No reemplaza a `qa-orchestrator-skill`** — esa decide qué skill usar para un PR concreto; esta
mira hacia atrás, sobre un período, y responde "¿qué tan real es la automatización que ya se
entregó?". No genera ni corre tests — solo lee estado ya existente en Azure DevOps.

No cubre: automatización de objetos de base de datos Oracle ni de escritorio (hoy no hay forma
madura de automatizarlos, así que quedan explícitamente fuera del denominador de "% real" — ver
§ Filtro API/Web) ni la arquitectura de ejecución/orquestación propia del equipo (portal, tareas
programadas, gateway) — esa es un tema separado, fuera del alcance de este informe.

---

## Comandos

| Comando | Acción |
|---------|--------|
| `/productividad:configurar` | Intake: org, proyecto, convención de filtro API/Web, período. Escribe `.env` de referencia (nunca commitea secretos). |
| `/productividad:extraer` | Corre (o lee fixtures en modo ejemplo) los `az`/`az devops invoke` de las 5 métricas. Guarda el JSON crudo por métrica. |
| `/productividad:auditar-profundidad` | Aplica la heurística superficial-vs-profunda (métrica 3) sobre los PRs de automatización del período. |
| `/productividad:consolidar` | Agrega las 5 métricas por persona/equipo en `INFORME_PRODUCTIVIDAD_*.md`. |
| `/productividad:completo` | Flujo completo `configurar → extraer → auditar-profundidad → consolidar`. |

---

## Context Intake — SIEMPRE ejecutar primero (`/productividad:configurar`)

1. **¿Org y proyecto de Azure DevOps?** (`--org https://dev.azure.com/<org> --project
   <project>`). Si no se dan, preguntar — nunca asumir un org por defecto.
2. **¿Modo real o modo ejemplo?**
   - Real: requiere `az extension add --name azure-devops`, `az login`,
     `az devops configure --defaults organization=<org> project=<project>`. Verificar con
     `az devops project show --project <project>` antes de seguir.
   - Ejemplo: sin credenciales. Cada llamada `az .../az devops invoke` de este documento se
     reemplaza por leer el fixture JSON equivalente en `../../examples/` (mapeo 1 a 1, ver
     tabla en `references/metrics-spec.md`). Se usa para validar la skill sin org real, o
     cuando el usuario dice explícitamente "usá los fixtures"/"modo ejemplo".
3. **¿Convención de filtro API/Web del org?** Preguntar cuál usan — Area Path o Tags — nunca
   asumir. Detalle completo en `references/api-web-filter-convention.md`. Sin esta respuesta no
   se puede calcular la métrica 1 ni la 5 correctamente (todo lo no clasificado queda fuera del
   denominador, no se adivina a qué capa pertenece).
4. **¿Período del informe?** (ej. "último mes", "Q3 2026"). Default: mes calendario anterior si
   no se especifica, y se deja explícito en el header del informe.
5. **Nunca extraer nada** hasta tener org+proyecto, modo, convención de filtro y período.

---

## Las 5 métricas — fuente y comando `az`

Tabla completa de comandos, campos esperados y mapeo a fixtures en
`references/metrics-spec.md`. Resumen:

| # | Métrica | Qué mide | Fuente | Comando base |
|---|---------|----------|--------|---------------|
| 1 | % automatización real (API/Web) | Casos automatizados vs. manuales, solo API/Web | Test Plans + PRs | `az boards query --wiql "..."` + `az repos pr list --status completed` |
| 2 | Evidencia de ejecución | Que la automatización corra en pipeline, no solo exista en el repo | Azure Pipelines | `az pipelines runs list` + `az devops invoke --area test --resource runs\|results` |
| 3 | Profundidad de validación | Si valida solo código HTTP o el resultado real de negocio | PR / diff | `az devops invoke --area git --resource pullrequestiterationchanges\|items` + heurística de archivo |
| 4 | Estabilidad en el tiempo | Si el test se mantiene pasando o se vuelve flaky | Historial de pipeline | Mismos calls que métrica 2, extendidos a N corridas |
| 5 | Cantidad de entregas | Volumen mensual por persona | Test Plans / PRs | Reusa el WIQL de la métrica 1, agrupado por `System.CreatedBy` + mes |

Regla dura heredada del diagnóstico del negocio: **un caso que solo valida `HTTP 200` sin
verificar el resultado real de negocio no cuenta como automatización de calidad**, aunque Azure
DevOps lo marque como "caso automatizado". La métrica 3 es la que aplica esta regla — nunca se
promedia con las demás, se reporta aparte (ver § Regla de agregación).

---

## Filtro API/Web — explícito, nunca asumido

Detalle completo en `references/api-web-filter-convention.md`. Dos convenciones posibles,
configurables por variable de entorno, preguntadas en el intake:

- **Area Path:** `ADO_AREA_API` / `ADO_AREA_WEB` (ej. `<Proyecto>\QA\API`, `<Proyecto>\QA\Web`).
- **Tags:** `ADO_TAG_API` / `ADO_TAG_WEB` (ej. `capa:api`, `capa:web`).

Todo Test Case que no matchea ninguna de las dos (objetos Oracle, desktop, u otra categoría)
**queda excluido del denominador de la métrica 1 y 5** — nunca se cuenta como "no automatizado"
ni se le asigna una capa por inferencia. Esto es lo que evita que la deuda técnica de BD/desktop
distorsione el % real, tal como exige el diagnóstico del negocio.

---

## Profundidad de validación (métrica 3) — heurística de archivo, no solver genérico

Detalle completo con ejemplos en `references/validation-depth-heuristics.md`. Ubica el archivo
de test desde el diff del PR de automatización por el prefijo de nombre que ya usa el stack
`aiquaa-labs` (mismo espíritu determinístico que `qa-orchestrator-skill/references/signal-mapping.md`):

| Archivo (por prefijo del stack) | Señal superficial | Señal profunda |
|---|---|---|
| `H_*.hurl` (hurl-skill) | `HTTP 200` sin `[Asserts]`, o assert solo de status | `jsonpath` sobre body, o `sql/select` pareado |
| `T_*.spec.ts` (playwright-skill) | solo `expect(response.status())...` | también body o verificación en BD |
| `F_*.feature` / `S_*.steps.ts` (bdd-skill) | solo step "el código de respuesta debería ser…" | step adicional "…en la base de datos" |
| `C_*.json` / `E_*.json` (postman-newman-skill) | solo `pm.response.to.have.status(...)` | también `pm.expect(jsonData...)` |

Cada caso auditado clasifica en una de tres categorías, **nunca se promedian entre sí**:

- **Profunda** — cuenta como automatización de calidad.
- **Superficial** — cuenta como "automatizado" a efectos de la métrica 1, pero se reporta
  aparte como no-calidad en el informe (esto es lo que expone la inflación de números).
  **No cuenta** como calidad.
- **Sin evidencia** — el archivo de test no se pudo localizar desde el diff del PR. Se reporta
  explícitamente como dato faltante — nunca se asume ni "Profunda" ni "Superficial" por
  omisión.

---

## Regla de agregación — nunca promediar calidad con cantidad

El informe consolidado (`/productividad:consolidar`) sigue un **patrón de gate, no de
promedio**, igual que `qa-orchestrator-skill` con su veredicto global:

- La métrica 5 (cantidad) se reporta **siempre por separado** de las métricas 1-4 (calidad) —
  nunca se combinan en un solo número. Cantidad alta con calidad baja debe ser visible como tal,
  no diluirse en un promedio que la esconda.
- Dentro de calidad: un caso "automatizado" que resulta **Superficial** en la métrica 3, o **sin
  evidencia de ejecución** en la métrica 2, o **inestable** en la métrica 4, no sube el % de
  "automatización de calidad" de esa persona — solo un caso Profundo + con evidencia + estable
  cuenta ahí. El % de automatización real (métrica 1) y el % de automatización de *calidad* son
  dos números distintos en el informe, no uno solo.

---

## Modo ejemplo — fixtures

Sin `az login`/org real disponible, cada llamada de este documento tiene un fixture equivalente
en `examples/` (mapeo completo en `references/metrics-spec.md`):

| Llamada real | Fixture |
|---|---|
| `az boards query --wiql "..."` (Test Cases) | `examples/az-boards-query-testcases.json` |
| `az repos pr list ...` | `examples/az-repos-pr-list.json` |
| `az pipelines runs list ...` | `examples/az-pipelines-runs-list.json` |
| `az devops invoke --area test --resource runs\|results ...` | `examples/az-test-runs-results.json` |
| Diff de PR con validación superficial | `examples/az-git-pr-diff-shallow.md` |
| Diff de PR con validación profunda | `examples/az-git-pr-diff-profundo.md` |

Correr `/productividad:completo` en modo ejemplo debe reproducir
`examples/INFORME_PRODUCTIVIDAD_EJEMPLO.md` — es la forma de validar la skill sin credenciales
reales (mismo principio que los servicios simulados de `database-object-testing-skill`).

---

## Informe — `INFORME_PRODUCTIVIDAD_<EQUIPO-o-PERSONA>_<PERIODO>.md`

Schema completo en `references/productivity-report-schema.md`. Estructura: header (org,
proyecto, convención de filtro usada, período, timestamp, modo real/ejemplo) → tabla resumen
por persona (métricas 1-5 separadas, nunca promediadas) → detalle por persona (casos Profunda/
Superficial/Sin evidencia con enlace al PR) → rollup de equipo → "Advertencias / datos
incompletos" (nunca rellena huecos en silencio) → metodología (enlaza a los references usados).

---

## Diagramas de contexto

Esta skill también trae, en `references/`, los dos diagramas de flujo usados para comunicar el
objetivo de negocio detrás de estas métricas en la reunión con líderes:

- `references/diagrama-adopcion-ia-qa.md` — flujo de adopción de IA en QA (estado actual →
  objetivo), atado al driver de negocio.
- `references/diagrama-sdd-qa-integrado.md` — flujo SDD con QA integrado (6 etapas), mostrando
  dónde se miden/exigen estas 5 métricas.

No son artefactos que la skill regenere en cada corrida — son contexto de negocio versionado,
consultar directamente cuando se necesite explicar el "por qué" del informe.

---

## Gates human-in-the-loop

1. **Convención de filtro API/Web no confirmada** — no se calcula la métrica 1 ni la 5 sin
   esto. Preguntar, nunca asumir.
2. **Modo real sin `az login` verificado** — `/productividad:extraer` verifica
   `az devops project show` antes de correr cualquier otro comando; si falla, ofrecer modo
   ejemplo en vez de fallar en silencio a mitad de la extracción.
3. **Dato faltante en cualquier métrica** — se reporta como "sin evidencia" en el informe, nunca
   se estima ni se interpola.
4. Esta skill **nunca** abre PR, comenta en Azure Boards, ni modifica ningún work item — es de
   solo lectura, siempre.

---

## Fallos comunes y fixes

| Síntoma | Causa | Fix |
|---------|-------|-----|
| % automatización da distinto a lo que reporta Azure DevOps "a ojo" | Azure DevOps cuenta todo lo marcado `Automated`, esta skill excluye lo no-API/Web del denominador | Correcto por diseño — ver § Filtro API/Web. Documentarlo así en el informe, no "corregirlo" para que coincida. |
| Métrica 3 no encuentra el archivo de test | El PR no sigue los prefijos del stack `aiquaa-labs` (`H_`/`T_`/`F_`/`C_`), o el archivo está en otra ruta | Reportar "sin evidencia", nunca adivinar el archivo por similitud de nombre |
| `az devops invoke` devuelve 404 en `test/runs` | El proyecto no tiene Test Plans habilitado, o el pipeline no publica resultados vía `PublishTestResults@2` | Reportar la métrica 2 como "sin evidencia" para ese pipeline, no fallar todo el informe |
| Dos personas con el mismo email en Boards y Repos no matchean | `System.CreatedBy`/`System.AssignedTo` vs. `creator` de PR usan formatos distintos (display name vs. email) | Normalizar por email en el intake; si no hay match exacto, reportarlo como "sin vincular" en vez de fusionar por nombre similar |

---

## Auto-Clarity

Salir de caveman para: cualquier hallazgo de "automatización inflada" (Superficial/sin
evidencia) por persona — eso se explica en claro, con el dato objetivo, nunca como acusación
directa (ver enfoque del documento de estrategia: exigencia con acompañamiento, no ataque). El
resumen ejecutivo del informe también se explica en claro. Retomar caveman después.

## Boundaries

Solo lee de Azure DevOps — nunca escribe, comenta, ni modifica work items, PRs ni pipelines.
NO calcula la métrica 1/5 sin convención de filtro API/Web confirmada por el usuario.
NO promedia cantidad con calidad, ni Superficial/sin-evidencia con Profunda — ver § Regla de
agregación.
NO adivina a qué persona pertenece un caso ni fusiona identidades por nombre similar sin
confirmación.
NO genera ni corre automatización — eso es siempre de las otras skills del stack
(`hurl-skill`, `playwright-skill`, `bdd-skill`, `postman-newman-skill`).
NO presenta ni referencia la arquitectura de ejecución/orquestación propia del equipo — fuera
de alcance de este informe.
"stop qa-productivity" o "normal mode": volver a estilo verbose.
