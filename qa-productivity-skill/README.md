# qa-productivity-skill

Scorecard de productividad y calidad real de automatización QA, extraído de **Azure DevOps**
(Test Plans, Pipelines, Pull Requests) vía Azure CLI. No mide solo cantidad de casos entregados
— mide si esa automatización es real: filtrada a lo que hoy es técnicamente automatizable (API y
Web), con evidencia de que corre en pipeline, con validación de resultado de negocio (no solo
código HTTP), y estable en el tiempo. Produce un informe auditable por persona/equipo, y trae
los dos diagramas de flujo (adopción de IA en QA, SDD con QA integrado) usados para explicar por
qué esto importa en una reunión de liderazgo.

## Instalación

```bash
npx skills add aiquaa-labs/qa-productivity-skill
```

Requiere `az` CLI con la extensión `azure-devops`:

```bash
az extension add --name azure-devops
az login
az devops configure --defaults organization=https://dev.azure.com/<org> project=<project>
```

Sin credenciales reales, la skill corre igual en **modo ejemplo** contra los fixtures de
`examples/` — ver [Guía de uso](./docs/uso.md).

## Por qué existe

El equipo de QA mide hoy solo cantidad de casos automatizados entregados. Eso permite que
automatizaciones de baja calidad (por ejemplo, un caso que solo valida `HTTP 200` sin verificar
el resultado real de negocio) cuenten igual que una automatización real, inflando el número sin
impacto en cobertura. Esta skill saca de Azure DevOps las 5 señales — automatización real
API/Web, evidencia de ejecución, profundidad de validación, estabilidad y cantidad — y las
reporta por separado, nunca promediadas, para que la brecha entre "cantidad" y "calidad" quede
visible por persona y por equipo.

## Comandos

| Comando | Acción |
|---------|--------|
| `/productividad:configurar` | Intake: org, proyecto, convención de filtro API/Web, período |
| `/productividad:extraer` | Corre (o lee fixtures) los `az`/`az devops invoke` de las 5 métricas |
| `/productividad:auditar-profundidad` | Aplica la heurística superficial-vs-profunda sobre los PRs del período |
| `/productividad:consolidar` | Agrega las 5 métricas por persona/equipo en el informe final |
| `/productividad:completo` | Flujo completo `configurar → extraer → auditar-profundidad → consolidar` |

## Contenido

- `skills/qa-productivity/SKILL.md` — el flujo completo
- `references/metrics-spec.md` — comandos `az`/`az devops invoke` y fórmulas por métrica
- `references/api-web-filter-convention.md` — convención de filtro (Area Path o Tags)
- `references/validation-depth-heuristics.md` — heurística de profundidad de validación
- `references/productivity-report-schema.md` — schema del informe
- `references/diagrama-adopcion-ia-qa.md` — Diagrama 1 (mermaid) + por qué importa al negocio
- `references/diagrama-sdd-qa-integrado.md` — Diagrama 2 (mermaid) + por qué importa al negocio
- Versión interactiva de ambos diagramas (Artifact, para la reunión de liderazgo):
  https://claude.ai/code/artifact/787993ed-b273-46b5-8f72-5a3c39df8365
- `examples/` — fixtures JSON simulados de Azure DevOps + diffs worked + informe de ejemplo

## Salidas

`INFORME_PRODUCTIVIDAD_<EQUIPO-o-PERSONA>_<PERIODO>.md`

→ [Guía de uso](./docs/uso.md)

## Licencia

MIT
