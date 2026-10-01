---
name: tgrep
description: >
  Búsqueda rápida de código con tgrep — grep con índice de trigramas y servidor opcional,
  compatible con los flags de ripgrep. Cubre cuándo indexar (`tgrep index`), cuándo levantar
  el servidor (`tgrep serve`), cómo buscar sin errores de parseo (`--` antes del patrón, `-F`
  para literales, `-t`/`-g` para acotar), cómo leer frescura del índice y exit codes, y qué
  flags hacen que el índice se ignore. Degrada con gracia: si `tgrep` no está instalado, sigue
  con `rg`/`Grep` — nunca instala binarios por cuenta propia.
  Usar cuando el usuario mencione "tgrep", "búsqueda indexada", "índice de trigramas",
  "grep rápido en repo grande", "monorepo lento para buscar", o pida buscar en un repositorio
  donde ya existe `.tgrep/`.
---

Indexar una vez. Servir durante la sesión. Buscar con `--`. `--no-index` cuando importa lo último.

---

## ¿Qué es tgrep?

`tgrep` es ripgrep con un índice de trigramas pre-construido y un servidor opcional. El índice
reduce cada consulta a los archivos que *podrían* coincidir y después los verifica con el
motor de regex en paralelo. En repos grandes (Chromium, Gecko, Kubernetes) es varias veces más
rápido que `rg` con el índice ya caliente.

Fuente: [stevenayal/tgrep](https://github.com/stevenayal/tgrep) (fork de `microsoft/tgrep`).

Una búsqueda se resuelve sola, en este orden — el comando es siempre el mismo:

| # | Fuente | Velocidad | Frescura |
|---|---|---|---|
| 1 | **Servidor** (`tgrep serve`) para este árbol | La más rápida | Watcher asíncrono — un edit recién hecho puede no estar aún |
| 2 | **Índice en disco** (`.tgrep/`) sin servidor | Rápida | Solo hasta el último `tgrep index` |
| 3 | **Sin índice** — escanea todo, como grep | Lenta en árboles grandes | Siempre actual. Avisa por stderr: `warning: no index at ...` |

---

## Paso 0 — ¿Está disponible?

```bash
command -v tgrep && tgrep status .
```

- **No está instalado** → decirlo en una línea y seguir con `rg` / la herramienta `Grep`. No
  bloquear el trabajo ni instalar por cuenta propia. Si el usuario pide instalarlo, ver
  `references/instalacion.md`.
- **Instalado, sin índice** → ver Paso 1.
- **Servidor activo** (`tgrep status .` muestra `PID`/`Port`) → ir directo al Paso 2.

---

## Paso 1 — Preparar el índice (una vez por sesión)

| Situación | Comando |
|---|---|
| El agente puede mantener un proceso en segundo plano | `tgrep serve . &` (construye el índice si falta y responde mientras construye) |
| No puede mantener procesos vivos | `tgrep index .` — y **re-ejecutarlo después de cada edit** que una búsqueda posterior tenga que ver |
| Repo sin `.git` | Agregar `--no-require-git` a `index`, `serve` **y** cada búsqueda |
| Directorios pesados que no interesan | `--exclude vendor --exclude node_modules` (solo en `index` y `serve`, mismo valor en ambos) |

Agregar `.tgrep/` al `.gitignore` del proyecto si no está — **nunca commitear el índice**.

Regla dura: los flags que describen el índice tienen que coincidir entre `index`, `serve` y
búsqueda — si no, el cliente no encuentra el servidor o busca en otro conjunto de archivos:

- `--exclude` → igual en `index` y `serve`.
- `--no-ignore` → igual en `index` y `serve` (en una búsqueda fuerza escaneo completo).
- `--index-path`, `--max-filesize` / `--no-max-filesize`, `--no-require-git` → igual en
  `index`, `serve` **y** cada búsqueda.

---

## Paso 2 — Buscar

```bash
tgrep -- "fn parse_config" .                 # regex (default)
tgrep -F -- "Vec<Option<T>>" .               # literal — sin escapar regex
tgrep -w -t rust -- handle .                 # palabra completa, solo Rust
tgrep -g "src/**" -C 2 -- "TODO|FIXME" .     # acotado por glob, 2 líneas de contexto
tgrep -l -- "impl .* for Server" .           # solo nombres de archivo
tgrep -c -- deprecated .                     # conteo por archivo
tgrep -q -- "pattern" .                      # solo exit code (sí/no)
tgrep --files -t py .                        # listar archivos Python indexados
tgrep --json -- "pattern" .                  # stream JSON compatible con rg --json
tgrep --vimgrep -- "pattern" .               # file:line:col:text, uno por match
```

Reglas para el agente:

1. **Siempre `--` antes del patrón, y la raíz explícita.** Las comillas no evitan que
   `index`, `serve`, `search`, `status`, `count-files` o `help` se lean como subcomando.
   `tgrep -- serve .` busca la palabra. Todos los flags van **antes** de `--`.
2. **Preferir `-F`** cuando la consulta es un símbolo o un texto que tipeó el usuario — evita
   errores de escape de regex.
3. **Acotar con `-t` o `-g` antes que con `-m`.** Ambos siguen usando el índice; `-m` solo
   recorta la salida.
4. **`-l` primero** en consultas amplias, después buscar en los archivos puntuales — salida
   chica, menos tokens.
5. **`-C 2` / `-C 3`** cuando hace falta leer el código alrededor.
6. **`--no-index`** cuando el resultado tiene que reflejar un edit recién hecho (propio o del
   usuario). Es lento en árboles grandes — usarlo a conciencia, no por defecto.
7. **`--stats`** para diagnosticar una búsqueda lenta: `no index narrowing` significa que el
   patrón no tiene trigramas útiles y se recorrió todo el índice.

---

## Paso 3 — Interpretar el resultado

| Exit code | Significado | Qué hacer |
|---|---|---|
| `0` | Al menos un match | Usar la salida |
| `1` | Sin matches | **No es un error** — reportar "sin resultados" |
| `2` | Error (regex inválida, path ilegible) | Leer stderr; con `-q`, match + error da `0` |

Siempre leer stderr: el aviso `warning: no index at ... - scanning every file` puede llegar
con exit code `0` o `1` y explica por qué la búsqueda fue lenta.

`tgrep status .` → `Indexing: complete` y `Hidden coverage: complete` describen **disponibilidad**
del índice, no frescura. No usarlos como prueba de que el último edit está indexado.

---

## Flags que saltean el índice

Estos fuerzan escaneo completo aunque haya servidor — evitarlos en repos grandes salvo que
hagan falta:

- `--no-ignore` y variantes, `-u` / `-uu` / `-uuu`
- `-a` / `--text`, `--binary`, `-E` / `--encoding` distinto de `auto`
- `--no-index` (explícito)
- Nombrar un archivo puntual en vez de un directorio

`-L`/`--follow`, `--one-file-system` e `--ignore-file` **se ignoran en silencio** en búsquedas
indexadas — combinarlos con `--no-index` si hacen falta.

Diferencias con `rg` a tener en cuenta: límite de tamaño por defecto de **64 MiB**
(`--no-max-filesize` para quitarlo, igual en índice y búsqueda); `-P` usa `fancy-regex`, no
PCRE2 real; `-z/--search-zip` no está soportado (sale con `2`).

Problemas comunes y su arreglo → `references/troubleshooting.md`.
Tabla completa de flags → `references/flags.md`.

---

## Boundaries

No instala tgrep ni configura servidores MCP / hooks de agente por cuenta propia — si el
usuario lo pide, documentar el comando (`references/instalacion.md`) y dejar que lo confirme.
No commitea `.tgrep/` ni `.tgrep-agent/`.
No deja un `tgrep serve` corriendo sin decirlo — avisar en una línea que quedó un proceso en
segundo plano y cómo detenerlo.
Si `tgrep` no está disponible, la búsqueda sigue con `rg`/`Grep` — nunca es un bloqueo.
"stop tgrep" o "usar rg": volver a la búsqueda nativa sin este criterio.
