# Prerrequisitos por skill — antes de `/qa:generar` / `/qa:ejecutar`

Regla dura para todas: un fallo de prerrequisito se reporta **explícito** en la sección 6 de
la bitácora (`references/decision-log-schema.md`) — nunca se omite en silencio, nunca bloquea
sin explicar por qué.

| Skill | Check | Cómo verificar | Si falla |
|---|---|---|---|
| `playwright-skill` | ¿Existe frontend real (componentes/páginas) en el repo objetivo? | Buscar `src/components/`, `pages/`, `*.tsx`/`*.jsx`/`*.vue` fuera de `node_modules` | Omitir generación y ejecución, reportar "no se encontró frontend — no se inventan selectores ni flujos" |
| `flaui-skill` | ¿Existe un `.csproj` con `<UseWindowsForms>true</UseWindowsForms>` o `<UseWPF>true</UseWPF>`? | `grep` sobre `**/*.csproj` | Omitir, reportar "no se encontró proyecto de escritorio WinForms/WPF" |
| `database-object-testing-skill` | ¿Gateway REST configurado? | Variables `DBTEST_BASELINE_URL` / `DBTEST_CANDIDATE_URL` presentes | Omitir — **nunca** cae a driver directo como alternativa |
| `jmeter-skill` | ¿JMeter instalado? ¿Entorno destino confirmado no-producción? | `jmeter --version`; preguntar el entorno si no viene del contexto | Generación puede seguir (el `.jmx` no requiere JMeter instalado); omitir solo `/qa:ejecutar` y reportar |
| `hurl-skill` | ¿CLI `hurl` instalado? | `hurl --version` | Omitir solo `/qa:ejecutar`, `/qa:generar` no depende del CLI |
| `postman-newman-skill` | ¿Newman instalado? | `newman --version` | Igual que arriba |
| `bdd-skill` | ¿`@cucumber/cucumber` y `@playwright/test` en `package.json`/instalados? | `npx cucumber-js --version` | Generación puede seguir; omitir solo `/qa:ejecutar` y reportar |
| `ocr-bdd-skill` | Preprocesador — no tiene prerrequisito de ejecución, corre siempre que el intake detecta un documento | — | N/A |
| `sandbox-skill` | Contexto — no genera ni ejecuta nada | — | N/A |
| `course-pr-skill` | Delegado a su propio pre-flight (`/curso:entregar` paso 0-1) | — | No se duplica el check acá — se reporta lo que `course-pr-skill` reporte en su propio pre-flight |

## Principio de seguridad para entorno de rendimiento

`jmeter-skill` nunca corre `/qa:ejecutar` contra un entorno sin confirmación explícita de que
no es producción — un load test mal dirigido puede tumbar un servicio real. Si el contexto no
deja claro el entorno, preguntar antes de ejecutar (la generación del `.jmx` sí puede seguir
sin esta confirmación, solo la ejecución la requiere).
