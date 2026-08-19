# Mapa de señales → skill (fuente de verdad)

Este archivo es la referencia completa que `SKILL.md` resume. Toda actualización al mapa de
clasificación se hace acá primero, después se refleja la versión condensada en `SKILL.md`.

## Principio

Reglas determinísticas primero (grep de rutas/extensiones sobre el diff, keywords sobre la
historia). El LLM solo entra en la segunda pasada, para desempatar casos "Media"/"Ambigua"
(ver tabla de confianza en `SKILL.md`) — nunca como clasificador primario. Esto es lo que hace
la decisión reproducible y auditable: dos corridas sobre el mismo input dan el mismo resultado
determinístico salvo que el LLM tenga que resolver un empate genuino, y en ese caso se
pregunta al usuario en vez de dejar que el modelo decida solo.

## Tabla completa

### `ocr-bdd-skill` — preprocesador bloqueante

| Señal | Peso |
|---|---|
| Adjunto con extensión `.pdf`, `.png`, `.jpg`, `.jpeg`, `.webp`, o mimetype `image/*`/`application/pdf` | 20 |
| Usuario dice explícitamente "esto es una captura/foto/scan de requisitos" | 20 |

No compite por capa contra las demás — si dispara, corre **antes** de puntuar el resto, y su
salida confirmada (el `.feature` ya generado, sin `TODO` pendientes) es la que se usa como
input de la historia para el resto del pipeline.

### `bdd-skill`

| Señal (ruta/extensión) | Peso | Señal (keyword en historia) | Peso |
|---|---|---|---|
| `**/*.feature` | 15 | "Given/Cuando/Entonces" en el texto | 8 |
| `**/*.steps.ts` | 15 | "criterios de aceptación" enumerados | 8 |
| `world.ts`, `hooks.ts`, `cucumber.js`/`cucumber.cjs` | 12 | tag `@grupo-N` del curso | 6 |

### `postman-newman-skill`

| Señal (ruta/extensión) | Peso | Señal (keyword) | Peso |
|---|---|---|---|
| `**/*.postman_collection.json` | 15 | "Postman" | 8 |
| `C_*.json`, `E_*.json` (convención del stack) | 15 | "colección" | 6 |
| `newman-reporter*` en `package.json` | 10 | "Newman", "GUI-first" | 6 |

### `hurl-skill`

| Señal (ruta/extensión) | Peso | Señal (keyword) | Peso |
|---|---|---|---|
| `**/*.hurl` | 15 | "Hurl" | 8 |
| `H_*.hurl`, `V_*.env` (convención del stack) | 15 | "texto plano", "diff-friendly" | 6 |
| — | — | "Azure Test Plans nativo" | 6 |

### `playwright-skill`

| Señal (ruta/extensión) | Peso | Señal (keyword) | Peso |
|---|---|---|---|
| `src/components/**/*.{tsx,jsx,vue,html}` | 15 | "navegador", "E2E" | 8 |
| `**/*.spec.ts` bajo `e2e/` o `tests/ui` | 15 | "Playwright" | 8 |
| `pages/*Page.ts`, `playwright.config.ts` | 15 | "flujo de usuario", "pantalla web", "checkout" | 6 |
| Diff agrega/cambia atributos `data-testid` | 12 | — | — |

### `jmeter-skill`

| Señal (ruta/extensión) | Peso | Señal (keyword) | Peso |
|---|---|---|---|
| `**/*.jmx`, `P_*.jmx` | 15 | "rendimiento", "carga", "estrés" | 8 |
| `D_*.csv` en contexto de perf | 12 | "usuarios concurrentes", "SLA" | 8 |
| `V_PERFILES.properties` | 12 | "p95/p99", "throughput", "escalabilidad" | 6 |

### `flaui-skill`

| Señal (ruta/extensión) | Peso | Señal (keyword) | Peso |
|---|---|---|---|
| `**/*.Designer.cs` | 15 | "escritorio" | 8 |
| `**/*.xaml` | 15 | "WinForms", "WPF" | 8 |
| `.csproj` con `<UseWindowsForms>true>` o `<UseWPF>true>` | 15 | "FlaUI", "Reqnroll" | 6 |

### `database-object-testing-skill`

| Señal (ruta/extensión) | Peso | Señal (keyword) | Peso |
|---|---|---|---|
| `migrations/**/*.sql` | 15 | "vista", "procedimiento almacenado" | 8 |
| `**/views/*.sql`, `**/procedures/*.sql`, `**/functions/*.sql`, `**/triggers/*.sql` | 15 | "función SQL", "trigger" | 8 |
| `rules/*.md` (formato database-object-testing) | 10 | "objeto de base de datos", "comparar base vs candidata" | 6 |

### `sandbox-skill` — contexto, no puntuada

Dispara carga de contexto (no compite): `x-api-key`, `aiquaa-sandbox-api`, `qa_training`,
"grupo N".

### `course-pr-skill` — paso fijo, no puntuado

Siempre al final del pipeline, solo en `/qa:entregar`, nunca antes.

## Desempate hurl vs postman-newman

Ambas cubren API funcional y comparten buena parte del vocabulario de historia. Si ninguna
extensión de archivo aparece en el diff (ambas quedan en 8 o menos, solo por keyword):

1. Preferir la herramienta cuyos archivos **ya existen** en el repo objetivo — si hay
   `*.postman_collection.json` en el repo aunque el PR actual no los toque, usar
   `postman-newman-skill`; si hay `*.hurl`, usar `hurl-skill`.
   2. Si ninguna existe todavía en el repo → empate genuino → gate de confirmación, preguntar
   al usuario cuál prefiere (y por qué, para dejarlo en la bitácora).

## Multi-skill — combinación

No hay límite de skills seleccionadas por corrida. Ejemplo típico: un PR que agrega un campo
nuevo a un endpoint (`.hurl` tocado) y lo expone en una pantalla web (`.tsx` con nuevo
`data-testid`) dispara `hurl-skill` **y** `playwright-skill` en la misma corrida — se generan
y ejecutan en el orden de puntaje, cada una completa antes de la siguiente, y el informe
consolidado las lista a ambas con su propio veredicto.
