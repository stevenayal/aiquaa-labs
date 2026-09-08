# Instalación del hook — `/router:instalar`

El hook es la única capa del router que no se erosiona en una sesión larga. Las otras dos
(extractores e instrucciones) dependen de que el agente elija bien; el hook no depende de nada.

## Qué hace

Se registra como `PreToolUse` sobre `Read` y `Bash`. Ante cada llamada:

1. Si `QA_ROUTER_OFF=1` → permite y termina.
2. Si no hay `jq` disponible → permite y termina (**nunca rompe la sesión por faltar una
   dependencia**).
3. Extrae el archivo objetivo: `tool_input.file_path` en `Read`, o el argumento de un
   `cat`/`jq` sobre `.json|.jtl|.xml|.jmx|.csv|.har` en `Bash`.
4. Bloquea (`exit 2`) si el archivo es un artefacto QA conocido, **sin importar el tamaño**.
5. Bloquea si supera `QA_ROUTER_MIN_LINES` (400 por defecto).
6. En cualquier otro caso permite (`exit 0`).

El mensaje de bloqueo va a stderr y lo lee el modelo: siempre nombra el comando exacto que sí
está permitido.

## Qué NO bloquea nunca

- `Read` con `offset`/`limit` — lectura acotada es justamente el comportamiento buscado.
- `grep`, `wc`, `head -n <chico>`, `tail` — inspección acotada.
- La ejecución de los propios extractores.
- Herramientas distintas de `Read`/`Bash` (`Edit`, `Write`, `Glob`, `Grep`).
- Archivos que no existen en disco (rutas de otro contexto, URLs).

## Instalación

`/router:instalar` **pide confirmación explícita** antes de tocar nada: modifica configuración
del proyecto del usuario.

```bash
# 1. Verificar dependencias
command -v jq   >/dev/null || echo "falta jq — el guard se auto-desactiva sin él"
command -v python3 >/dev/null || echo "falta python3 — los extractores no corren"

# 2. Merge en .claude/settings.json (no sobrescribir: puede haber otros hooks)
mkdir -p .claude
python3 - <<'PY'
import json, os, pathlib
p = pathlib.Path(".claude/settings.json")
cfg = json.loads(p.read_text()) if p.exists() else {}
entry = {"matcher": "Read|Bash", "hooks": [{"type": "command",
         "command": "$CLAUDE_PROJECT_DIR/qa-router-skill/hooks/qa-router-guard.sh"}]}
pre = cfg.setdefault("hooks", {}).setdefault("PreToolUse", [])
if not any("qa-router-guard" in json.dumps(h) for h in pre):
    pre.append(entry)
p.write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + "\n")
print(f"hook registrado en {p}")
PY

# 3. Permisos de ejecución
chmod +x qa-router-skill/hooks/qa-router-guard.sh qa-router-skill/extractors/diff_digest.sh

# 4. Ignorar el ledger en git
grep -q '^\.qa-router/' .gitignore 2>/dev/null || echo '.qa-router/' >> .gitignore
```

Si la skill se instaló fuera del repo (por ejemplo con `npx skills add`), exportar
`QA_ROUTER_HOME=<ruta real>` — el guard la usa para construir el comando sugerido.

## Verificación

```bash
export CLAUDE_PROJECT_DIR=$PWD
G=qa-router-skill/hooks/qa-router-guard.sh

# debe salir 2
echo '{"tool_name":"Read","tool_input":{"file_path":"resultados.jtl"}}' | bash $G; echo "exit=$?"

# debe salir 0
echo '{"tool_name":"Read","tool_input":{"file_path":"README.md","limit":50}}' | bash $G; echo "exit=$?"
```

## Escape hatch

| Necesidad | Cómo |
|---|---|
| Leer un archivo grande esta vez | `QA_ROUTER_OFF=1` en el comando |
| Trabajar con archivos largos toda la sesión | `QA_ROUTER_MIN_LINES=2000` |
| Desactivar el router del todo | `/router:off`, o quitar la entrada de `.claude/settings.json` |

Nunca editar el guard para desbloquear un caso puntual: si un patrón está mal, se corrige el
matcher y se documenta; si es una excepción de una vez, es para eso el escape hatch.

## Troubleshooting

| Síntoma | Causa | Fix |
|---|---|---|
| No bloquea nada | Falta `jq`, o el hook no quedó registrado | `command -v jq` y revisar `.claude/settings.json` |
| El comando sugerido apunta a una ruta inexistente | La skill no está en `$CLAUDE_PROJECT_DIR/qa-router-skill` | Exportar `QA_ROUTER_HOME` |
| Bloquea un archivo de datos legítimo (fixture `.csv` grande) | Supera el umbral de líneas | Subir `QA_ROUTER_MIN_LINES` para la sesión |
| Bloquea dentro de un script propio | El guard ve el `cat` del script | El script no pasa por `Bash` del agente si se corre desde otro proceso; si molesta, `QA_ROUTER_OFF=1` en el entorno del script |
| El agente entra en bucle reintentando | Está reintentando la misma lectura cruda | El mensaje ya trae la alternativa; si insiste, decirlo explícito: "usá `/router:digest`" |
