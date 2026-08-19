# Guía de uso — qa-orchestrator-skill

## Instalación

```bash
npx skills add aiquaa-labs/qa-orchestrator-skill
```

Para agentes específicos:

```bash
npx skills add aiquaa-labs/qa-orchestrator-skill -a cursor
npx skills add aiquaa-labs/qa-orchestrator-skill -a windsurf
npx skills add aiquaa-labs/qa-orchestrator-skill -a cline
```

## Requisitos

- Al menos una de las 10 skills del stack instalada como carpeta hermana (`<name>-skill/`) en
  el mismo repo — el orquestador lee su `SKILL.md` para invocarla, no la reimplementa.
- Para la entrega final: `course-pr-skill` instalada, con `gh`/`az` ya autenticado (igual
  requisito que esa skill documenta en su propia guía).
- Por skill que termine seleccionada: sus propios requisitos de ejecución (Newman, Hurl CLI,
  JMeter, etc. — ver `references/prerequisites-check.md`). La generación de artefactos no
  siempre depende de tener la herramienta instalada; la ejecución sí.

## Flujo típico

1. `/qa:orquestar` con un número de PR y/o una historia de usuario pegada — corre
   `analizar → generar → ejecutar → consolidar` de punta a punta, parando en los gates que
   correspondan.
2. `/qa:analizar` primero escanea secretos, después clasifica. Si algo queda en confianza
   "Media" o "Ambigua", pregunta antes de seguir — revisar y confirmar.
3. `/qa:generar` invoca cada skill seleccionada, leyendo su `SKILL.md` y siguiendo su propio
   flujo — no hace falta repetirle el contexto, ya lo tiene.
4. `/qa:ejecutar` corre cada suite generada, después de verificar prerrequisitos.
5. `/qa:consolidar` arma `INFORME_CONSOLIDADO_*.md` a partir de los reportes nativos de cada
   skill.
6. `/qa:entregar` — pide confirmación, y ahí sí delega a `course-pr-skill`
   (`/curso:entregar`), que vuelve a confirmar antes de abrir el PR.

## Cuándo usar esto en vez de una skill individual

Si ya sabés con certeza qué skill aplica (por ejemplo, "necesito un `.feature` para un
criterio de aceptación"), usar esa skill directamente sigue siendo más rápido. Esta skill
suma valor cuando:

- No estás seguro de qué skill(s) aplican a un PR o historia.
- El cambio toca varias capas (API + UI, por ejemplo) y querés que se automaticen todas sin
  tener que invocar cada skill a mano.
- Necesitás dejar un registro auditable de por qué se automatizó con tal herramienta.

## Salidas

`BITACORA_<PR-o-historia>.md` (decisión de ruteo), artefactos propios de cada skill invocada
(sin cambios respecto a lo que esa skill ya documenta), `INFORME_CONSOLIDADO_<NOMBRE>.md`
(agregado de resultados), y finalmente el PR vía `course-pr-skill`.
