# Instalación — engram

La skill **nunca** instala engram ni configura el MCP por cuenta propia. Estos comandos se
documentan para que el usuario los ejecute (o confirme que el agente los ejecute).

## 1. Binario

| Plataforma | Comando |
|------------|---------|
| macOS / Linux (Homebrew) | `brew install gentleman-programming/tap/engram` |
| Cualquiera con Go 1.24+ | `go install github.com/Gentleman-Programming/engram/cmd/engram@latest` |
| Desde el fork | `git clone https://github.com/stevenayal/engram.git && cd engram && go install ./cmd/engram` |
| Binario pre-compilado | GitHub Releases → `engram_<versión>_<os>_<arch>.tar.gz` / `.zip` |

Sin dependencias de runtime (SQLite embebido, Go puro). Datos en `~/.engram/engram.db`
(Windows: `%USERPROFILE%\.engram\engram.db`).

En Windows, los binarios pre-compilados sin firmar pueden disparar falsos positivos del
antivirus — preferir `go install`.

```bash
engram version
```

## 2. Integración con el agente

| Agente | Comando |
|--------|---------|
| Claude Code (plugin, recomendado) | `claude plugin marketplace add Gentleman-Programming/engram && claude plugin install engram` |
| Claude Code (desde el binario) | `engram setup claude-code` |
| Claude Code (MCP pelado) | `claude mcp add engram -- engram mcp` |
| OpenCode | `engram setup opencode` |
| Codex | `engram setup codex` |
| Gemini CLI | `engram setup gemini-cli` |
| Pi | `engram setup pi` |
| VS Code (Copilot) | `code --add-mcp '{"name":"engram","command":"engram","args":["mcp"]}'` |
| Cursor / Windsurf / otro MCP | Config JSON manual con `command: "engram"`, `args: ["mcp"]` |

El plugin de Claude Code registra el servidor MCP, los hooks de sesión (inicio, prompt,
compactación, cierre) y su propio skill de protocolo de memoria. Esta skill es compatible con
ese protocolo — lo explica en español y agrega las reglas del curso (no guardar secretos,
confirmar operaciones destructivas).

`engram setup claude-code` pregunta si agregar las herramientas a `permissions.allow` de
`~/.claude/settings.json`. Re-ejecutarlo repara allowlists viejas.

## 3. Después de actualizar el binario

Un servidor MCP stdio ya corriendo **no** se reemplaza al actualizar el binario en disco:

```bash
engram setup claude-code   # refresca config y hooks
# y reiniciar Claude Code
```

## 4. Verificar

En la sesión del agente: `mem_current_project` debe responder con el proyecto esperado, y
`mem_stats` con conteos. Desde la terminal: `engram doctor`.
