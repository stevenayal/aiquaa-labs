# engram-skill — CLAUDE.md

## Project

Skill de memoria persistente con engram (SQLite + FTS5 vía MCP) para sesiones de Claude del
curso de automatización aiquaa. Owned by aiquaa-labs. No genera archivos de prueba — define
el protocolo de cuándo guardar, buscar y resumir.

## Structure

```
skills/engram/  ← skill principal (protocolo de memoria)
references/     ← herramientas MCP, CLI, proyectos, sync/cloud, instalación, troubleshooting
docs/           ← guía de uso en español, con ejemplos antes/después
```

## Key rules

- No vendorea engram — lo referencia a https://github.com/stevenayal/engram (fork de
  `Gentleman-Programming/engram`). Si cambia upstream, actualizar `references/` contra
  `DOCS.md`, `docs/AGENT-SETUP.md` e `internal/mcp/mcp.go` (perfiles de herramientas).
- Compatible con el protocolo oficial (`plugin/claude-code/skills/memory/SKILL.md` del repo
  de engram): mismos disparadores, formato What/Why/Where/Learned y estructura de
  `mem_session_summary`. No contradecirlo.
- Nunca instala el binario ni configura MCP/hooks/plugins por cuenta propia.
- Nunca guarda secretos, tokens ni credenciales en memoria (la memoria se puede sincronizar
  por git o cloud).
- Operaciones destructivas o que mueven datos (`mem_delete`, `mem_merge_projects`,
  `projects consolidate|prune`, `doctor repair --apply`, `delete --hard`) solo con
  confirmación explícita.
- Degradación elegante: sin `mem_*` en la sesión, se sigue trabajando sin memoria.
