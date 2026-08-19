# aiquaa-labs — skills de automatización QA

> Skills para agentes de IA — powered by [aiquaa](https://aiquaa.com/)

Colección de skills para Claude Code, Cursor, Windsurf y más de 40 agentes de IA.
Cubre el ciclo completo de automatización QA: BDD, pruebas funcionales, pruebas declarativas,
pruebas E2E de navegador y de escritorio, verificación de base de datos y objetos de BD, y
pruebas de rendimiento dinámicas — con salidas compactas, informes PDF profesionales,
pipelines CI listos para usar, y entrega por Pull Request. Es también la base del **curso de
automatización de pruebas de aiquaa** (8 semanas, arranca a usar estas skills desde la semana 3).

---

## Skills disponibles

| Skill | Herramienta | Tipo de prueba | Docs |
|-------|------------|----------------|------|
| `sandbox-skill` | — | Contrato del entorno de práctica del curso | [→](./sandbox-skill/README.md) |
| `bdd-skill` | Cucumber + Playwright | BDD — Gherkin, steps API/web/BD | [→](./bdd-skill/README.md) |
| `postman-newman-skill` | Postman + Newman | Funcional — GUI-first, colecciones JSON | [→](./postman-newman-skill/README.md) |
| `hurl-skill` | Hurl | Funcional — declarativo, diff-friendly, CI-native | [→](./hurl-skill/README.md) |
| `playwright-skill` | Playwright | E2E navegador + API — TypeScript, Page Objects | [→](./playwright-skill/README.md) |
| `jmeter-skill` | Apache JMeter | Rendimiento dinámico — carga, estrés, pico, resistencia, escalabilidad | [→](./jmeter-skill/README.md) |
| `flaui-skill` | FlaUI + Reqnroll + NUnit | Funcional — escritorio C# (WinForms/WPF), BDD + trazabilidad | [→](./flaui-skill/README.md) |
| `database-object-testing-skill` | Node.js + API REST | Objetos de BD — funcional, diferencias y costo | [→](./database-object-testing-skill/README.md) |
| `ocr-bdd-skill` | visión / pdftotext / tesseract | Documento → requisitos → BDD | [→](./ocr-bdd-skill/README.md) |
| `course-pr-skill` | `gh` / `az repos` | Entrega semanal vía Pull Request | [→](./course-pr-skill/README.md) |

---

## ¿Cuál usar?

```
¿Necesitás el contrato del entorno de práctica (API, auth, rate limit)?   →  sandbox-skill
¿Vas a escribir criterios de aceptación como Gherkin?                    →  bdd-skill
¿Explorás la API con GUI y ya tenés colecciones Postman?                 →  postman-newman-skill
¿Querés tests en texto plano que se revisen en PRs?                      →  hurl-skill
¿Necesitás automatizar flujos en el navegador o E2E?                     →  playwright-skill
¿Necesitás saber cuántos usuarios concurrentes aguanta el API?           →  jmeter-skill
¿Automatizás pantallas de escritorio C# (WinForms/WPF)?                  →  flaui-skill
¿Necesitás probar objetos de BD sin conexión directa al motor?           →  database-object-testing-skill
¿Los requisitos llegaron como PDF, foto o captura de pantalla?           →  ocr-bdd-skill
¿Ya automatizaste y necesitás entregar por PR?                           →  course-pr-skill
```

Todas son complementarias — se usan juntas en el mismo proyecto. `sandbox-skill` es la base
de contexto que las demás consultan para no inventar endpoints, campos ni tablas.

---

## Ruta del curso — 8 semanas

El curso arranca a usar este stack desde la **semana 3** (semanas 1-2 son fundamentos previos
al agente). Progresión sugerida — ajustable según el ritmo real de la clase:

| Semana | Foco | Skill principal | Complementa con |
|--------|------|-------------------|--------------------|
| 1-2 | Fundamentos (HTTP, testing, Git) | — | — |
| 3 | BDD — features y steps por grupo | `bdd-skill` | `sandbox-skill` |
| 4 | BDD + verificación en base de datos | `bdd-skill` | `sandbox-skill` (`sql/select`) |
| 5 | API funcional — Postman o Hurl | `postman-newman-skill` / `hurl-skill` | `sandbox-skill` |
| 6 | E2E web — Playwright | `playwright-skill` | `sandbox-skill` (`data-testid`) |
| 7 | Rendimiento — JMeter, 5 perfiles de carga | `jmeter-skill` | `references/ptu-cptjm.md` (temario PtU) |
| 8 | Integración final, CI, entrega | `course-pr-skill` | todas las anteriores |

Documentos que llegan como PDF/foto en cualquier semana pasan primero por `ocr-bdd-skill`
antes de convertirse en `.feature`. `flaui-skill` y `database-object-testing-skill` cubren
casos fuera del sandbox del curso (escritorio C# y objetos de BD sin acceso directo al motor)
— disponibles para proyectos propios del alumno una vez terminado el temario base.

Cada uno de los **10 grupos** del curso trabaja un módulo funcional distinto del sandbox
durante las 8 semanas — ver `sandbox-skill/references/grupos.md` para el mapeo completo
(Grupo 1 Autenticación … Grupo 10 Administración de Roles).

---

## Quickstart del alumno

```bash
# 1. Pedir la API key del sandbox al docente (una por alumno — nunca compartida)

# 2. Instalar las skills que correspondan a la semana actual
npx skills add aiquaa-labs/sandbox-skill
npx skills add aiquaa-labs/bdd-skill

# 3. Guardar la key como variable de entorno — nunca en un archivo versionado
export SANDBOX_API_KEY="sbx_alumno01_xxxxxxxxxxxx"
export SANDBOX_API_BASE_URL="https://aiquaa-sandbox-api.vercel.app"

# 4. Trabajar con el agente — "grupo 3, generá el feature de pagos"

# 5. Entregar
# "/curso:entregar"  (requiere course-pr-skill instalada y un repo propio con remote configurado)
```

---

## Entorno de práctica

| Pieza | URL |
|-------|-----|
| API sandbox | `https://aiquaa-sandbox-api.vercel.app` |
| Docs OpenAPI | `https://aiquaa-sandbox-api.vercel.app/docs` |
| Front web de práctica | repo `aiquaa-sandbox-web` (dev `http://localhost:3001`) |

Auth por header `x-api-key` (sin JWT), rate limit de 30 req/min por key, y un endpoint
`POST /api/v1/sql/select` para verificar en base de datos cualquier acción hecha por API o
web. Contrato completo, con los 32 endpoints y las 15 tablas del schema `qa_training`, en
[`sandbox-skill`](./sandbox-skill).

---

## postman-newman-skill

**Herramienta:** [Postman](https://www.postman.com/) + [Newman](https://github.com/postmanlabs/newman)
**Lenguaje:** JavaScript (`pm.test()`)
**Formato:** JSON (colección Postman v2.1)
**Reporte CI:** JUnit XML via `newman-reporter-junit`

Genera colecciones Postman, scripts de tests, environments y pipelines CI.
Analiza fallos de Newman y produce informes PDF con detalle por request. Incluye patrón de
verificación en base de datos contra `sandbox-skill`.

### Instalación

```bash
npx skills add aiquaa-labs/postman-newman-skill
npx skills add aiquaa-labs/postman-newman-skill -a cursor
npx skills add aiquaa-labs/postman-newman-skill -a windsurf
```

### Instalar Newman localmente

```bash
npm install -g newman newman-reporter-htmlextra
```

### Comandos

| Comando | Acción |
|---------|--------|
| `/postman:generate` | Generar colección desde spec / curl / URL |
| `/postman:add-test` | Agregar `pm.tests` a requests existentes |
| `/postman:fix` | Analizar y reparar test fallido |
| `/postman:ci` | Generar pipeline GitHub Actions o Azure Pipelines |
| `/postman:env` | Crear o actualizar environment file |
| `/postman:run` | Correr colección y reportar resultados |

### Salidas

`C_NOMBRE.json` · `E_NOMBRE.json` · `Y_NOMBRE.yml` · `INFORME_DE_AUT_NOMBRE.pdf`

→ [Documentación completa](./postman-newman-skill/README.md)

---

## hurl-skill

**Herramienta:** [Hurl](https://hurl.dev/)
**Lenguaje:** Hurl DSL (texto plano)
**Formato:** `.hurl` (diff-friendly en git)
**Reporte CI:** JUnit XML nativo → Azure Test Plans sin plugins

Genera archivos `.hurl`, variables `.env` y pipelines Azure Pipelines. Los resultados aparecen
directamente en la pestaña **Tests** de Azure DevOps. Incluye patrón de verificación en base
de datos contra `sandbox-skill`.

### Instalación

```bash
npx skills add aiquaa-labs/hurl-skill
npx skills add aiquaa-labs/hurl-skill -a cursor
npx skills add aiquaa-labs/hurl-skill -a windsurf
```

### Instalar Hurl localmente

```bash
winget install Hurl.Hurl          # Windows
brew install hurl                  # macOS
apt-get install -y hurl            # Ubuntu / Debian
```

### Comandos

| Comando | Acción |
|---------|--------|
| `/hurl:generate` | Generar `.hurl` desde spec / curl / URL |
| `/hurl:add-test` | Agregar assertions a un entry existente |
| `/hurl:fix` | Analizar y reparar un entry fallido |
| `/hurl:ci` | Generar pipeline Azure Pipelines |
| `/hurl:env` | Crear o actualizar archivo de variables `.env` |
| `/hurl:run` | Mostrar comando de ejecución y reportar resultados |

### Salidas

`H_NOMBRE.hurl` · `V_NOMBRE.env` · `Y_NOMBRE_hurl.yml`

→ [Documentación completa](./hurl-skill/README.md)

---

## playwright-skill

**Herramienta:** [Microsoft Playwright](https://playwright.dev/)
**Lenguaje:** TypeScript
**Browsers:** Chromium, Firefox, WebKit
**Reporte CI:** JUnit XML nativo → Azure Test Plans + informe PDF ejecutivo

Genera specs TypeScript, Page Objects, `playwright.config.ts`, `auth.setup.ts` con
`storageState` y pipelines CI. Cubre E2E web, API testing y visual testing. Incluye patrón de
verificación en base de datos contra `sandbox-skill` y usa la convención `data-testid` del
front de práctica.

### Instalación

```bash
npx skills add aiquaa-labs/playwright-skill
npx skills add aiquaa-labs/playwright-skill -a cursor
npx skills add aiquaa-labs/playwright-skill -a windsurf
```

### Instalar Playwright localmente

```bash
npm init playwright@latest                       # proyecto nuevo
npm install -D @playwright/test                    # proyecto existente
npx playwright install --with-deps chromium
```

### Comandos

| Comando | Acción |
|---------|--------|
| `/playwright:generate` | Generar spec `.ts` desde flujo / URL / código fuente |
| `/playwright:page` | Generar o actualizar Page Object |
| `/playwright:fix` | Analizar y reparar test fallido |
| `/playwright:ci` | Generar pipeline Azure Pipelines o GitHub Actions |
| `/playwright:auth` | Generar `auth.setup.ts` con storageState |
| `/playwright:config` | Generar o actualizar `playwright.config.ts` |
| `/playwright:report` | Analizar JSON y generar descripción del PDF ejecutivo |

### Salidas

`T_NOMBRE.spec.ts` · `pages/NombrePage.ts` · `playwright.config.ts` · `Y_NOMBRE_playwright.yml` · `INFORME_E2E_NOMBRE.pdf`

→ [Documentación completa](./playwright-skill/README.md)

---

## bdd-skill

**Herramienta:** [Cucumber](https://cucumber.io/) (`@cucumber/cucumber`) + [Playwright](https://playwright.dev/)
**Lenguaje:** Gherkin (`.feature`) + TypeScript (steps)
**Reporte:** JSON nativo de cucumber-js → PDF con matriz de trazabilidad

Genera `.feature`, step definitions reutilizables (API, web, base de datos), `world.ts`,
`hooks.ts`, `cucumber.js` y pipelines CI. Es la skill con la que arranca la semana 3 del curso
— cada grupo automatiza su módulo del sandbox en BDD.

### Instalación

```bash
npx skills add aiquaa-labs/bdd-skill
npm install -D @cucumber/cucumber @playwright/test ts-node typescript
npx playwright install --with-deps chromium
```

### Comandos

| Comando | Acción |
|---------|--------|
| `/bdd:generate` | Generar `.feature` desde criterios / grupo del curso / documento |
| `/bdd:steps` | Agregar o completar steps reutilizables |
| `/bdd:fix` | Analizar y reparar un escenario fallido |
| `/bdd:ci` | Generar pipeline GitHub Actions o Azure Pipelines |
| `/bdd:report` | Analizar resultados y describir el informe PDF |

### Salidas

`F_GRUPO_NN_MODULO.feature` · `S_<capa>.steps.ts` · `Y_NOMBRE_bdd.yml` · `INFORME_BDD_NOMBRE.pdf`

→ [Documentación completa](./bdd-skill/README.md)

---

## jmeter-skill

**Herramienta:** [Apache JMeter](https://jmeter.apache.org/) 5.6+
**Lenguaje:** XML (`.jmx`) + CSV de datos, todo property-driven (`${__P(...)}`)
**Perfiles:** baseline, carga, estrés, pico, resistencia, escalabilidad — un solo `.jmx`
**Reporte CI:** JTL → Dashboard HTML + informe PDF con SLA configurable y comparación a baseline

Genera un plan `.jmx` con thread groups, CSV Data Set Config, correlación (JSON/Regex
Extractor), temporizadores y controladores lógicos, alineado al temario **PtU Certified
Performance Tester con JMeter (CPTJM)** — ver `jmeter-skill/references/ptu-cptjm.md` para el
mapa LO1–LO23.

### Instalación

```bash
npx skills add aiquaa-labs/jmeter-skill
```

### Instalar JMeter localmente

```bash
# Windows — https://jmeter.apache.org/download_jmeter.cgi
# Ubuntu / Debian
sudo apt-get install -y default-jdk
wget https://downloads.apache.org/jmeter/binaries/apache-jmeter-5.6.3.tgz
tar xzf apache-jmeter-5.6.3.tgz
export PATH=$PWD/apache-jmeter-5.6.3/bin:$PATH
```

### Comandos

| Comando | Acción |
|---------|--------|
| `/jmeter:generate` | Generar `.jmx` property-driven desde spec / curl / URL / grupo del sandbox |
| `/jmeter:csv` | Generar o actualizar archivo CSV de datos |
| `/jmeter:perfil` | Calcular los valores `-J` de un perfil de carga |
| `/jmeter:fix` | Analizar y reparar plan fallido o resultado anómalo |
| `/jmeter:ci` | Generar pipeline Azure Pipelines o GitHub Actions |
| `/jmeter:run` | Mostrar el comando de ejecución para el perfil elegido |
| `/jmeter:report` | Analizar `.jtl` y generar descripción del PDF |

### Salidas

`P_NOMBRE.jmx` · `D_NOMBRE.csv` · `V_PERFILES.properties` · `R_NOMBRE.jtl` · `INFORME_PERF_NOMBRE.pdf` · `Y_NOMBRE_jmeter.yml`

→ [Documentación completa](./jmeter-skill/README.md)

---

## flaui-skill

**Herramienta:** [FlaUI](https://github.com/FlaUI/FlaUI) (UIA3) + [Reqnroll](https://reqnroll.net/) + [NUnit](https://nunit.org/)
**Lenguaje:** C# (`net8.0-windows`)
**UI soportada:** WinForms y WPF de escritorio (Windows)
**Reporte CI:** NUnit3 XML nativo → Azure Test Plans + informe PDF con matriz de trazabilidad

Lee requerimientos funcionales, el código real de la pantalla (`.Designer.cs` / `.xaml`) y los
cambios de un Pull Request para generar automatización funcional: features Gherkin, Window
Objects, tests NUnit y matriz de trazabilidad `RF-XXX` ↔ tests. Incluye un analizador propio
(`ui_inventory.py`) que extrae los `AutomationId` reales del código — nunca inventa selectores.

### Instalación

```bash
npx skills add aiquaa-labs/flaui-skill
npx skills add aiquaa-labs/flaui-skill -a cursor
npx skills add aiquaa-labs/flaui-skill -a windsurf
```

### Instalar el stack localmente

```bash
dotnet new nunit -n MiApp.UiTests
cd MiApp.UiTests
dotnet add package FlaUI.Core
dotnet add package FlaUI.UIA3
dotnet add package Reqnroll.NUnit
dotnet add package NunitXml.TestLogger
```

### Comandos

| Comando | Acción |
|---------|--------|
| `/flaui:inventory` | Inventario de controles reales (AutomationId) de una pantalla |
| `/flaui:generate` | Generar feature + steps + Window Object + tests desde un requerimiento |
| `/flaui:window` | Generar o actualizar un Window Object |
| `/flaui:from-pr` | Leer un PR y actualizar solo los tests impactados por el cambio |
| `/flaui:trace` | Generar o actualizar la matriz de trazabilidad |
| `/flaui:fix` | Analizar y reparar un test fallido |
| `/flaui:ci` | Generar pipeline Azure Pipelines |
| `/flaui:run` | Mostrar comando `dotnet test` correcto |
| `/flaui:report` | Analizar resultados y generar el PDF ejecutivo |

### Salidas

`F_NOMBRE.feature` · `S_NOMBRE_Steps.cs` · `N_NOMBRE_Tests.cs` · `W_Nombre.cs` ·
`MATRIZ_NOMBRE.md` · `Y_NOMBRE_flaui.yml` · `INFORME_UI_NOMBRE.pdf`

### Informe PDF

```bash
pip install reportlab

python reporter/flaui_report.py \
  --results TestResult.xml \
  --app-name "Sistema de Gestión" \
  --environment "QA" \
  --author "Nombre — email@empresa.com" \
  --pr "123"
```

→ [Documentación completa](./flaui-skill/README.md)

---

## database-object-testing-skill

**Herramienta:** runner Node.js + API REST corporativa (sin driver ni acceso directo al motor)
**Formato:** suites `.json`, reglas en `rules/*.md`
**Reporte:** PDF, JSON, Markdown y JUnit para CI

Prueba objetos de bases de datos relacionales (vistas, SQL, funciones, procedimientos,
paquetes, triggers) a través de un gateway REST corporativo — nunca se conecta al motor
directo. Compara comportamiento entre una versión base y una candidata (filas sin orden),
controla regresiones de costo con umbrales porcentuales, y aplica reglas humanas/ejecutables
almacenadas como Markdown.

### Instalación

```bash
npx skills add aiquaa-labs/database-object-testing-skill
```

### Inicio rápido

Requiere Node.js 20+. El runner no tiene dependencias npm; para el PDF, `npm run report:deps`
(ReportLab). Ejemplo con dos servicios simulados en paralelo:

```bash
npm run example:baseline
npm run example:candidate
```

```powershell
$env:DBTEST_BASELINE_URL='http://127.0.0.1:4101'
$env:DBTEST_CANDIDATE_URL='http://127.0.0.1:4102'
$env:DBTEST_API_TOKEN='local-example-token'
npm run example:run
```

### Comandos

```bash
node src/cli.mjs validate-rules --rules rules
node src/cli.mjs run --suite examples/S_EXAMPLE.json --rules rules --output results
```

Integración real: implementar los endpoints normalizados de
`skills/test-database-objects/references/api-contract.md`, con un usuario de solo los
privilegios necesarios y lista permitida de objetos — nunca apuntar suites de escritura a
producción.

→ [Documentación completa](./database-object-testing-skill/README.md)

---

## ocr-bdd-skill

**Entrada:** PDF, imagen, captura de pantalla
**Método:** visión del agente (primario) → `pdftotext -layout` → `tesseract` (respaldos)
**Salida:** `.feature` + matriz de trazabilidad requisito → escenario

Convierte documentos de requisitos en Gherkin. Regla dura: **nunca completa un campo
ilegible por inferencia** — todo lo que no se puede leer con confianza queda como
`# TODO: confirmar con el docente`. Complementa `bdd-skill`, que toma la lista ya confirmada.

### Instalación

```bash
npx skills add aiquaa-labs/ocr-bdd-skill
```

→ [Documentación completa](./ocr-bdd-skill/README.md)

---

## course-pr-skill

**Plataformas:** GitHub (`gh`) o Azure DevOps (`az repos`) — autodetectadas por el remote

Entrega semanal vía Pull Request contra el repositorio propio del alumno. Corre un pre-flight
(escaneo de secretos, tests, artefactos esperados de la semana) **antes** de commitear, y
nunca abre el PR sin confirmación explícita.

### Instalación

```bash
npx skills add aiquaa-labs/course-pr-skill
```

### Comandos

| Comando | Acción |
|---------|--------|
| `/curso:entregar` | Pre-flight → rama → commit → PR |
| `/curso:revisar` | Checklist de entrega sobre un PR ajeno |
| `/curso:pr` | Solo arma el PR |

→ [Documentación completa](./course-pr-skill/README.md)

---

## sandbox-skill

Contrato compartido del entorno de práctica — no genera archivos, es el contexto que
consultan las demás skills. Endpoints, auth (`x-api-key`), envelope de respuesta, rate limit
(30 req/min), endpoints de SQL crudo para verificar en base de datos, y los 10 grupos del
curso mapeados a módulo/endpoints/tablas.

### Instalación

```bash
npx skills add aiquaa-labs/sandbox-skill
```

→ [Documentación completa](./sandbox-skill/README.md)

---

## Instalación completa del stack

```bash
npx skills add aiquaa-labs/sandbox-skill
npx skills add aiquaa-labs/bdd-skill
npx skills add aiquaa-labs/postman-newman-skill
npx skills add aiquaa-labs/hurl-skill
npx skills add aiquaa-labs/playwright-skill
npx skills add aiquaa-labs/jmeter-skill
npx skills add aiquaa-labs/flaui-skill
npx skills add aiquaa-labs/database-object-testing-skill
npx skills add aiquaa-labs/ocr-bdd-skill
npx skills add aiquaa-labs/course-pr-skill
```

---

## Convención de nombres

Todas las skills usan el mismo sistema de prefijos:

| Prefijo | Tipo de archivo | Skill |
|---------|----------------|-------|
| `C_` | Colección Postman `.json` | postman-newman |
| `E_` | Environment Postman `.json` | postman-newman |
| `H_` | Test file Hurl `.hurl` | hurl |
| `V_` | Variables Hurl `.env` / perfiles JMeter `.properties` | hurl, jmeter |
| `T_` | Test spec Playwright `.spec.ts` | playwright |
| `F_` | Feature Gherkin `.feature` | bdd, ocr-bdd, flaui |
| `S_` | Step definitions (`.steps.ts` en bdd, `_Steps.cs` en flaui) | bdd, flaui |
| `P_` | Plan de prueba JMeter `.jmx` | jmeter |
| `D_` | Datos CSV JMeter `.csv` | jmeter |
| `R_` | Resultados JMeter `.jtl` | jmeter |
| `N_` | Test NUnit puro `_Tests.cs` | flaui |
| `W_` | Window Object `W_Nombre.cs` | flaui |
| `MATRIZ_` | Matriz de trazabilidad `.md` | flaui |
| `TRAZA_` | Matriz de trazabilidad requisito → escenario | ocr-bdd |
| `Y_` | Pipeline CI `.yml` (Azure / GitHub) | todas |
| `INFORME_DE_AUT_` | Informe PDF funcional | postman-newman |
| `INFORME_E2E_` | Informe PDF ejecutivo E2E | playwright |
| `INFORME_BDD_` | Informe PDF BDD con trazabilidad | bdd |
| `INFORME_PERF_` | Informe PDF rendimiento | jmeter |
| `INFORME_UI_` | Informe PDF con matriz de trazabilidad | flaui |

---

## Características comunes del stack

- **Context Intake** — el agente pregunta URL, flujo, auth y datos antes de generar. Nunca
  inventa campos ni selectores. `ocr-bdd-skill` extiende esta regla a documentos: nunca
  completa lo ilegible por inferencia; `flaui-skill` la extiende al código real de la pantalla:
  nunca inventa un `AutomationId`.
- **Caveman mode** — salidas comprimidas (~75% menos tokens) sin perder precisión técnica.
  Activar con `/caveman`.
- **Informe PDF** — cada skill genera su propio PDF con portada, métricas, detalle y
  veredicto. Python + ReportLab.
- **CI ready** — todos los templates YML usan JUnit/JSON (`PublishTestResults@2` en Azure) para
  integrarse con Azure Test Plans o GitHub Actions, con `continueOnError`/reporte
  `condition: always()`.
- **Sin hardcodeo** — URLs, tokens y credenciales siempre en variables de entorno. Nunca en
  los archivos generados.
- **Verificación en base de datos** — `postman-newman`, `hurl`, `playwright` y `bdd` saben
  cerrar el ciclo acción → verificación con `POST /api/v1/sql/select` del sandbox.
- **Entrega auditable** — `course-pr-skill` nunca commitea con secretos detectados en el diff
  ni abre un PR sin confirmación.

---

## Estructura del monorepo

```
aiquaa-labs/
├── sandbox-skill/                  → contrato del entorno de práctica del curso
├── bdd-skill/                      → Cucumber + Playwright — BDD, semana 3+
├── postman-newman-skill/           → Postman + Newman — pruebas funcionales GUI
├── hurl-skill/                     → Hurl — pruebas funcionales declarativas
├── playwright-skill/               → Playwright — E2E navegador + API TypeScript
├── jmeter-skill/                   → JMeter — rendimiento dinámico, perfiles PtU CPTJM
├── flaui-skill/                    → FlaUI + Reqnroll + NUnit — escritorio C# (WinForms/WPF)
├── database-object-testing-skill/  → Node.js + API REST — objetos de BD relacional
├── ocr-bdd-skill/                  → documento → requisitos → BDD
├── course-pr-skill/                → entrega semanal vía Pull Request
└── README.md                       → este archivo
```

---

## Créditos

Creado por [aiquaa](https://aiquaa.com/) — *Saber es calidad*

Skills de caveman basadas en [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) — MIT License.

## Licencia

MIT
