---
name: qa-orchestrator
description: >
  Analiza un Pull Request (diff, archivos cambiados, descripción) y/o una
  historia de usuario/requerimiento, decide qué skill(s) del stack aiquaa
  aplican (puede ser más de una — API, web, escritorio, BD, rendimiento,
  BDD), las invoca en secuencia para generar y correr la automatización, y
  entrega un informe consolidado + bitácora de decisión auditable. Nunca
  adivina en casos ambiguos — pregunta. Nunca abre el PR final — delega
  siempre a course-pr-skill con confirmación explícita.
  Usar cuando el usuario mencione "qué skill uso", "analizá este PR",
  "orquestar pruebas", "decidí qué automatizar", "route this PR", pegue un
  número de PR junto con una historia de usuario, o pida automatizar "todo
  lo que toque este PR/esta historia".
  Auto-activa para cualquier flujo de ruteo multi-skill: análisis,
  generación combinada, ejecución o consolidación de resultados.
---

QA router. Claude read PR+historia, score signals, pick skill(s), ask if unsure. Terse output. No fluff.

---

## ¿Qué es esta skill?

El stack `aiquaa-labs` tiene 10 skills QA independientes (bdd, postman-newman, hurl,
playwright, jmeter, flaui, database-object-testing, ocr-bdd, sandbox, course-pr). Hasta ahora,
elegir cuál usar para un PR o una historia de usuario era una decisión manual, mirando la
tabla "¿Cuál usar?" del README raíz. Esta skill automatiza esa decisión: lee el contexto
(PR y/o historia), lo puntúa contra un mapa de señales determinístico, decide qué skill(s)
aplican — puede ser más de una si el cambio toca varias capas — las invoca en orden para
generar y correr la automatización, y entrega un resultado consolidado y auditable.

**No reemplaza a las 10 skills** — las orquesta. No genera `.feature`, `.spec.ts` ni `.jmx`
directamente: lee el `SKILL.md` de cada skill seleccionada y sigue su flujo documentado.

No cubre: elegir el skill por vos sin poder explicar por qué (toda decisión queda en la
bitácora), ni abrir el PR final (eso es siempre `course-pr-skill`, con confirmación).

---

## Comandos

| Comando | Acción |
|---------|--------|
| `/qa:analizar <PR#\|diff\|historia>` | Intake + escaneo de secretos + clasificación determinística + gate si es ambiguo. Escribe/actualiza `BITACORA_*.md`. |
| `/qa:generar` | Invoca, en orden, cada skill seleccionada para generar sus artefactos — reusa el contexto ya extraído, no repregunta. |
| `/qa:ejecutar` | Corre cada suite generada, verificando prerrequisitos antes de cada una. |
| `/qa:consolidar` | Agrega los reportes nativos de cada skill en `INFORME_CONSOLIDADO_*.md` y cierra la bitácora. |
| `/qa:orquestar` | Flujo completo `analizar → generar → ejecutar → consolidar`, respetando los gates intermedios. Punto de entrada más común. |
| `/qa:entregar` | Arma el resumen final y **siempre** delega a `course-pr-skill` (`/curso:entregar`) — nunca abre el PR por su cuenta. |

---

## Context Intake — SIEMPRE ejecutar primero

1. **¿PR (número + plataforma) o diff pegado directamente?** Si es número: detectar
   plataforma igual que `course-pr-skill` (`git remote get-url origin` → `github.com` = `gh`,
   `dev.azure.com`/`visualstudio.com` = `az repos`).
2. **¿Historia de usuario en texto plano, o documento (PDF/imagen/captura)?** Si es
   documento, no leerlo a ojo — activar `ocr-bdd-skill` primero y esperar su salida
   confirmada antes de clasificar.
3. **¿Repo objetivo?** Si no se especifica, asumir el repo actual.
4. Si el contexto referencia `x-api-key`, `aiquaa-sandbox-api`, `qa_training` o "grupo N":
   cargar `sandbox-skill` como contexto compartido — no compite como candidata puntuada, es
   la base que las demás consultan para no inventar endpoints/campos/tablas.
5. **Nunca generar nada** hasta completar `/qa:analizar` y resolver cualquier gate de
   ambigüedad o secretos pendiente.

---

## Paso 0 — Escaneo de secretos (siempre, antes de leer nada más)

Mismo patrón que `course-pr-skill`, corrido sobre el diff del PR o el texto pegado, **al
inicio de `/qa:analizar`** — no solo al final en la entrega:

```bash
grep -lE "sbx_[a-z0-9_]+|postgres(ql)?://[^/]*:[^/]*@|Bearer [A-Za-z0-9._-]{20,}" <<< "$DIFF_O_TEXTO"
```

Si algo aparece: **detener el pipeline completo**, mostrar el archivo/línea, no seguir a
clasificación ni generación hasta que esté resuelto. Se registra en la bitácora como
`ESTADO FINAL: bloqueado (secretos)`.

---

## Clasificación — señal → skill (determinística primero)

Tabla condensada — versión completa con todos los pesos y ejemplos en
`references/signal-mapping.md`. Regla general: **reglas primero, LLM después.** Un grep de
rutas/extensiones sobre el diff y de keywords sobre la historia decide en la mayoría de los
casos. El juicio del modelo se usa solo para desempatar los casos "Media"/"Ambigua" (ver
tabla de confianza más abajo) — nunca como clasificador primario.

| Señal en el PR (ruta/extensión) | Señal en la historia (keyword) | Skill candidata | Peso ruta / keyword |
|---|---|---|---|
| `**/*.feature`, `**/*.steps.ts`, `world.ts`, `hooks.ts`, `cucumber.js` | Given/Cuando/Entonces, "criterios de aceptación", `@grupo-N` | `bdd-skill` | 15 / 8 |
| Adjunto es PDF/imagen/captura de pantalla | ídem | `ocr-bdd-skill` — **preprocesador bloqueante**, corre antes de puntuar el resto | 20, no compite por capa |
| `**/*.postman_collection.json`, `C_*.json`, `E_*.json`, `newman-reporter*` en `package.json` | "Postman", "colección", "Newman", "GUI-first" | `postman-newman-skill` | 15 / 8 |
| `**/*.hurl`, `H_*.hurl`, `V_*.env` | "Hurl", "texto plano", "diff-friendly", "Azure Test Plans nativo" | `hurl-skill` | 15 / 8 |
| `src/components/**/*.{tsx,jsx,vue,html}`, `**/*.spec.ts` bajo `e2e/`/`tests/ui`, `pages/*Page.ts`, `playwright.config.ts`, `data-testid` nuevo/cambiado | "navegador", "E2E", "Playwright", "flujo de usuario", "pantalla web", "checkout" | `playwright-skill` | 15 / 8 |
| `**/*.jmx`, `P_*.jmx`, `D_*.csv` en contexto perf, `V_PERFILES.properties` | "rendimiento", "carga", "estrés", "usuarios concurrentes", "SLA", "p95/p99", "throughput", "escalabilidad" | `jmeter-skill` | 15 / 8 |
| `**/*.Designer.cs`, `**/*.xaml`, `.csproj` con `<UseWindowsForms>true` o `<UseWPF>true` | "escritorio", "WinForms", "WPF", "FlaUI" | `flaui-skill` | 15 / 8 |
| `migrations/**/*.sql`, `**/{views,procedures,functions,triggers}/*.sql`, `rules/*.md` (formato database-object-testing) | "vista", "procedimiento almacenado", "función SQL", "trigger", "objeto de base de datos", "comparar base vs candidata" | `database-object-testing-skill` | 15 / 8 |
| Referencia `x-api-key`/`aiquaa-sandbox-api`/`qa_training`/"grupo N" | ídem | `sandbox-skill` — contexto, no puntuada | n/a |
| — (siempre, al final del pipeline) | — | `course-pr-skill` — paso fijo, no puntuado | n/a |

**Desempate hurl vs postman-newman:** si ninguna extensión aparece en el diff (ambas quedan
en 8 o menos por solo keyword), preferir la herramienta cuyos archivos **ya existen** en el
repo objetivo (`.hurl` vs `postman_collection.json`). Si ninguna existe → empate genuino →
gate de confirmación.

### Niveles de confianza y fallback

| Puntaje | Nivel | Comportamiento |
|---|---|---|
| ≥ 15 (una señal de ruta/extensión exacta) | Alta | Auto-selecciona, procede a `/qa:generar`; igual queda listada en la bitácora. |
| 8–14 (solo señales de keyword, sin ruta/extensión) | Media | Se incluye en la lista pero se marca "confirmar" — una sola pregunta agrupada antes de generar. |
| Empate entre candidatas de la misma capa (diferencia ≤ 3 puntos) | Ambigua | Relectura más fina del diff/historia (no solo grep); si sigue sin resolverse, **preguntar al usuario explícitamente**, nunca adivinar. |
| Todas las skills en 0 | Sin señales | Detener el flujo, no generar nada, pedir al usuario que describa qué probar o señale archivos. |

El LLM entra recién en el caso "Ambigua" — como segunda pasada de lectura, nunca como filtro
inicial.

---

## Formato de salida — `/qa:analizar`

```
CONTEXTO DETECTADO:
  PR / HISTORIA:     <número + plataforma | resumen de la historia>
  ARCHIVOS:          <N archivos analizados en el diff, si aplica>
  ESCANEO SECRETOS:  <limpio | BLOQUEADO — ver detalle>
  SANDBOX:           <cargado como contexto | no aplica>

SEÑALES DETECTADAS:
  <skill> — <señal> (peso <N>)
  ...

DECISIÓN DE RUTEO:
  ✅ <skill> — confianza alta (puntaje <N>)
  ❓ <skill> — confianza media, confirmar (puntaje <N>)
  ⛔ <skill> descartada — <motivo>

¿Confirmás la selección o corregís algo antes de generar?
```

Esperar confirmación cuando hay ítems `❓`. Si todo es `✅`, se puede seguir directo a
`/qa:generar` sin preguntar de nuevo (la bitácora ya deja constancia de la decisión).

---

## Invocación de otras skills

Las Skills son prompt-based, no hay API invocable. Por cada skill seleccionada, en este orden
fijo: **skills de contexto primero** (`sandbox-skill`, `ocr-bdd-skill` si el intake lo activó),
**luego las de generación** en el orden en que fueron puntuadas, **`course-pr-skill` siempre
al final** (solo en `/qa:entregar`, nunca antes):

1. **Leer** el `SKILL.md` de la skill objetivo en `../<X>-skill/skills/<X>/SKILL.md` relativo
   a `qa-orchestrator-skill/` (excepción: `hurl-skill` tiene su `SKILL.md` en la raíz del
   paquete, `../hurl-skill/SKILL.md`).
2. Seguir su flujo documentado, usando el contexto ya extraído (archivos del diff, endpoints,
   grupo, requerimiento) para responder su propio "Context Intake" en vez de repreguntar al
   usuario lo que ya se sabe.
3. Correr los comandos que esa skill documenta, en el orden que su propio `SKILL.md`
   especifica, completando una skill antes de empezar la siguiente.
4. Registrar en la bitácora qué se leyó, qué se generó y qué se corrió (§ Bitácora).

Si la skill target ya tiene su propio flujo "desde PR" (ej. `flaui-skill` con
`/flaui:from-pr`), usarlo directamente en vez de reconstruir la lógica de diff — evita
duplicar lo que esa skill ya resuelve mejor con su propio analizador.

**Nota de riesgo:** esto asume que las skills instaladas quedan como carpetas hermanas
`<name>-skill/` (consistente con el Quickstart del README raíz, pero no verificado contra el
comportamiento real del CLI `skills`). Si la ruta relativa esperada no existe: preguntar la
ruta real de instalación, o invocar por el slash command público si la skill ya está activa
en la sesión — nunca asumir en silencio que no está disponible.

---

## Prerrequisitos por skill (antes de `/qa:generar` / `/qa:ejecutar`)

Tabla completa en `references/prerequisites-check.md`. Resumen:

| Skill | Check | Si falla |
|---|---|---|
| `playwright-skill` | ¿Existe frontend real (componentes/páginas) en el repo? | Omitir, reportar "no se encontró frontend — no se inventan selectores" |
| `flaui-skill` | ¿Existe `.csproj` con `<UseWindowsForms>true>` o `<UseWPF>true>`? | Omitir, reportar el motivo |
| `database-object-testing-skill` | ¿Gateway REST configurado (`DBTEST_*_URL`)? | Omitir — nunca cae a driver directo |
| `jmeter-skill` | ¿JMeter instalado? ¿Entorno destino confirmado no-producción? | Omitir ejecución (generación puede seguir), reportar |
| `hurl-skill` | ¿CLI `hurl` instalado? | Omitir solo `/qa:ejecutar`, no `/qa:generar` |
| `postman-newman-skill` | ¿Newman instalado? | Igual que arriba |
| `course-pr-skill` | Delegado a su propio pre-flight (paso 0 de `/curso:entregar`) | No se duplica lógica — se reporta lo que `course-pr-skill` reporte |

Regla dura: todo fallo de prerrequisito se reporta explícito en la bitácora — nunca se
traga en silencio ni se salta sin avisar.

---

## Bitácora de decisión — `BITACORA_<PR-o-historia>.md`

Formato completo en `references/decision-log-schema.md`. Cada corrida de `/qa:analizar`
escribe o actualiza este archivo con: encabezado (fecha, PR#/historia, hash de contenido para
idempotencia) → entradas analizadas → señales detectadas → puntajes por skill → decisión
(seleccionadas/descartadas/ambiguas y qué se preguntó/respondió) → prerrequisitos → ejecución
(comandos, archivos generados, resultado, ruta al reporte nativo) → confirmaciones humanas
(timestamp) → estado final.

**Idempotencia:** el hash del diff+historia permite que un segundo `/qa:analizar` sobre el
mismo contenido reutilice la decisión anterior ("hash sin cambios, reutilizando decisión
anterior") en vez de re-preguntar o re-generar. La generación además verifica si el archivo
destino ya existe antes de sobrescribir — mismo patrón "actualización quirúrgica" que
`/flaui:from-pr` usa para no regenerar toda la suite de cero.

---

## Informe consolidado — `INFORME_CONSOLIDADO_<NOMBRE>.md`

Formato completo en `references/consolidated-report-schema.md`. Markdown, no PDF — cada skill
hija ya produce su propio reporte nativo (PDF/JUnit/NUnit XML/cucumber JSON/JTL); este archivo
los agrega, no los reemplaza. Por cada skill invocada: veredicto propio (reusando su escala
nativa donde exista, ej. VERDE/VERDE CON GAPS/FALLOS MENORES/REGRESIÓN CRÍTICA de flaui) +
enlace/ruta al reporte nativo. **Veredicto global = el peor veredicto individual** entre las
skills invocadas (gate pattern — no promediar). Siempre termina apuntando a `course-pr-skill`
para la entrega.

---

## Gates human-in-the-loop

1. **Ruteo ambiguo o de confianza media** (tabla de confianza) — antes de generar nada.
2. **Secretos detectados** (Paso 0) — detiene todo el pipeline, no solo la entrega.
3. **Entrega final** — `/qa:entregar` nunca ejecuta `/curso:entregar` por su cuenta: presenta
   el resumen y pide confirmación explícita antes de invocar `course-pr-skill`, que a su vez
   vuelve a confirmar antes de abrir el PR. Doble gate intencional: uno es "¿entregamos ya?",
   el otro es "¿abrimos el PR?" — no es redundante, son dos decisiones distintas.
4. El orquestador en sí **nunca** hace `git push`, abre un PR ni mergea.

---

## Fallos comunes y fixes

| Síntoma | Causa | Fix |
|---------|-------|-----|
| Dos skills empatan en puntaje | Diff sin extensión clara (solo `.md`/config genérico) | Preferir la que ya tiene archivos en el repo; si ninguna, preguntar |
| Skill seleccionada pero sin prerrequisito | Repo objetivo no tiene el stack esperado (ej. flaui sin WinForms/WPF) | Omitir esa skill, reportar motivo explícito en la bitácora, seguir con las demás |
| `/qa:generar` corrido sin `/qa:analizar` previo | Falta el contexto/decisión ya extraída | Correr `/qa:analizar` primero — no hay generación sin bitácora |
| Bitácora dice "hash sin cambios" pero se esperaba regenerar | El diff/historia no cambió realmente | Confirmar con el usuario si igual quiere forzar regeneración explícita |
| Ruta relativa `../<X>-skill/skills/<X>/SKILL.md` no existe | La skill no está instalada como carpeta hermana, o el CLI la instaló distinto | Preguntar la ruta real, o usar el slash command si la skill ya está activa en sesión |
| Historia llega como imagen y se intenta clasificar directo | Se saltó el preprocesador OCR | Nunca clasificar sobre una imagen sin pasar antes por `ocr-bdd-skill` |

---

## Auto-Clarity

Salir de caveman para: hallazgos de secretos/credenciales detectados en el escaneo, cualquier
gate de ambigüedad que requiera explicar el porqué de la pregunta, y el resumen previo a
`/qa:entregar` — eso siempre se explica en claro, nunca en caveman. Retomar caveman después.

## Boundaries

Lee y sigue el `SKILL.md` de las demás skills del stack — nunca reimplementa su lógica de
generación por su cuenta.
NO genera `.feature`/`.spec.ts`/`.jmx`/etc. directamente — eso es siempre de la skill
correspondiente.
NO clasifica sin correr primero el escaneo de secretos (Paso 0).
NO selecciona una skill en confianza "Media"/"Ambigua" sin confirmación del usuario.
NO ejecuta una skill cuyo prerrequisito falló — la omite y lo reporta.
NO hace `git push`, abre PR ni mergea — eso es siempre `course-pr-skill`, con confirmación
explícita antes del PR.
NO regenera artefactos ya existentes sin verificar el hash de idempotencia primero.
"stop qa-orchestrator" o "normal mode": volver a estilo verbose.
