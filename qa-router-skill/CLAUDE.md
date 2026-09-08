# qa-router-skill — CLAUDE.md

## Project

Router de consumo del stack `aiquaa-labs`. Implementa el patrón *shunt* (relevado en
`docs/router-qa-relevamiento.md`, raíz del repo) en versión nativa: sin proveedores externos y
sin servidores MCP. Decide en qué **tier de costo** corre cada operación y digiere artefactos
QA pesados a resúmenes de ~50 líneas antes de que entren al contexto caro.

## Structure

```
skills/qa-router/   ← skill principal (tabla de tiers, comandos, boundaries)
references/         ← routing-policy.md (tabla completa), digest-contracts.md (formato de
                       salida, estable — otras skills lo parsean), hooks-setup.md,
                       cost-ledger-schema.md
agents/             ← 4 subagentes tier 1 (model: haiku), cada uno con su contrato de salida
extractors/         ← 10 extractores tier 0, solo stdlib de Python 3 + bash
hooks/              ← qa-router-guard.sh (PreToolUse) + settings.example.json
examples/           ← fixtures: .jtl con fallos + baseline, newman, junit, playwright, openapi
test/               ← test_extractors.sh — 23 asserts sobre extractores, dispatcher, guard y ledger
docs/               ← guía de uso en español
```

## Key rules

- **Tres tiers, por costo y no por tema.** Tier 0 = extractor determinístico (0 tokens de
  LLM); tier 1 = subagente `haiku` con contexto aislado; tier 2 = sesión principal. La
  ventaja de QA sobre el patrón original: los artefactos pesados son máquina-parseables, así
  que el worker barato casi siempre es un script, no un modelo.
- **Ningún proveedor externo.** No se agrega Gemini/OpenAI/Portal ni se instala MCP. Si una
  propuesta requiere un proveedor externo, no entra en esta skill.
- **Códigos de salida como contrato:** `0` digest OK · `2` uso/archivo inexistente ·
  `3` formato no reconocido → delegar a tier 1. Un extractor **nunca** imprime un digest
  parcial: si el parseo falla a mitad, sale 3 sin emitir nada.
- **Los digests conservan el 100% de los fallos**, agrupados en clusters con conteo. El tope
  `QA_ROUTER_MAX_CLUSTERS` limita la variedad impresa, nunca el total — y cuando corta lo
  declara en una línea explícita. Se comprime prosa, jamás sustancia técnica (mismo límite que
  `caveman`).
- **Todo digest termina en `CRUDO: <ruta> (<tamaño>)`.** Nunca es un callejón sin salida.
- **El hook es la única capa que no se erosiona.** Bloquea con `exit 2` y en el mismo mensaje
  nombra el comando permitido. Sin `jq` se auto-desactiva: el guard nunca rompe una sesión.
  El escape hatch (`QA_ROUTER_OFF=1`, `QA_ROUTER_MIN_LINES`) no es opcional.
- **`/router:instalar` pide confirmación explícita** — modifica `.claude/settings.json` del
  usuario. El merge es idempotente y preserva hooks y `env` preexistentes.
- **`qa-code-writer` sin `--reference` no genera nada.** Es la regla que evita que un modelo
  barato invente convenciones; no tiene excepción.
- **Lo que nunca baja de tier 2:** edición por número de línea, semántica de asserts y valores
  esperados, diagnóstico de causa raíz, ruteo ambiguo, veredictos, gates human-in-the-loop, y
  qué hacer ante un secreto (el *match* es tier 0, la decisión es tier 2).
- **El ahorro en tokens del ledger es una estimación (bytes ÷ 4), no una medición.** Se
  reporta siempre como tal. Artefactos: 95–99%. Sesión completa: 40–70%, porque el
  razonamiento sigue en tier 2.
- **No compite con las otras skills:** `qa-orchestrator` decide *qué* probar, `qa-router`
  *quién ejecuta y a qué costo*, `caveman` *cómo se ve la salida*, `token-optimization` los
  hábitos del operador. Esa separación se repite en los `Boundaries` de cada una.
- **Sin dependencias nuevas.** Los extractores usan solo la stdlib (`json`, `csv`, `array`,
  `xml.etree`). Nada de pandas: `jtl_digest.py` recorre el `.jtl` en streaming con
  `array('l')`, ~4 bytes por muestra, porque un `.jtl` real puede pesar cientos de MB.
- `docs/uso.md` va en español (convención del repo); el código y los mensajes de error también.

## Tests

```bash
bash qa-router-skill/test/test_extractors.sh   # 23 asserts, sin dependencias
```

La suite corre contra fixtures propios **y** contra artefactos reales de otras skills del repo
(`jmeter-skill`, `postman-newman-skill`, `flaui-skill`, `qa-productivity-skill`) — si esas
skills cambian sus formatos de ejemplo, la suite lo detecta.
