#!/usr/bin/env bash
# qa-router — PreToolUse guard.
#
# Bloquea la lectura cruda de artefactos QA pesados y redirige al extractor
# tier 0 correspondiente. Es la única capa que no se erosiona en sesiones
# largas: una regla escrita en un SKILL.md es una sugerencia, un bloqueo no.
#
# Contrato de hook de Claude Code:
#   stdin  = JSON con .tool_name y .tool_input
#   exit 0 = permitir · exit 2 = bloquear (stderr va al modelo)
#   cualquier otro exit = error del hook, no bloquea
#
# Escape hatch:
#   QA_ROUTER_OFF=1              desactiva el guard por completo
#   QA_ROUTER_MIN_LINES=<n>      umbral de líneas (default 400)
set -uo pipefail

[ "${QA_ROUTER_OFF:-0}" = "1" ] && exit 0

MIN_LINES="${QA_ROUTER_MIN_LINES:-400}"
SKILL_DIR="${QA_ROUTER_HOME:-$CLAUDE_PROJECT_DIR/qa-router-skill}"
DIGEST="$SKILL_DIR/extractors/router_digest.py"

IN=$(cat)
command -v jq >/dev/null 2>&1 || exit 0   # sin jq no se puede inspeccionar: no bloquear

TOOL=$(printf '%s' "$IN" | jq -r '.tool_name // empty')
TARGET=""

case "$TOOL" in
  Read)
    TARGET=$(printf '%s' "$IN" | jq -r '.tool_input.file_path // empty')
    # Read con offset+limit es lectura acotada: ya es el comportamiento deseado.
    LIMIT=$(printf '%s' "$IN" | jq -r '.tool_input.limit // empty')
    [ -n "$LIMIT" ] && exit 0
    ;;
  Bash)
    CMD=$(printf '%s' "$IN" | jq -r '.tool_input.command // empty')
    # Solo interesan los volcados completos. Un grep/wc/head acotado pasa.
    TARGET=$(printf '%s' "$CMD" \
      | grep -oE '(^|[|;&] *)(cat|jq [^|;&]*) +[^ |;&<>]+\.(json|jtl|xml|jmx|csv|har)' \
      | awk '{print $NF}' | head -1)
    ;;
  *) exit 0 ;;
esac

[ -n "$TARGET" ] || exit 0
[ -f "$TARGET" ] || exit 0

BASE=$(basename "$TARGET")
SIZE=$(wc -c < "$TARGET" 2>/dev/null | tr -d ' ')

# 1. Artefactos QA conocidos: bloqueados sin importar el tamaño — hay extractor exacto.
case "$BASE" in
  *.jtl|*.jmx|*postman_collection.json|*newman*.json|*junit*.xml|*TestResult.xml|*.har)
    {
      echo "BLOQUEADO por qa-router: '$TARGET' ($SIZE B) es un artefacto QA con extractor tier 0."
      echo "Corré en su lugar:  python3 $DIGEST \"$TARGET\""
      echo "Devuelve el contenido accionable — el 100% de los fallos cuando los hay — en ~50 líneas."
      echo "Si el extractor falla (exit 3), delegá al subagente qa-bulk-reader."
      echo "Bypass puntual: QA_ROUTER_OFF=1"
    } >&2
    exit 2 ;;
esac

# 2. Cualquier otro archivo de texto por encima del umbral de líneas.
LINES=$(wc -l < "$TARGET" 2>/dev/null | tr -d ' ')
if [ -n "$LINES" ] && [ "$LINES" -gt "$MIN_LINES" ] 2>/dev/null; then
  {
    echo "BLOQUEADO por qa-router: '$TARGET' tiene $LINES líneas (umbral $MIN_LINES)."
    echo "Opciones, en orden de preferencia:"
    echo "  1. python3 $DIGEST \"$TARGET\"   (si tiene extractor tier 0)"
    echo "  2. delegá al subagente qa-bulk-reader — el archivo no entra a este contexto"
    echo "  3. Read con offset/limit si ya sabés la línea exacta (de un Grep previo)"
    echo "Bypass puntual: QA_ROUTER_OFF=1 · subir umbral: QA_ROUTER_MIN_LINES=$((LINES + 1))"
  } >&2
  exit 2
fi

exit 0
