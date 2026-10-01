# Resolución de proyecto — engram

Engram decide en qué proyecto leer/escribir **en cada llamada**, a partir del cwd del proceso
del servidor MCP (no del momento en que arrancó).

## Algoritmo de detección

| # | Condición | `project_source` | Proyecto |
|---|-----------|------------------|----------|
| 1 | Hay `.engram/config.json` más cercano dentro de la raíz git (o en el cwd fuera de git) | `config` | `project_name` del config |
| 2 | El cwd es raíz git con remote `origin` | `git_remote` | nombre del repo según la URL |
| 3 | El cwd está dentro de un repo (subdirectorio) | `git_root` | nombre de la carpeta raíz |
| 4 | El cwd tiene exactamente un repo hijo | `git_child` | ese repo (con warning) |
| 5 | El cwd tiene varios repos hijos | error `ambiguous` | las escrituras fallan |
| 6 | No hay git cerca | `dir_basename` | nombre del cwd |

## Precedencia de `mem_save`

1. `project` explícito **válido** (debe existir en el store, en la sesión, en un
   `.engram/config.json` resoluble, o ser una recuperación de ambigüedad exacta).
2. Proyecto asociado al `session_id`.
3. Detección por config / cwd.
4. Nombre del directorio.

`mem_session_end`, `mem_session_summary` y `mem_capture_passive` **ignoran** `project` y usan
siempre el cwd. Las herramientas de lectura (`mem_search`, `mem_context`, `mem_timeline`,
`mem_stats`, `mem_doctor`) aceptan `project` opcional, validado contra el store.

## Recuperar un `ambiguous_project`

Pasa cuando el MCP arrancó en una carpeta padre con varios repos:

```json
{ "error_code": "ambiguous_project",
  "available_projects": ["aiquaa-labs", "tgrep", "engram"] }
```

1. **No adivinar.** Mostrar la lista al usuario.
2. El usuario elige **un valor exacto**.
3. Reintentar:

```json
{ "project": "aiquaa-labs",
  "project_choice_reason": "user_selected_after_ambiguous_project" }
```

Si devuelve `project_name_collision` (p. ej. `foo--bar` vs `foo-bar` normalizan igual), pedir
al usuario que renombre o desambigüe antes de reintentar.

Alternativas permanentes: arrancar el agente desde el repo, o agregar `.engram/config.json`.

## Fijar el proyecto con `.engram/config.json`

```json
{ "project_name": "aiquaa-labs" }
```

En monorepos, un config por subproyecto: `backend/.engram/config.json` y
`frontend/.engram/config.json` se resuelven como proyectos independientes. Un
`~/.engram/config.json` en el home **no** se filtra hacia repos anidados.

La skill **sugiere** este archivo; no lo crea sin confirmación del usuario.
