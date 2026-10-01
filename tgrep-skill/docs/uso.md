# Guía de uso — tgrep-skill

Ejemplos de antes/después. Todos asumen `tgrep` en el `PATH`; si no está, la skill sigue con
`rg`/`Grep` y lo dice en una línea.

---

## 1. Arrancar una sesión en un repo grande

**Sin criterio:** cada búsqueda es un `grep -r` que recorre `node_modules`, reportes y
fixtures generados.

**Con esta skill:**
```bash
tgrep status .          # ¿ya hay servidor?
tgrep serve . &         # si no: construye el índice y responde mientras construye
grep -qx ".tgrep/" .gitignore || echo ".tgrep/" >> .gitignore
```

---

## 2. Buscar un símbolo o texto que dio el usuario

**Sin criterio (falla o busca otra cosa):**
```bash
tgrep "Vec<Option<T>>" .     # regex mal escapada
tgrep serve .                # ¡levanta un servidor en vez de buscar "serve"!
```

**Con esta skill:**
```bash
tgrep -F -- "Vec<Option<T>>" .
tgrep -F -- serve .
```

---

## 3. Consulta amplia sin inundar el contexto

**Sin criterio:** `tgrep -- "TODO" .` → miles de líneas en el contexto.

**Con esta skill:**
```bash
tgrep -l -t ts -- "TODO" .                        # primero: qué archivos
tgrep -C 2 -- "TODO" tests/login.spec.ts          # después: el archivo puntual
```

---

## 4. Verificar un edit recién hecho

**Sin criterio:** se edita `pages/LoginPage.ts`, se busca el método nuevo y el índice todavía
no lo tiene → "no existe", y el agente lo vuelve a escribir.

**Con esta skill:**
```bash
tgrep --no-index -F -- "loginWithSso" pages/
```
O, sin servidor, re-ejecutar `tgrep index .` antes de la próxima búsqueda indexada.

---

## 5. Leer el resultado correctamente

```bash
tgrep -q -F -- "data-testid=\"btn-pagar\"" src/
echo $?   # 0 = existe · 1 = no existe (no es error) · 2 = error, leer stderr
```

---

## 6. Búsqueda lenta "sin razón"

```bash
tgrep --stats -- "\w+Service" .
# Candidates: ... (no index narrowing)  → el patrón no tiene trigramas útiles
tgrep --stats -t ts -- "PaymentService" .   # literal de 3+ caracteres → el índice acota
```

Si sigue lento, revisar que no haya un flag que saltee el índice (`--no-ignore`, `-u`, `-a`,
`--binary`, `-E`) — ver `references/troubleshooting.md`.
