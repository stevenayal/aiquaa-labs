# Troubleshooting — engram

| Síntoma | Causa probable | Arreglo |
|---------|----------------|---------|
| No hay herramientas `mem_*` en la sesión | MCP no configurado, o herramientas diferidas | Buscar con ToolSearch (`engram mem_save`). Si no aparecen: `engram setup claude-code` y reiniciar Claude Code (lo ejecuta el usuario) |
| Herramientas existen pero piden permiso cada vez | Allowlist incompleta | Re-ejecutar `engram setup claude-code` y aceptar el allowlist |
| `ambiguous_project` al guardar | El agente arrancó en una carpeta con varios repos | Recuperación con `available_projects` (ver `proyectos.md`), o arrancar desde el repo, o `.engram/config.json` |
| `unknown_project` en una lectura | `project` explícito que no existe en el store | Omitir `project` o usar uno de `available_projects` |
| Las memorias quedan en un proyecto con otro nombre | Detección por basename / sin remote | `mem_current_project` para ver `project_source`; fijar con `.engram/config.json`; para unificar el pasado, `engram projects consolidate --dry-run` (confirmar antes de aplicar) |
| `project_name_collision` | Dos nombres normalizan igual (`foo--bar` / `foo-bar`) | Pedir al usuario que renombre o desambigüe |
| `mem_save` falla con `session_id` | La sesión no existe, o no coincide con `project` | Omitir `session_id` o usar el correcto |
| `mem_search` no encuentra algo que se guardó | Otro proyecto, o palabras distintas | `all_projects: true`; probar sinónimos; `mem_context` primero |
| Resultado con `superseded_by: #N` | La memoria fue reemplazada | Usar `#N` (`mem_get_observation`) |
| Tras actualizar engram sigue el comportamiento viejo | El proceso MCP viejo sigue vivo | `engram setup claude-code` + reiniciar el agente |
| `database is locked` / lentitud | Contención de SQLite | `engram doctor --check sqlite_lock_contention` |
| Sync cloud bloqueado | Datos legacy / campos faltantes | `engram doctor`, `engram cloud upgrade doctor --project P`; seguir `docs/engram-cloud/troubleshooting.md` del repo |
| Autosync "dejó de andar" | `engram serve` murió (p. ej. tras `brew upgrade`) | `engram cloud status` → `Local daemon:`; relanzar `engram serve` |

## Diagnóstico

```bash
engram doctor                 # resumen legible
engram doctor --json          # para agentes (mismo formato que mem_doctor)
engram doctor --project P --check session_project_directory_mismatch
```

`engram doctor` es solo lectura. Si un check marca `requires_confirmation: true`, mostrar la
evidencia al usuario; la reparación (`engram doctor repair ... --plan` → `--dry-run` →
`--apply`) se corre solo con su confirmación. `--apply` hace backup en
`<ENGRAM_DATA_DIR>/backups/` antes de tocar nada.
