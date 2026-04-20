# aiquaa-labs — skills de automatización QA

> Skills para agentes de IA — powered by [aiquaa](https://aiquaa.com/)

Colección de skills para Claude Code, Cursor, Windsurf y más de 40 agentes de IA.
Cubre el ciclo completo de automatización QA: pruebas funcionales, pruebas declarativas,
pruebas E2E de navegador y pruebas de rendimiento — con salidas compactas, informes PDF
profesionales y pipelines CI listos para usar.

---

## Skills disponibles

| Skill | Herramienta | Tipo de prueba | Docs |
|-------|------------|----------------|------|
| `postman-newman-skill` | Postman + Newman | Funcional — GUI-first, colecciones JSON | [→](./postman-newman-skill/README.md) |
| `hurl-skill` | Hurl | Funcional — declarativo, diff-friendly, CI-native | [→](./hurl-skill/README.md) |
| `playwright-skill` | Playwright | E2E navegador + API — TypeScript, Page Objects | [→](./playwright-skill/README.md) |
| `jmeter-skill` | Apache JMeter | Rendimiento y estrés — 30.000 req, percentiles | [→](./jmeter-skill/README.md) |

---

## ¿Cuál usar?

```
¿Explorás la API con GUI y ya tenés colecciones Postman?        →  postman-newman-skill
¿Querés tests en texto plano que se revisen en PRs?             →  hurl-skill
¿Necesitás automatizar flujos en el navegador o E2E?            →  playwright-skill
¿Necesitás saber cuántos usuarios concurrentes aguanta el API?  →  jmeter-skill
```

Las cuatro skills son complementarias — se pueden usar juntas en el mismo proyecto.

---

## postman-newman-skill

**Herramienta:** [Postman](https://www.postman.com/) + [Newman](https://github.com/postmanlabs/newman)
**Lenguaje:** JavaScript (`pm.test()`)
**Formato:** JSON (colección Postman v2.1)
**Reporte CI:** JUnit XML via `newman-reporter-junit`

Genera colecciones Postman, scripts de tests, environments y pipelines CI.
Analiza fallos de Newman y produce informes PDF con detalle por request.

### Instalación

```bash
# Claude Code
npx skills add aiquaa-labs/postman-newman-skill

# Cursor
npx skills add aiquaa-labs/postman-newman-skill -a cursor

# Windsurf
npx skills add aiquaa-labs/postman-newman-skill -a windsurf

# Cualquier otro agente
npx skills add aiquaa-labs/postman-newman-skill
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

### Informe PDF

```bash
pip install reportlab Pillow

python reporter/newman_report.py \
  --results results/output.json \
  --api-version "v1.0.0" \
  --repo-url "https://github.com/org/repo" \
  --author "Nombre — email@empresa.com"
```

→ [Documentación completa](./postman-newman-skill/README.md)

---

## hurl-skill

**Herramienta:** [Hurl](https://hurl.dev/)
**Lenguaje:** Hurl DSL (texto plano)
**Formato:** `.hurl` (diff-friendly en git)
**Reporte CI:** JUnit XML nativo → Azure Test Plans sin plugins

Genera archivos `.hurl`, variables `.env` y pipelines Azure Pipelines.
Los resultados aparecen directamente en la pestaña **Tests** de Azure DevOps.

### Instalación

```bash
# Claude Code
npx skills add aiquaa-labs/hurl-skill

# Cursor
npx skills add aiquaa-labs/hurl-skill -a cursor

# Windsurf
npx skills add aiquaa-labs/hurl-skill -a windsurf

# Cualquier otro agente
npx skills add aiquaa-labs/hurl-skill
```

### Instalar Hurl localmente

```bash
# Windows
winget install Hurl.Hurl

# macOS
brew install hurl

# Ubuntu / Debian
apt-get install -y hurl

# Binario estático
curl -LO https://github.com/Orange-OpenSource/hurl/releases/latest/download/hurl-x86_64-unknown-linux-gnu.tar.gz
tar xzf hurl-*.tar.gz && sudo mv hurl /usr/local/bin/
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
`storageState` y pipelines CI. Cubre E2E web, API testing y visual testing.

### Instalación

```bash
# Claude Code
npx skills add aiquaa-labs/playwright-skill

# Cursor
npx skills add aiquaa-labs/playwright-skill -a cursor

# Windsurf
npx skills add aiquaa-labs/playwright-skill -a windsurf

# Cualquier otro agente
npx skills add aiquaa-labs/playwright-skill
```

### Instalar Playwright localmente

```bash
# Proyecto nuevo
npm init playwright@latest

# Proyecto existente
npm install -D @playwright/test
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

### Informe PDF ejecutivo

```bash
pip install reportlab

python reporter/playwright_report.py \
  --results     results/playwright-results.json \
  --app-name    "Mi App" \
  --environment "QA" \
  --app-version "v1.0.0" \
  --author      "Nombre — email@empresa.com"
```

→ [Documentación completa](./playwright-skill/README.md)

---

## jmeter-skill

**Herramienta:** [Apache JMeter](https://jmeter.apache.org/) 5.6+
**Lenguaje:** XML (`.jmx`) + CSV de datos
**Escenario base:** 1000 usuarios × 30 loops = 30.000 peticiones, ramp-up 0
**Reporte CI:** JTL → Dashboard HTML + informe PDF con veredicto

Genera planes `.jmx` con thread groups, CSV Data Set Config, extractores de token
y assertions. Informe PDF con throughput, percentiles P90/P95/P99 y veredicto automático.

### Instalación

```bash
# Claude Code
npx skills add aiquaa-labs/jmeter-skill

# Cursor
npx skills add aiquaa-labs/jmeter-skill -a cursor

# Windsurf
npx skills add aiquaa-labs/jmeter-skill -a windsurf

# Cualquier otro agente
npx skills add aiquaa-labs/jmeter-skill
```

### Instalar JMeter localmente

```bash
# Windows — descargar desde:
# https://jmeter.apache.org/download_jmeter.cgi

# Ubuntu / Debian
sudo apt-get install -y default-jdk
wget https://downloads.apache.org/jmeter/binaries/apache-jmeter-5.6.3.tgz
tar xzf apache-jmeter-5.6.3.tgz
export PATH=$PWD/apache-jmeter-5.6.3/bin:$PATH
```

### Comandos

| Comando | Acción |
|---------|--------|
| `/jmeter:generate` | Generar plan `.jmx` desde spec / curl / URL |
| `/jmeter:csv` | Generar o actualizar archivo de datos CSV |
| `/jmeter:fix` | Analizar y reparar plan fallido o resultado anómalo |
| `/jmeter:ci` | Generar pipeline Azure Pipelines |
| `/jmeter:run` | Mostrar comando de ejecución correcto |
| `/jmeter:report` | Analizar `.jtl` y generar descripción del PDF |

### Salidas

`P_NOMBRE.jmx` · `D_NOMBRE.csv` · `R_NOMBRE.jtl` · `INFORME_PERF_NOMBRE.pdf` · `Y_NOMBRE_jmeter.yml`

### Informe PDF

```bash
pip install reportlab pandas

python reporter/jmeter_report.py \
  --results  results/R_MI_API.jtl \
  --api-name "Mi API" \
  --threads  1000 \
  --loops    30 \
  --author   "Nombre — email@empresa.com"
```

→ [Documentación completa](./jmeter-skill/README.md)

---

## Instalación completa del stack

```bash
npx skills add aiquaa-labs/postman-newman-skill
npx skills add aiquaa-labs/hurl-skill
npx skills add aiquaa-labs/playwright-skill
npx skills add aiquaa-labs/jmeter-skill
```

---

## Convención de nombres

Todas las skills usan el mismo sistema de prefijos:

| Prefijo | Tipo de archivo | Skill |
|---------|----------------|-------|
| `C_` | Colección Postman `.json` | postman-newman |
| `E_` | Environment Postman `.json` | postman-newman |
| `H_` | Test file Hurl `.hurl` | hurl |
| `V_` | Variables Hurl `.env` | hurl |
| `T_` | Test spec Playwright `.spec.ts` | playwright |
| `P_` | Plan de prueba JMeter `.jmx` | jmeter |
| `D_` | Datos CSV JMeter `.csv` | jmeter |
| `R_` | Resultados JMeter `.jtl` | jmeter |
| `Y_` | Pipeline CI `.yml` (Azure / GitHub) | todas |
| `INFORME_DE_AUT_` | Informe PDF funcional | postman-newman |
| `INFORME_E2E_` | Informe PDF ejecutivo E2E | playwright |
| `INFORME_PERF_` | Informe PDF rendimiento | jmeter |

---

## Características comunes del stack

- **Context Intake** — el agente pregunta URL, flujo, auth y datos antes de generar. Nunca inventa campos ni selectores.
- **Caveman mode** — salidas comprimidas (~75% menos tokens) sin perder precisión técnica. Activar con `/caveman`.
- **Informe PDF** — cada skill genera su propio PDF con portada, métricas, detalle y veredicto. Python + ReportLab.
- **Azure Pipelines ready** — todos los templates YML usan `PublishTestResults@2` con JUnit XML para la pestaña Tests.
- **Sin hardcodeo** — URLs, tokens y credenciales siempre en variables de entorno. Nunca en los archivos generados.

---

## Estructura del monorepo

```
aiquaa-labs/
├── postman-newman-skill/    → Postman + Newman — pruebas funcionales GUI
├── hurl-skill/              → Hurl — pruebas funcionales declarativas
├── playwright-skill/        → Playwright — E2E navegador + API TypeScript
├── jmeter-skill/            → JMeter — pruebas de rendimiento y estrés
└── README.md                → este archivo
```

---

## Créditos

Creado por [aiquaa](https://aiquaa.com/) — *Saber es calidad*

Skills de caveman basadas en [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) — MIT License.

## Licencia

MIT
