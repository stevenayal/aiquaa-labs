# Especificación de las 5 métricas

Fuente de verdad de comandos `az` / `az devops invoke`, campos esperados y mapeo a fixtures de
`examples/`. `SKILL.md` resume esta tabla — este archivo tiene el detalle completo.

Prerrequisitos de entorno (modo real):

```bash
az extension add --name azure-devops
az login
az devops configure --defaults organization=https://dev.azure.com/<org> project=<project>
az devops project show --project <project>   # verificación antes de extraer nada
```

---

## Métrica 1 — % de automatización real (API/Web)

**Qué mide:** casos automatizados vs. manuales, filtrando solo lo que hoy es técnicamente
automatizable (API y Web) — ver `api-web-filter-convention.md`.

**Fuente:** Azure DevOps Test Plans (work items tipo Test Case) + Pull Requests.

```bash
az boards query --wiql "SELECT [System.Id],[System.Title],[System.AreaPath],[System.Tags],\
[System.AssignedTo],[System.CreatedBy],[System.CreatedDate],\
[Microsoft.VSTS.TCM.AutomationStatus],[Microsoft.VSTS.TCM.AutomatedTestName] \
FROM WorkItems WHERE [System.WorkItemType]='Test Case'"

az repos pr list --creator "<email>" --status completed
```

**Cálculo:**
1. Filtrar filas por la convención API/Web activa (Area Path o Tags). Descartar el resto —
   nunca contarlo como "no automatizado".
2. `% automatización real = automatizados (Microsoft.VSTS.TCM.AutomationStatus = 'Automated') /
   total filtrado`, por persona (`System.AssignedTo`) y por equipo.
3. Cruzar contra `az repos pr list` para confirmar que existe un PR real vinculado — un
   `AutomationStatus=Automated` sin PR asociado se reporta como "marcado automatizado, sin PR
   vinculado" (posible dato inconsistente, nunca se cuenta como automatización real).

**Fixture:** `examples/az-boards-query-testcases.json`, `examples/az-repos-pr-list.json`.

---

## Métrica 2 — Evidencia de ejecución

**Qué mide:** que la automatización efectivamente corra en pipeline, no solo exista en el
repositorio.

**Fuente:** Azure Pipelines.

```bash
az pipelines runs list --pipeline-ids <id> --top 50

az devops invoke --area test --resource runs \
  --route-parameters project=<project> \
  --api-version 7.1 --http-method GET

az devops invoke --area test --resource results \
  --route-parameters project=<project> runId=<runId> \
  --api-version 7.1 --http-method GET
```

**Cálculo:** por cada Test Case con `Microsoft.VSTS.TCM.AutomatedTestName` no vacío, buscar ese
`automatedTestName` entre los resultados de Test Runs dentro del lookback configurado (default
30 días, `ADO_EVIDENCE_LOOKBACK_DAYS`). Si no aparece en ningún run → "sin evidencia de
ejecución", independientemente de lo que diga el flag de estado.

**Fixture:** `examples/az-pipelines-runs-list.json`, `examples/az-test-runs-results.json`.

---

## Métrica 3 — Profundidad de validación

**Qué mide:** si el caso valida solo el código de respuesta (ej. `HTTP 200`) o el resultado real
de negocio (ej. estado en base de datos).

**Fuente:** revisión del diff del Pull Request de automatización.

```bash
az devops invoke --area git --resource pullrequestiterationchanges \
  --route-parameters project=<project> repositoryId=<repoId> pullRequestId=<prId> \
  iterationId=<lastIterationId> --api-version 7.1 --http-method GET

az devops invoke --area git --resource items \
  --route-parameters project=<project> repositoryId=<repoId> \
  --api-version 7.1 --http-method GET \
  --in-parameters path=<path> versionDescriptor.version=<branch> versionDescriptor.versionType=branch
```

(No hay subcomando estable de `az repos` para diff/contenido de archivo por iteración de PR —
por eso se usa `az devops invoke` directo contra la Git API.)

**Cálculo:** ver heurística completa en `validation-depth-heuristics.md`. Clasifica cada caso en
Profunda / Superficial / Sin evidencia — nunca se promedia con las otras métricas.

**Fixture:** `examples/az-git-pr-diff-shallow.md`, `examples/az-git-pr-diff-profundo.md`.

---

## Métrica 4 — Estabilidad en el tiempo

**Qué mide:** si la prueba automatizada se mantiene pasando en ejecuciones sucesivas o se vuelve
inestable ("flaky").

**Fuente:** historial de ejecuciones en pipeline (mismas llamadas que la métrica 2, extendidas a
N corridas).

```bash
az devops invoke --area test --resource results \
  --route-parameters project=<project> runId=<runId> \
  --api-version 7.1 --http-method GET
# repetir por cada runId dentro de la ventana configurada
```

**Cálculo:** para cada `automatedTestName`, tomar sus últimas N corridas (default 10, o los
últimos 30 días — lo que dé menos corridas, `ADO_STABILITY_WINDOW`). `flakiness_rate = (#
transiciones pass↔fail) / (N-1)`. Marcar "inestable" si `flakiness_rate ≥ 0.2`
(`ADO_FLAKY_THRESHOLD`) o si las últimas 5 corridas mezclan pass/fail.

**Fixture:** `examples/az-test-runs-results.json` (incluye una serie de corridas con
transiciones).

---

## Métrica 5 — Cantidad de entregas

**Qué mide:** volumen mensual de casos entregados por persona.

**Fuente:** Azure DevOps (reusa el WIQL de la métrica 1).

**Cálculo:** agrupar los Test Case filtrados (API/Web) por `System.CreatedBy` y por mes
(`System.CreatedDate`). Cruzar opcionalmente con:

```bash
az repos pr list --creator "<email>" --status completed --min-time <inicio-periodo>
```

para contexto de PRs de automatización entregados en el mismo período — no reemplaza el conteo
de Test Cases, es un dato de apoyo.

**Fixture:** `examples/az-boards-query-testcases.json`, `examples/az-repos-pr-list.json`.

---

## Mapeo llamada real → fixture (modo ejemplo)

| Llamada | Fixture |
|---|---|
| `az boards query --wiql "..."` (Test Cases) | `examples/az-boards-query-testcases.json` |
| `az repos pr list ...` | `examples/az-repos-pr-list.json` |
| `az pipelines runs list ...` | `examples/az-pipelines-runs-list.json` |
| `az devops invoke --area test --resource runs\|results ...` | `examples/az-test-runs-results.json` |
| `az devops invoke --area git --resource pullrequestiterationchanges\|items ...` (diff superficial) | `examples/az-git-pr-diff-shallow.md` |
| `az devops invoke --area git --resource pullrequestiterationchanges\|items ...` (diff profundo) | `examples/az-git-pr-diff-profundo.md` |

Salida esperada al correr todo el pipeline en modo ejemplo: `examples/INFORME_PRODUCTIVIDAD_EJEMPLO.md`.
