# Guía de uso — qa-router-skill

## En una línea

Antes de leer cualquier archivo de resultados de una herramienta de testing, pasalo por el
extractor. El crudo no entra al contexto.

---

## 1. Digerir un artefacto

El dispatcher detecta el tipo solo:

```bash
python3 extractors/router_digest.py results/R_CARGA.jtl
python3 extractors/router_digest.py reports/newman-results.json
python3 extractors/router_digest.py results/TestResult.xml
python3 extractors/router_digest.py --list        # ver tipos soportados
```

O el extractor directo, cuando querés sus opciones:

```bash
# JMeter, comparando contra una corrida baseline
python3 extractors/jtl_digest.py results/R_CARGA.jtl \
  --baseline results/R_BASELINE.jtl --top 20

# Newman, incluyendo también los requests que pasaron
python3 extractors/newman_digest.py reports/newman-results.json --all

# OpenAPI del sandbox, solo los endpoints del grupo
python3 extractors/openapi_digest.py openapi.json --tag pagos
python3 extractors/openapi_digest.py openapi.json --grep sql --schemas

# Colección Postman con el nombre de cada pm.test()
python3 extractors/collection_digest.py C_PAGOS_API.postman_collection.json --tests

# Azure DevOps proyectando campos puntuales
python3 extractors/az_digest.py runs.json --fields id,state,result,createdDate

# Diff de un PR — rutas y hunks, sin una sola línea de contenido
extractors/diff_digest.sh main..HEAD
extractors/diff_digest.sh --file pr-8801.diff
```

### Si el extractor sale 3

Significa "no reconozco este formato". El mensaje de stderr dice por qué. Dos salidas:

1. Corregir el origen — el caso más común es un `.jtl` escrito en XML en vez de CSV
   (reconfigurar el Simple Data Writer, ver `jmeter-skill`).
2. Delegar a tier 1: el subagente `qa-bulk-reader`.

Lo que **no** hay que hacer es leer el crudo "porque el extractor falló".

---

## 2. Activar el bloqueo

```
/router:instalar
```

Pide confirmación (modifica `.claude/settings.json`), hace merge idempotente y no pisa hooks
existentes. A partir de ahí, intentar leer un `.jtl` crudo devuelve un bloqueo con el comando
correcto en el mismo mensaje.

Verificación manual:

```bash
export CLAUDE_PROJECT_DIR=$PWD
echo '{"tool_name":"Read","tool_input":{"file_path":"results/R_CARGA.jtl"}}' \
  | bash qa-router-skill/hooks/qa-router-guard.sh; echo "exit=$?"   # esperado: 2
```

Si molesta en algún momento:

```bash
QA_ROUTER_OFF=1 <comando>          # solo esta vez
export QA_ROUTER_MIN_LINES=2000    # toda la sesión
/router:off                        # apagar el router
```

---

## 3. Delegar a tier 1

Cuando no hay extractor y el archivo es grande:

```
/router:leer "e2e/**/*.spec.ts"
```

Invoca `qa-bulk-reader` (haiku, contexto aislado). Vuelven bullets con `nombre · L<línea>`, no
el contenido. Con esas líneas después se puede leer puntual con `offset`/`limit`.

Para boilerplate:

```
/router:escribir "agregar request DELETE /payments/{id} con verificación en BD" \
  --reference C_PAGOS_API.postman_collection.json
```

**Sin `--reference` no genera nada.** Es deliberado: es la regla que evita que un modelo barato
invente convenciones que el repo no usa.

---

## 4. Medir el ahorro

```bash
python3 extractors/ledger_report.py            # acumulado
python3 extractors/ledger_report.py --reset    # arrancar una medición limpia
```

```
QA-ROUTER · COSTO · .qa-router/ledger.jsonl
ARTEFACTO               N      CRUDO     DIGEST  REDUCCIÓN
jmeter-jtl              1    59.2 KB      766 B      98.7%
newman                  1     2.0 KB      674 B      67.5%
TOTAL                   2    61.2 KB     1.4 KB      97.7%

TOKENS EVITADOS (est. bytes/4): ~15,312 — estimación, no medición.
```

Para un baseline honesto, correr el mismo flujo dos veces —una con `QA_ROUTER_OFF=1`, otra sin—
y publicar el par de números. Ver `references/cost-ledger-schema.md`.

---

## 5. Flujo típico, de punta a punta

```bash
# 1. Corrida de rendimiento
jmeter -n -t P_SANDBOX_API.jmx -l results/R_CARGA.jtl -Jperfil=carga

# 2. Digerir (el crudo nunca entra al contexto)
python3 extractors/jtl_digest.py results/R_CARGA.jtl --baseline results/R_BASELINE.jtl

# 3. El agente decide sobre el digest — tier 2, que es donde tiene sentido gastar
#    "p95 subió 167ms y aparecieron 500 en POST /payments. ¿Regresión o carga?"

# 4. Profundizar puntual, sin cargar todo
grep -n "500" results/R_CARGA.jtl | head -5

# 5. Ver cuánto se ahorró
python3 extractors/ledger_report.py
```

---

## Problemas frecuentes

| Síntoma | Fix |
|---|---|
| `exit 3` sobre un archivo válido | El stderr dice el formato esperado. Si es correcto igual, delegar a `qa-bulk-reader` |
| El hook no bloquea nada | Falta `jq` (el guard se auto-desactiva) o el hook no quedó en `.claude/settings.json`. `/router:estado` lo diagnostica |
| El hook bloquea un fixture legítimo | `QA_ROUTER_MIN_LINES=<n>` para la sesión. No editar el guard |
| Faltan fallos en el digest | Los clusters se cortaron por `QA_ROUTER_MAX_CLUSTERS`; la línea "… N clusters más" lo declara. Subir la variable |
| `/router:costo` dice que no hay ledger | No se corrió ningún extractor todavía, o `QA_ROUTER_LEDGER=off` |
| El comando sugerido apunta a una ruta que no existe | La skill se instaló fuera del repo: `export QA_ROUTER_HOME=<ruta real>` |
