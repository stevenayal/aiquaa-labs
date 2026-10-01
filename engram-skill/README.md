# engram-skill

Memoria persistente entre sesiones con [engram](https://github.com/stevenayal/engram) — un
binario Go con SQLite + FTS5 expuesto como servidor MCP. La skill define el protocolo completo
de uso para el curso: qué guardar y cuándo, cómo recuperar contexto antes de re-explorar,
cómo cerrar sesión y sobrevivir a la compactación, cómo escribir en el proyecto correcto y
cómo resolver conflictos entre memorias. Degrada con gracia: si engram no está configurado,
sigue sin memoria.

## Instalación

```bash
npx skills add aiquaa-labs/engram-skill
```

Requiere el binario `engram` y su servidor MCP configurado en el agente para tener memoria
real — ver [references/instalacion.md](./references/instalacion.md). Sin ellos, la skill no
bloquea nada.

## Por qué existe

El curso dura 8 semanas y cada semana es una sesión nueva: el agente olvida qué convención de
prefijos se eligió, por qué se usó Hurl en vez de Postman para cierto endpoint, qué
`data-testid` estaba roto o cómo se resolvió un flaky en JMeter. Sin memoria, cada sesión
re-explora el repo y gasta tokens en reconstruir decisiones ya tomadas. Engram guarda esas
decisiones; esta skill fija **cuándo** guardarlas, **cómo** formatearlas para que se
encuentren, y **qué nunca** guardar (secretos, credenciales).

## Comandos / triggers

No define comandos `/` propios. Se activa cuando el usuario menciona "engram", "memoria
persistente", "acordate", "¿qué hicimos?", "guardá esta decisión", "resumen de sesión", al
cerrar una sesión, o después de una compactación de contexto.

## Contenido

- `skills/engram/SKILL.md` — protocolo: disponibilidad → recuperar → guardar → conflictos →
  cierre/compactación → proyecto correcto.
- `references/herramientas-mcp.md` — las 19 herramientas `mem_*` y perfiles (`agent`/`admin`).
- `references/cli.md` — comandos `engram` y variables de entorno.
- `references/proyectos.md` — resolución de proyecto, monorepos, `ambiguous_project`.
- `references/sync-cloud.md` — sync por git y cloud (opt-in).
- `references/instalacion.md` — binario + setup por agente (Claude Code, OpenCode, Codex, …).
- `references/troubleshooting.md` — síntomas comunes y `engram doctor`.

→ [Guía de uso](./docs/uso.md)

## Relación con otras skills

- `token-optimization-skill` recomienda consultar engram antes de re-explorar; esta skill es
  el detalle de cómo hacerlo bien.
- `course-pr-skill`: el `mem_session_summary` de cierre es un buen insumo para la descripción
  del PR semanal.
- Si el plugin oficial de engram para Claude Code ya está instalado, trae su propio skill de
  protocolo (en inglés); esta skill es compatible y agrega las reglas del curso.

## Licencia

MIT — engram es MIT (© Gentleman Programming).
