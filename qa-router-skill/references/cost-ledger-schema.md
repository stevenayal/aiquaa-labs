# Ledger de costo

Registro de lo que el router evitó cargar. Alimenta `/router:costo`.

## Ubicación

`.qa-router/ledger.jsonl` en el directorio de trabajo. Se sobreescribe con `QA_ROUTER_LEDGER`;
`QA_ROUTER_LEDGER=off` lo desactiva. **Va al `.gitignore`** — es telemetría local, no un
artefacto del proyecto.

## Formato — una línea JSON por digest

```json
{"ts":"2026-09-07T17:53Z","tier":0,"kind":"jmeter-jtl","source":"R_EJEMPLO_carga.jtl",
 "bytes_raw":60621,"bytes_digest":766,"ratio":0.9874,"tokens_saved_est":14963,"ms":3}
```

| Campo | Significado |
|---|---|
| `ts` | UTC, minuto de resolución |
| `tier` | 0 (extractor) — tier 1 y 2 no se instrumentan todavía |
| `kind` | Tipo de artefacto (`jmeter-jtl`, `newman`, `junit`, `nunit`, `playwright`, `jmx`, `postman-collection`, `openapi`, `azure-devops`, `diff`) |
| `source` | Nombre del archivo (basename, no la ruta completa) |
| `bytes_raw` | Tamaño del artefacto crudo |
| `bytes_digest` | Tamaño del digest emitido |
| `ratio` | `1 - digest/raw` |
| `tokens_saved_est` | `(raw - digest) / 4` |
| `ms` | Duración del extractor |

## La estimación de tokens

`bytes ÷ 4` es una **aproximación declarada**, no una medición del tokenizer. Sirve para
comparar artefactos entre sí y ver el orden de magnitud; no sirve para conciliar contra el
consumo facturado. `ledger_report.py` lo dice en su salida, y cualquier informe que use estos
números debe repetirlo.

Para JSON y XML muy repetitivos la relación real de bytes por token es más alta que 4, así que
la estimación tiende a **subestimar** el ahorro. Se prefiere subestimar.

## Lo que el ledger no mide

- Tokens de razonamiento de tier 2 — el grueso de una sesión QA, y no cambia con el router.
- Costo de los subagentes tier 1 (tienen su propio consumo, menor pero no cero).
- Lo que se habría leído si el router no existiera: el ledger cuenta lo que **sí** se digirió,
  no las lecturas crudas que el hook evitó. El ahorro real es mayor que el registrado.

Por eso el número honesto de sesión completa es **40–70%**, no el 95%+ que muestran los
artefactos individuales.

## Baseline reproducible

```bash
# sin router
QA_ROUTER_OFF=1 QA_ROUTER_LEDGER=off  <flujo>
# con router
python3 extractors/ledger_report.py --reset
<mismo flujo>
python3 extractors/ledger_report.py
```

Correr ambos sobre el mismo input (por ejemplo `qa-orchestrator-skill/examples/PR_DIFF_MIXTO.md`
más una corrida de Newman y una de JMeter) y publicar el par de números, nunca uno solo.
