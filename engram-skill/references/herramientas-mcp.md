# Herramientas MCP — engram

Referencia de las 19 herramientas `mem_*`. Fuente: `DOCS.md` del repo
[stevenayal/engram](https://github.com/stevenayal/engram#mcp-tools-19).

En Claude Code aparecen como `mcp__engram__<tool>` (o `mcp__plugin_engram_engram__<tool>` en
instalaciones de plugin viejas). Las herramientas core las precarga el hook de arranque del
plugin; las de administración pueden estar diferidas (cargarlas con ToolSearch).

## Perfiles

| Comando | Herramientas |
|---------|--------------|
| `engram mcp` | Las 19 (default) |
| `engram mcp --tools=agent` | 15 orientadas al agente — todas menos las 4 de admin. Lo que instalan los plugins de OpenCode / Pi |
| `engram mcp --tools=admin` | 4 de curación manual: `mem_delete`, `mem_stats`, `mem_timeline`, `mem_merge_projects` |
| `engram mcp --tools=agent,admin` | Combinar perfiles (o listar nombres sueltos: `--tools=mem_save,mem_search`) |

Si `mem_timeline` o `mem_stats` no aparecen, el servidor corre con el perfil `agent` — no es
un error.

## Guardar y actualizar

| Herramienta | Parámetros clave | Notas |
|-------------|------------------|-------|
| `mem_save` | `title`, `type`, `content`, `scope?`, `topic_key?`, `project?`, `session_id?`, `capture_prompt?` | Deduplica guardados idénticos en una ventana de tiempo. Con `topic_key` hace upsert (`revision_count++`). Puede devolver `candidates[]` + `judgment_required` |
| `mem_update` | `id`, `title?`, `content?`, `type?`, `scope?`, `topic_key?` | Actualización parcial por ID |
| `mem_suggest_topic_key` | `type`, `title` (o `content`) | Sugiere un key estable (`architecture/*`, `bug/*`, `decision/*`, …) |
| `mem_delete` | `id`, `hard_delete?` | Soft-delete por defecto. **Pedir confirmación** |

`type`: `bugfix` · `decision` · `architecture` · `discovery` · `pattern` · `config` · `preference` · `learning`
`scope`: `project` (default) · `personal` · `global`

## Buscar y recuperar

| Herramienta | Parámetros clave | Notas |
|-------------|------------------|-------|
| `mem_context` | `project?`, `scope?` | Sesiones, prompts y observaciones recientes. **Primera opción** — barata |
| `mem_search` | `query`, `type?`, `project?`, `scope?`, `limit?`, `all_projects?` | FTS5. Contenido truncado. Anota `supersedes:` / `superseded_by:` / `conflicts:` |
| `mem_get_observation` | `id` | Contenido completo, sin truncar |
| `mem_timeline` | `id` | Observaciones antes/después en la misma sesión |

## Ciclo de sesión

| Herramienta | Uso |
|-------------|-----|
| `mem_session_start` | Registrar inicio (`directory?` define el proyecto) |
| `mem_session_end` | Marcar sesión terminada, con resumen opcional |
| `mem_session_summary` | Resumen estructurado (Goal / Instructions / Discoveries / Accomplished / Next Steps / Relevant Files). **Obligatorio al cerrar y tras compactación** |

## Conflictos

| Herramienta | Uso |
|-------------|-----|
| `mem_judge` | `judgment_id` (de `mem_save`), `relation`, `reason?`, `evidence?`, `confidence?` — si confianza < 0.7, preguntar al usuario antes |
| `mem_compare` | `memory_id_a`, `memory_id_b`, `relation`, `confidence`, `reasoning` (≤ 200 chars), `model?` — comparación proactiva entre dos memorias del mismo proyecto |

`relation`: `related` · `compatible` · `scoped` · `conflicts_with` · `supersedes` · `not_conflict`

## Utilidades

| Herramienta | Uso |
|-------------|-----|
| `mem_current_project` | Detecta el proyecto desde el cwd. Nunca falla; si es ambiguo devuelve `project` vacío + `available_projects`. **Primera llamada recomendada** |
| `mem_save_prompt` | Guarda el pedido del usuario como contexto para sesiones futuras |
| `mem_capture_passive` | Extrae aprendizajes de una sección `## Key Learnings:` y los guarda uno por uno |
| `mem_stats` | Conteos de sesiones, observaciones, prompts, proyectos |
| `mem_doctor` | Diagnóstico de solo lectura (mismo JSON que `engram doctor --json`), `project?`, `check?` |
| `mem_merge_projects` | `from` (lista separada por comas), `to` — **admin, mueve datos; pedir confirmación** |

## Sobre de respuesta

La mayoría de las respuestas vienen envueltas así:

```json
{
  "project": "aiquaa-labs",
  "project_source": "git_remote",
  "project_path": "/home/user/aiquaa-labs",
  "result": "..."
}
```

Errores `ambiguous_project` / `unknown_project` incluyen `available_projects`.
