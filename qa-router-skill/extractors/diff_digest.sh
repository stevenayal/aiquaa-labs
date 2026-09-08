#!/usr/bin/env bash
# Diff de PR → rutas, extensiones y cabeceras de hunk. Sin cuerpos. Tier 0.
#
# Uso:
#   diff_digest.sh <base>..<head>      # rango git
#   diff_digest.sh --file <patch.diff> # patch ya guardado en disco
#   diff_digest.sh                     # working tree vs HEAD
#
# Alimenta el scoring determinístico de qa-orchestrator-skill sin que el diff
# entre al contexto caro.
set -euo pipefail

SRC="working tree"
if [ "${1:-}" = "--file" ]; then
  [ -f "${2:-}" ] || { echo "qa-router: no existe '${2:-}'" >&2; exit 2; }
  DIFF=$(cat "$2"); SRC="$2"
elif [ -n "${1:-}" ]; then
  DIFF=$(git diff "$1"); SRC="$1"
else
  DIFF=$(git diff HEAD)
fi

[ -n "$DIFF" ] || { echo "DIFF · $SRC · sin cambios"; exit 0; }

RAW_BYTES=$(printf '%s' "$DIFF" | wc -c | tr -d ' ')

echo "DIFF · $SRC · $(date -u +%Y-%m-%dT%H:%MZ)"

# Conteo por archivo (+/-) sin imprimir una sola línea de contenido.
STAT=$(printf '%s\n' "$DIFF" | git apply --numstat - 2>/dev/null || true)
if [ -z "$STAT" ]; then
  STAT=$(printf '%s\n' "$DIFF" | awk '
    /^\+\+\+ b\// { f=substr($0,7); add[f]=add[f]+0 }
    /^\+/ && !/^\+\+\+/ { add[f]++ }
    /^-/  && !/^---/    { del[f]++ }
    END { for (k in add) printf "%d\t%d\t%s\n", add[k], del[k], k }')
fi

FILES=$(printf '%s\n' "$STAT" | grep -c . || true)
echo "ARCHIVOS: ${FILES:-0}"
printf '%s\n' "$STAT" | while IFS=$'\t' read -r a d f; do
  [ -n "${f:-}" ] || continue
  if [ "${a:-0}" = "-" ]; then
    printf '  %s · binario\n' "$f"
  else
    printf '  %s · +%s/-%s\n' "$f" "${a:-0}" "${d:-0}"
  fi
done

echo "EXTENSIONES:"
printf '%s\n' "$STAT" | awk -F'\t' '{n=split($3,p,"."); if (n>1) print "."p[n]; else print "(sin ext)"}' \
  | sort | uniq -c | sort -rn | awk '{printf "  %s ×%s\n", $2, $1}'

echo "HUNKS:"
printf '%s\n' "$DIFF" | awk '
  /^\+\+\+ b\// { f=substr($0,7) }
  /^@@/ { c[f]++; if (c[f] <= 3) printf "  %s %s\n", f, $0 }
  END { }' | head -40

echo "CRUDO: $SRC (${RAW_BYTES} B)"

# Ledger (mismo formato que los extractores Python).
if [ "${QA_ROUTER_LEDGER:-}" != "off" ]; then
  LEDGER="${QA_ROUTER_LEDGER:-$PWD/.qa-router/ledger.jsonl}"
  mkdir -p "$(dirname "$LEDGER")" 2>/dev/null || true
  printf '{"ts":"%s","tier":0,"kind":"diff","source":"%s","bytes_raw":%s}\n' \
    "$(date -u +%Y-%m-%dT%H:%MZ)" "$SRC" "$RAW_BYTES" >> "$LEDGER" 2>/dev/null || true
fi
