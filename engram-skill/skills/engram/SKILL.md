---
name: engram
description: >
  Memoria persistente entre sesiones con engram — binario Go con SQLite + FTS5 expuesto como
  servidor MCP (`mem_*`), CLI, HTTP y TUI. Define el protocolo completo: qué guardar y cuándo
  (`mem_save` con What/Why/Where/Learned y `topic_key`), cómo recuperar contexto antes de
  re-explorar (`mem_context` → `mem_search` → `mem_get_observation`), cómo cerrar sesión y
  sobrevivir a la compactación (`mem_session_summary`), cómo resolver el proyecto correcto y
  cómo tratar conflictos entre memorias (`mem_judge`). Degrada con gracia: si las herramientas
  `mem_*` no están disponibles, lo dice en una línea y sigue sin memoria — nunca instala ni
  configura el servidor MCP por cuenta propia.
  Usar cuando el usuario mencione "engram", "memoria persistente", "acordate", "recordá",
  "qué hicimos la otra vez", "cómo lo resolvimos", "guardá esta decisión", "resumen de sesión",
  al cerrar una sesión ("listo", "eso es todo"), o después de una compactación de contexto.
---

Buscar antes de re-explorar. Guardar apenas se decide. Resumir antes de cerrar.

---

## ¿Qué es engram?

Un binario Go único (sin Node, Python ni Docker) que guarda observaciones en SQLite con
búsqueda full-text FTS5 (`~/.engram/engram.db`). El agente lo usa vía MCP:

```
Agente (Claude Code / OpenCode / Codex / Gemini CLI / Cursor / ...)
    ↓ MCP stdio  (engram mcp)
engram
    ↓
SQLite + FTS5  (~/.engram/engram.db)
```

Fuente: [stevenayal/engram](https://github.com/stevenayal/engram) (fork de
`Gentleman-Programming/engram`). Engram es infraestructura: si funciona bien, el usuario no
tiene que pensar en él — el agente guarda y recupera solo.

---

## Paso 0 — ¿Está disponible?

- Herramientas `mem_*` en la sesión (Claude Code: `mcp__engram__mem_*` o
  `mcp__plugin_engram_engram__mem_*`; pueden estar diferidas → cargarlas con ToolSearch).
- Si no están → decirlo en una línea ("engram no está configurado en esta sesión, sigo sin
  memoria persistente") y continuar. **No es un bloqueo.** Si el usuario pide instalarlo, ver
  `references/instalacion.md` y dejar que confirme.
- Si están → primera llamada recomendada: **`mem_current_project`** para confirmar en qué
  proyecto se va a escribir (ver Paso 5).

---

## Paso 1 — Recuperar antes de trabajar

Cuando el usuario pide recordar algo ("acordate", "¿qué hicimos?", "¿cómo lo resolvimos?") o
hace referencia a trabajo pasado:

1. `mem_context` — historial reciente de sesiones (rápido, barato).
2. Si no alcanza → `mem_search` con palabras clave (FTS5). `all_projects: true` para buscar
   en todos los proyectos; `scope: personal` para preferencias del usuario.
3. Si hay match → `mem_get_observation` con el ID para el contenido completo (la búsqueda
   devuelve contenido truncado). `mem_timeline` para ver qué pasó antes/después en esa sesión.

Buscar también **proactivamente**, sin que lo pidan:

- En el **primer mensaje**, si menciona el proyecto, una feature o un problema → `mem_search`
  con esas palabras antes de responder.
- Antes de empezar algo que pudo haberse hecho antes.
- Cuando aparece un tema del que no hay contexto en la sesión.

Leer las anotaciones de relación en los resultados: `superseded_by: #<id>` significa que esa
memoria ya fue reemplazada — usar la más nueva. `conflicts: #<id>` → no asumir, verificar.

---

## Paso 2 — Guardar apenas pasa algo que vale la pena

Llamar a `mem_save` **inmediatamente y sin que lo pidan** después de:

| Disparador | `type` |
|---|---|
| Decisión de arquitectura o diseño (con sus tradeoffs) | `architecture` / `decision` |
| El usuario confirma, rechaza o elige entre opciones ("dale", "mejor X", "no, eso no") | `decision` |
| Bug resuelto — **con la causa raíz** | `bugfix` |
| Hallazgo no obvio del código, gotcha, edge case | `discovery` |
| Convención fijada (naming, estructura, prefijos) | `pattern` |
| Cambio de configuración o de entorno | `config` |
| Preferencia o restricción del usuario | `preference` (con `scope: personal`) |

Auto-chequeo después de **cada** tarea:

> ¿Se tomó una decisión, se confirmó una recomendación, se expresó una preferencia, se arregló
> un bug, se aprendió algo no obvio o se fijó una convención? → `mem_save` ahora.

Formato:

```
title:     Verbo + qué — corto y buscable   ("Elegido Hurl sobre Postman para API smoke")
type:      bugfix | decision | architecture | discovery | pattern | config | preference
scope:     project (default) | personal
topic_key: familia/tema estable — opcional, recomendado si el tema evoluciona
content:
  **What**: una oración — qué se hizo
  **Why**: qué lo motivó (pedido, bug, performance, ...)
  **Where**: archivos o paths afectados
  **Learned**: gotchas, edge cases, sorpresas (omitir si no hay)
```

Reglas de `topic_key`:

- Temas distintos **nunca** se pisan (una decisión de arquitectura ≠ un bugfix).
- Si el mismo tema evoluciona → `mem_save` con el **mismo** `topic_key` (hace upsert e
  incrementa `revision_count`, no crea otra observación).
- Si no está claro el key → `mem_suggest_topic_key` primero y reutilizarlo siempre.
- Si se conoce el ID exacto a corregir → `mem_update`.

Qué **no** guardar: secretos, tokens, credenciales, contenido de `.env`, datos personales de
terceros, ni volcados de archivos completos. La memoria se puede sincronizar por git o cloud.
Lo que el código o el historial de git ya dicen por sí solos tampoco hace falta guardarlo —
guardar el *por qué*, no el *qué*.

---

## Paso 3 — Conflictos entre memorias

Si `mem_save` devuelve `candidates[]` con `judgment_required: true`, hay memorias previas que
podrían contradecir la nueva. Leer cada candidata (`mem_get_observation`) y registrar el
veredicto con `mem_judge`:

| `relation` | Cuándo |
|---|---|
| `supersedes` | La nueva reemplaza a la anterior (cambió la decisión) |
| `conflicts_with` | Se contradicen y ambas siguen vigentes — hay que resolverlo |
| `scoped` | Ambas valen, en ámbitos distintos (p. ej. backend vs frontend) |
| `compatible` / `related` | Tratan lo mismo sin contradecirse |
| `not_conflict` | Falso positivo léxico |

Si la confianza es **< 0.7**, preguntar al usuario antes de llamar a `mem_judge`.

---

## Paso 4 — Cerrar sesión y sobrevivir a la compactación

**Antes de decir "listo" / "eso es todo"** — obligatorio — `mem_session_summary` con:

```
## Goal
[En qué se trabajó]

## Instructions
[Preferencias o restricciones del usuario descubiertas — omitir si no hay]

## Discoveries
- [Hallazgos técnicos, gotchas, aprendizajes no obvios]

## Accomplished
- [Lo completado, con detalles clave]

## Next Steps
- [Lo que queda para la próxima sesión]

## Relevant Files
- path/al/archivo — [qué hace o qué cambió]
```

Sin esto, la próxima sesión arranca a ciegas.

**Después de una compactación o reseteo de contexto**, en este orden:

1. `mem_session_summary` con el contenido del resumen compactado — persiste lo hecho antes.
2. `mem_context` — recupera contexto de sesiones anteriores.
3. Recién ahí seguir trabajando.

---

## Paso 5 — Proyecto correcto

Engram resuelve el proyecto en cada llamada, a partir del **cwd del servidor MCP**:

1. `.engram/config.json` más cercano dentro de la raíz git → `project_name`
2. Raíz git con remote `origin` → nombre del repo
3. Subdirectorio de un repo → nombre de la raíz git
4. Un solo repo hijo → ese repo (con warning)
5. Varios repos hijos → error `ambiguous_project`
6. Sin git → nombre del directorio

Reglas:

- Si una escritura devuelve **`ambiguous_project`** → **no adivinar.** Mostrar
  `available_projects`, que el usuario elija uno exacto, y reintentar `mem_save` con
  `project: "<elegido>"` y `project_choice_reason: "user_selected_after_ambiguous_project"`.
- `project_name_collision` → pedirle al usuario que renombre/desambigüe; no reintentar a ciegas.
- Un `project` explícito inventado falla — `mem_save(project=...)` selecciona un proyecto
  existente, no crea uno nuevo.
- Para fijar el proyecto de un repo o subproyecto de monorepo, sugerir (no crear sin
  confirmación) `.engram/config.json` con `{"project_name": "nombre"}`.

Detalle completo → `references/proyectos.md`.

---

## Referencias

- `references/herramientas-mcp.md` — las 19 herramientas `mem_*`, parámetros y perfiles.
- `references/cli.md` — comandos `engram` y variables de entorno.
- `references/proyectos.md` — resolución de proyecto, monorepos y recuperación de ambigüedad.
- `references/sync-cloud.md` — sincronización por git y cloud (opt-in).
- `references/instalacion.md` — instalación del binario y setup por agente.
- `references/troubleshooting.md` — síntomas comunes, `engram doctor` / `mem_doctor`.

---

## Boundaries

No instala el binario ni configura el servidor MCP, hooks o plugins por cuenta propia — si el
usuario lo pide, documentar el comando y esperar confirmación.
No edita `~/.engram/engram.db` a mano ni ejecuta `mem_delete`, `mem_merge_projects`,
`engram projects consolidate|prune`, `engram doctor repair --apply` ni `engram delete ... --hard`
sin confirmación explícita — son destructivos o mueven datos entre proyectos.
No habilita sync a cloud ni commitea `.engram/` sin que el usuario lo pida.
Nunca guarda secretos ni credenciales en memoria.
Si engram no está disponible, el trabajo sigue sin memoria — nunca es un bloqueo.
"stop engram" o "sin memoria": dejar de guardar proactivamente en esta sesión (las búsquedas
pedidas explícitamente siguen funcionando).
