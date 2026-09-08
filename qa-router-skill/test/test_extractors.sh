#!/usr/bin/env bash
# Suite del qa-router. Corre los extractores contra los fixtures y verifica los
# invariantes de references/digest-contracts.md. Sin dependencias externas.
#
# Uso: bash test/test_extractors.sh   (desde qa-router-skill/)
set -uo pipefail
cd "$(dirname "$0")/.."

export QA_ROUTER_LEDGER="${TMPDIR:-/tmp}/qa-router-test-ledger.jsonl"
rm -f "$QA_ROUTER_LEDGER"
E=extractors
X=examples
PASS=0
FAIL=0

ok()   { PASS=$((PASS+1)); printf '  ok   %s\n' "$1"; }
bad()  { FAIL=$((FAIL+1)); printf '  FAIL %s\n' "$1"; }

# assert_digest <nombre> <salida> <exit> <patrón obligatorio>...
assert_digest() {
  local name=$1 out=$2 code=$3; shift 3
  [ "$code" = "0" ] || { bad "$name — exit $code (esperado 0)"; return; }
  grep -q '^CRUDO: ' <<<"$out" || { bad "$name — falta línea CRUDO"; return; }
  local pat
  for pat in "$@"; do
    grep -qE "$pat" <<<"$out" || { bad "$name — falta patrón: $pat"; return; }
  done
  ok "$name"
}

# assert_exit <nombre> <esperado> <comando...>
assert_exit() {
  local name=$1 want=$2; shift 2
  "$@" >/dev/null 2>&1
  local got=$?
  [ "$got" = "$want" ] && ok "$name (exit $got)" || bad "$name — exit $got, esperado $want"
}

echo "== extractores tier 0 =="

OUT=$(python3 $E/newman_digest.py $X/newman-results.json); C=$?
assert_digest "newman" "$OUT" "$C" '^NEWMAN · ' '^TOTALES: .*fallos' '^FALLOS \(5\):' 'status is 201'

OUT=$(python3 $E/jtl_digest.py $X/R_EJEMPLO_carga.jtl --baseline $X/R_EJEMPLO_baseline.jtl); C=$?
assert_digest "jtl" "$OUT" "$C" '^JMETER · ' '^MUESTRAS: 600 ' 'p95 [0-9]+' '^ERRORES \(20 ' '^VS BASELINE'

OUT=$(python3 $E/junit_digest.py $X/junit-results.xml); C=$?
assert_digest "junit" "$OUT" "$C" '^JUNIT · ' '^TOTALES: 12 casos' '^FALLOS \(3\):'

OUT=$(python3 $E/junit_digest.py ../flaui-skill/examples/fixtures/sample_TestResult.xml); C=$?
assert_digest "nunit (fixture de flaui-skill)" "$OUT" "$C" '^NUNIT · ' '^FALLOS \(1\):' 'RF-002'

OUT=$(python3 $E/pw_digest.py $X/playwright-report.json); C=$?
assert_digest "playwright" "$OUT" "$C" '^PLAYWRIGHT · ' '^FALLOS \(2\):' '^FLAKY: '

OUT=$(python3 $E/jmx_digest.py ../jmeter-skill/examples/P_SANDBOX_API.jmx); C=$?
assert_digest "jmx (plan de jmeter-skill)" "$OUT" "$C" '^JMX · ' '^THREAD GROUPS:' '^SAMPLERS:' '^ASSERTIONS: '

OUT=$(python3 $E/collection_digest.py ../postman-newman-skill/examples/C_EXAMPLE_API.json); C=$?
assert_digest "postman (colección de postman-newman-skill)" "$OUT" "$C" '^POSTMAN · ' '^ÁRBOL:' 'test\(s\)'

OUT=$(python3 $E/openapi_digest.py $X/openapi.json --tag pagos); C=$?
assert_digest "openapi --tag" "$OUT" "$C" '^OPENAPI · ' '^ENDPOINTS: 3 de 5'

OUT=$(python3 $E/az_digest.py ../qa-productivity-skill/examples/az-test-runs-results.json); C=$?
assert_digest "azure devops" "$OUT" "$C" '^AZURE DEVOPS · ' 'inestable'

echo "== dispatcher =="
OUT=$(python3 $E/router_digest.py $X/newman-results.json); C=$?
assert_digest "dispatch → newman" "$OUT" "$C" '^NEWMAN · '
OUT=$(python3 $E/router_digest.py $X/R_EJEMPLO_carga.jtl); C=$?
assert_digest "dispatch → jtl" "$OUT" "$C" '^JMETER · '
assert_exit "dispatch archivo inexistente → 2" 2 python3 $E/router_digest.py no-existe.json
assert_exit "dispatch sin extractor → 3"       3 python3 $E/router_digest.py ../README.md
assert_exit "formato equivocado → 3"           3 python3 $E/newman_digest.py $X/openapi.json

echo "== guard (PreToolUse) =="
export CLAUDE_PROJECT_DIR="$PWD/.."
G=hooks/qa-router-guard.sh
guard() { printf '%s' "$1" | bash $G >/dev/null 2>&1; echo $?; }
[ "$(guard '{"tool_name":"Read","tool_input":{"file_path":"examples/R_EJEMPLO_carga.jtl"}}')" = "2" ] \
  && ok "bloquea Read de .jtl" || bad "bloquea Read de .jtl"
[ "$(guard '{"tool_name":"Bash","tool_input":{"command":"cat examples/newman-results.json"}}')" = "2" ] \
  && ok "bloquea cat de newman json" || bad "bloquea cat de newman json"
[ "$(guard '{"tool_name":"Read","tool_input":{"file_path":"examples/R_EJEMPLO_carga.jtl","limit":50}}')" = "0" ] \
  && ok "permite Read acotado (limit)" || bad "permite Read acotado (limit)"
[ "$(guard '{"tool_name":"Bash","tool_input":{"command":"grep -c 500 examples/R_EJEMPLO_carga.jtl"}}')" = "0" ] \
  && ok "permite grep acotado" || bad "permite grep acotado"
[ "$(guard '{"tool_name":"Edit","tool_input":{"file_path":"examples/R_EJEMPLO_carga.jtl"}}')" = "0" ] \
  && ok "no interfiere con Edit" || bad "no interfiere con Edit"
[ "$(QA_ROUTER_OFF=1 guard '{"tool_name":"Read","tool_input":{"file_path":"examples/R_EJEMPLO_carga.jtl"}}')" = "0" ] \
  && ok "escape hatch QA_ROUTER_OFF" || bad "escape hatch QA_ROUTER_OFF"

# Sin jq el guard debe permitir, nunca romper la sesión. PATH aislado con lo mínimo.
BIN=$(mktemp -d)
for b in bash cat grep awk wc basename head tr sed dirname; do
  SRC=$(command -v "$b") && ln -sf "$SRC" "$BIN/$b"
done
NOJQ=$(printf '%s' '{"tool_name":"Read","tool_input":{"file_path":"examples/R_EJEMPLO_carga.jtl"}}' \
  | PATH="$BIN" bash $G >/dev/null 2>&1; echo $?)
[ "$NOJQ" = "0" ] && ok "sin jq el guard permite (no rompe la sesión)" \
  || bad "sin jq el guard salió $NOJQ, esperado 0"
rm -rf "$BIN"

echo "== ledger =="
LINES=$(wc -l < "$QA_ROUTER_LEDGER" 2>/dev/null | tr -d ' ')
[ "${LINES:-0}" -ge 9 ] && ok "ledger registró $LINES digests" || bad "ledger tiene ${LINES:-0} líneas (esperado ≥9)"
python3 $E/ledger_report.py "$QA_ROUTER_LEDGER" | grep -q '^TOTAL' \
  && ok "ledger_report imprime TOTAL" || bad "ledger_report imprime TOTAL"
RATIO=$(python3 -c "
import json,sys
rows=[json.loads(l) for l in open('$QA_ROUTER_LEDGER') if l.strip()]
jtl=[r for r in rows if r['kind']=='jmeter-jtl'][0]
print(1 if jtl['ratio']>0.95 else 0)")
[ "$RATIO" = "1" ] && ok "reducción del .jtl > 95%" || bad "reducción del .jtl > 95%"

echo
echo "RESULTADO: $PASS ok · $FAIL fallos"
rm -f "$QA_ROUTER_LEDGER"
[ "$FAIL" -eq 0 ]
