# tgrep-skill — CLAUDE.md

## Project

Skill de búsqueda de código con tgrep (grep indexado por trigramas, compatible con ripgrep)
para sesiones de Claude del curso de automatización aiquaa. Owned by aiquaa-labs. No genera
archivos de prueba — fija criterio sobre cómo indexar, buscar e interpretar resultados.

## Structure

```
skills/tgrep/   ← skill principal (disponibilidad → índice → búsqueda → interpretación)
references/     ← flags, troubleshooting, instalación
docs/           ← guía de uso en español, con ejemplos antes/después
```

## Key rules

- No vendorea tgrep — lo referencia a https://github.com/stevenayal/tgrep (fork de
  `microsoft/tgrep`). Si cambia la CLI upstream, actualizar `references/flags.md` contra el
  README y `AGENTS.md` de ese repo.
- Nunca instala el binario ni ejecuta `install-agent.sh` por cuenta propia — documenta el
  comando y espera confirmación del usuario.
- Degradación elegante: si `tgrep` no está en el `PATH`, la búsqueda sigue con `rg`/`Grep`.
- `.tgrep/` y `.tgrep-agent/` nunca se commitean.
- Reglas de búsqueda innegociables: `--` antes del patrón, raíz explícita, exit code `1` no es
  error, flags de índice alineados entre `index`/`serve`/búsqueda.
