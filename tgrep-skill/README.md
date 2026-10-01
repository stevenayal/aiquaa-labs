# tgrep-skill

Búsqueda rápida de código con [tgrep](https://github.com/stevenayal/tgrep) — grep con índice
de trigramas y servidor opcional, compatible con los flags de ripgrep. La skill fija cuándo
indexar, cuándo levantar el servidor, cómo buscar sin errores de parseo, cómo leer la frescura
del índice y qué flags hacen que el índice se ignore. Degrada con gracia: si `tgrep` no está
instalado, sigue con `rg`/`Grep`.

## Instalación

```bash
npx skills add aiquaa-labs/tgrep-skill
```

Requiere el binario `tgrep` en el `PATH` para aprovechar el índice — ver
[references/instalacion.md](./references/instalacion.md). Sin él, la skill no bloquea nada.

## Por qué existe

En repos grandes (monorepos, proyectos del curso con muchos tests generados, `node_modules`
vendorizados) cada `grep` recorre todo el árbol. `tgrep` responde en milisegundos con el
índice caliente, pero tiene trampas que un agente comete solo: olvidar `--` y que el patrón
se lea como subcomando, buscar un edit recién hecho contra un índice viejo, usar un flag que
fuerza escaneo completo sin darse cuenta, o desalinear `--exclude`/`--index-path` entre
`index`, `serve` y búsqueda. Esta skill fija esas reglas.

## Comandos / triggers

No define comandos `/` propios — se activa cuando el usuario menciona "tgrep", "búsqueda
indexada", "índice de trigramas", "grep rápido en repo grande", o cuando el repo ya tiene un
directorio `.tgrep/`.

## Contenido

- `skills/tgrep/SKILL.md` — flujo disponibilidad → índice → búsqueda → interpretación.
- `references/flags.md` — tabla resumida de flags y subcomandos.
- `references/troubleshooting.md` — síntomas comunes y su arreglo.
- `references/instalacion.md` — instalación (Homebrew, Cargo, releases, integración MCP).

→ [Guía de uso](./docs/uso.md)

## Relación con otras skills

Complementa a `token-optimization-skill`: esa decide *qué herramienta usar primero*; esta
hace que la búsqueda textual, cuando toca, sea barata (`-l` primero, `-t`/`-g` para acotar,
salida chica).

## Licencia

MIT — tgrep es MIT (© Microsoft).
