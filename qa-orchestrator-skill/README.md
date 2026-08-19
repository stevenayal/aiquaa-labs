# qa-orchestrator-skill

Agente QA que decide **qué skill(s) del stack aiquaa usar**, según el contexto de un Pull
Request y/o una historia de usuario/requerimiento. Puede combinar varias skills en una misma
corrida (API + UI + BD + rendimiento), las invoca en secuencia para generar y correr la
automatización, y entrega un informe consolidado + una bitácora de decisión auditable. Nunca
adivina en casos ambiguos — pregunta. Nunca abre el PR final — delega siempre a
`course-pr-skill` con confirmación explícita.

## Instalación

```bash
npx skills add aiquaa-labs/qa-orchestrator-skill
```

Requiere tener instaladas (o poder instalar bajo demanda) las skills que el ruteo termine
seleccionando — ver [Instalación completa del stack](../README.md#instalación-completa-del-stack)
en el README raíz del monorepo.

## Por qué existe

Con 10 skills QA independientes, elegir cuál usar para un PR o una historia era una decisión
manual contra la tabla "¿Cuál usar?" del README raíz — y no había forma de combinar varias
automáticamente cuando un cambio tocaba más de una capa, ni un registro de por qué se eligió
tal skill. Esta skill reemplaza esa decisión manual por un mapa de señales determinístico
(rutas, extensiones, keywords), con confirmación explícita en los casos ambiguos y una
bitácora que deja el razonamiento por escrito.

## Comandos

| Comando | Acción |
|---------|--------|
| `/qa:analizar <PR#\|diff\|historia>` | Intake + escaneo de secretos + clasificación + gate si es ambiguo |
| `/qa:generar` | Invoca cada skill seleccionada para generar sus artefactos |
| `/qa:ejecutar` | Corre cada suite generada, verificando prerrequisitos |
| `/qa:consolidar` | Agrega los reportes nativos en un informe consolidado |
| `/qa:orquestar` | Flujo completo `analizar → generar → ejecutar → consolidar` |
| `/qa:entregar` | Resumen final + delega a `course-pr-skill` (con confirmación) |

## Hardening — las 4 dimensiones

- **Seguridad** — escaneo de secretos al inicio (no solo antes de entregar), nunca hardcodea
  credenciales, respeta el gateway REST de `database-object-testing-skill` (nunca driver
  directo), nunca ejecuta rendimiento contra un entorno no confirmado como no-producción.
- **Confiabilidad** — clasificación por reglas primero, LLM solo para desempatar; prerrequisitos
  chequeados antes de generar/ejecutar cada skill; reintentos de idempotencia vía hash de
  contenido; nunca falla en silencio.
- **Auditoría** — cada corrida deja una `BITACORA_*.md` con señales, puntajes, decisión,
  prerrequisitos, ejecución y confirmaciones humanas.
- **Human-in-the-loop** — ruteo ambiguo o de confianza media siempre se confirma; entrega
  final siempre pasa por `course-pr-skill`, que vuelve a confirmar antes de abrir el PR; el
  orquestador nunca hace `git push`, abre PR ni mergea por su cuenta.

## Contenido

- `skills/qa-orchestrator/SKILL.md` — el flujo completo
- `references/signal-mapping.md` — mapa completo de señales → skill → peso
- `references/decision-log-schema.md` — formato de la bitácora
- `references/consolidated-report-schema.md` — formato del informe consolidado
- `references/prerequisites-check.md` — checks por skill antes de generar/ejecutar
- `examples/` — diffs sintéticos + historia + bitácora/informe de ejemplo

→ [Guía de uso](./docs/uso.md)

## Licencia

MIT
