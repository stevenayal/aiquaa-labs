# Referencia de flags — tgrep

Resumen de los flags de búsqueda más usados. La lista completa está en el
[README de tgrep](https://github.com/stevenayal/tgrep#cli-flags); para subcomandos usar
`tgrep index --help` y `tgrep serve --help`.

## Coincidencia

| Flag | Descripción |
|------|-------------|
| `-i, --ignore-case` | Sin distinguir mayúsculas |
| `-S, --smart-case` | Sin distinguir si el patrón es todo minúsculas |
| `-F, --fixed-strings` | Patrón literal |
| `-w, --word-regexp` | Palabra completa |
| `-x, --line-regexp` | Línea completa |
| `-v, --invert-match` | Líneas que NO coinciden |
| `-e, --regexp <PAT>` | Patrón adicional (OR, repetible) — con `-e`, todos los posicionales son paths |
| `-f, --file <FILE>` | Patrones desde archivo |
| `-U, --multiline` | Matches que cruzan líneas |
| `-P, --pcre2` | Motor con backtracking (`fancy-regex`: lookaround, backreferences) |
| `-r, --replace <TEXT>` | Reemplazo en la salida (`$1`, `${name}`) |

## Alcance

| Flag | Descripción |
|------|-------------|
| `-t, --type <TYPE>` / `-T, --type-not` | Filtrar / excluir tipo (`rust`, `py`, `js`, …) |
| `-g, --glob <GLOB>` / `--iglob` | Filtrar por glob (sigue usando el índice) |
| `-., --hidden` | Incluir ocultos (sigue usando el índice) |
| `--no-ignore`, `-u…` | No respetar `.gitignore` — **escaneo completo** |
| `--max-filesize <SIZE>` / `--no-max-filesize` | Límite de tamaño (default 64M) |
| `--no-index` | Leer del disco, ignorar servidor e índice |
| `--index-path <DIR>` | Índice en otra ubicación |
| `--no-require-git` | Aplicar `.gitignore` fuera de un repo Git |

## Salida

| Flag | Descripción |
|------|-------------|
| `-l` / `--files-without-match` | Solo archivos con / sin match |
| `-c` / `--count-matches` | Líneas con match / matches totales por archivo |
| `-m, --max-count <N>` | Máximo de líneas con match por archivo |
| `-A/-B/-C <N>` | Contexto después / antes / ambos |
| `-o, --only-matching` | Solo la parte que coincide |
| `-q, --quiet` | Solo exit code |
| `--json` | Stream JSON compatible con `rg --json` (`begin`/`match`/`context`/`end`/`summary`) |
| `--vimgrep` | `file:line:col:text`, una fila por match |
| `--files` | Listar paths admitidos (lee del índice; `--no-index` para el disco actual) |
| `--stats` | Plan de consulta, candidatos y tiempos |

## Subcomandos

| Comando | Uso |
|---------|-----|
| `tgrep index .` | Construir índice en `.tgrep/` (`--index-buffer <MiB>`, `--index-strategy=memory`, `--exclude <DIR>`) |
| `tgrep serve .` | Servidor con watcher (`--watch-mode poll`, `--poll-interval <s>`, `--no-watch`, `--max-memory`, `--max-cpu`) |
| `tgrep status .` | Estado del servidor / índice |
| `tgrep count-files .` | Contar archivos candidatos sin leer contenido |
