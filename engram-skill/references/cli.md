# CLI — engram

Útil cuando no hay MCP en la sesión, para inspeccionar a mano, o desde scripts/CI.

## Comandos

| Comando | Descripción |
|---------|-------------|
| `engram setup [agente]` | Instala la integración (`claude-code`, `opencode`, `codex`, `gemini-cli`, `pi`) |
| `engram mcp [--tools=PERFIL]` | Servidor MCP por stdio |
| `engram serve [puerto]` | API HTTP (default `7437`) |
| `engram tui` | Interfaz de terminal (`j/k`, `Enter`, `/` buscar, `c` copiar, `Esc`) |
| `engram search <query>` | Buscar memorias |
| `engram save <title> <msg> [--type T] [--project P]` | Guardar una memoria |
| `engram context [proyecto]` | Contexto de sesiones recientes |
| `engram timeline <obs_id>` | Contexto cronológico |
| `engram stats` | Estadísticas |
| `engram export [file]` / `engram import <file>` | Exportar / importar JSON |
| `engram sync [--import\|--status\|--project P\|--all]` | Sync por git (ver `sync-cloud.md`) |
| `engram conflicts list\|stats\|scan` | Auditar relaciones de conflicto (`scan --dry-run` primero) |
| `engram doctor [--json] [--project P] [--check C]` | Diagnóstico de solo lectura |
| `engram doctor repair --project P --check C --plan\|--dry-run\|--apply` | Reparación acotada — `--apply` hace backup antes. **Confirmar** |
| `engram projects list` | Proyectos con conteos |
| `engram projects consolidate [--dry-run]` | Fusionar nombres similares — **confirmar** |
| `engram projects prune [--dry-run]` | Borrar proyectos vacíos — **confirmar** |
| `engram delete <obs_id> [--hard]` | Borrar observación — **confirmar** |
| `engram delete project <name> [--hard]` | Borrado en cascada — **confirmar** |
| `engram cloud <sub>` | Config / estado / enrolamiento / servidor cloud (opt-in) |
| `engram obsidian-export` | Exportar a un vault de Obsidian (beta) |
| `engram version` | Versión |

Regla: los comandos marcados **confirmar** son destructivos o mueven datos — correr siempre
la variante `--dry-run`/`--plan` primero y pedir confirmación antes de la real.

## Variables de entorno

| Variable | Descripción | Default |
|----------|-------------|---------|
| `ENGRAM_DATA_DIR` | Directorio de datos | `~/.engram` |
| `ENGRAM_PORT` | Puerto HTTP | `7437` |
| `ENGRAM_PROJECT` | Proyecto default para `GET /sync/status` | detectado por cwd |
| `ENGRAM_HTTP_TOKEN` | Bearer para rutas destructivas/export del HTTP local | sin auth |
| `ENGRAM_TIMEZONE` | Zona horaria en TUI/dashboard | local |
| `ENGRAM_AGENT_CLI` | `claude` u `opencode` para `conflicts scan --semantic` | — |
| `ENGRAM_CLOUD_SERVER` / `ENGRAM_CLOUD_TOKEN` | Cliente cloud | — |
| `ENGRAM_CLOUD_AUTOSYNC` | `1` = autosync en segundo plano (requiere server + token) | off |

Para un entorno aislado de prueba (no toca `~/.engram`):

```bash
export ENGRAM_DATA_DIR=/tmp/engram-prueba
mkdir -p "$ENGRAM_DATA_DIR"
```
