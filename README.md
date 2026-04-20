# aiquaa-labs — skills de automatización QA

> Skills para agentes de IA — powered by [aiquaa](https://aiquaa.com/)

Colección de skills para Claude Code, Cursor, Windsurf y más de 40 agentes de IA.
Cubre el ciclo completo de automatización QA: pruebas funcionales, pruebas declarativas
y pruebas de rendimiento — con salidas compactas, informes PDF profesionales y pipelines
CI listos para usar.

---

## Skills disponibles

| Skill | Herramienta | Tipo de prueba | Docs |
|-------|------------|----------------|------|
| `postman-newman-skill` | Postman + Newman | Funcional — GUI-first | [→](./postman-newman-skill/README.md) |
| `hurl-skill` | Hurl | Funcional — declarativo, CI-native | [→](./hurl-skill/README.md) |
| `jmeter-skill` | Apache JMeter | Rendimiento y estrés | [→](./jmeter-skill/README.md) |

---

## ¿Cuál usar?

```
¿Explorás la API con GUI y ya tenés colecciones Postman?        →  postman-newman-skill
¿Querés tests en texto plano que se revisen en PRs?             →  hurl-skill
¿Necesitás saber cuántos usuarios concurrentes aguanta el API?  →  jmeter-skill
```

Las tres skills son complementarias — se pueden usar juntas en el mismo proyecto.

---

## postman-newman-skill

**Herramienta:** [Postman](https://www.postman.com/) + [Newman](https://github.com/postmanlabs/newman)
**Lenguaje de tests:** JavaScript (`pm.test()`)
**Formato de salida:** JSON (colección Postman v2.1)
**Reporte CI:** JSON + htmlextra (plugin Newman)

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

### Generar informe PDF

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
**Lenguaje de tests:** Hurl DSL (texto plano)
**Formato de salida:** `.hurl` (diff-friendly en git)
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

# Binario estático (cualquier plataforma)
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

## jmeter-skill

**Herramienta:** [Apache JMeter](https://jmeter.apache.org/) 5.6+
**Lenguaje de tests:** XML (`.jmx`) + CSV de datos
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
jmeter --version
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

### Generar informe PDF

```bash
pip install reportlab pandas

python reporter/jmeter_report.py \
  --results results/R_MI_API.jtl \
  --api-name "Mi API" \
  --threads 1000 \
  --loops 30 \
  --author "Nombre — email@empresa.com" \
  --repo-url "https://github.com/org/repo" \
  --api-version "v1.0.0"
```

→ [Documentación completa](./jmeter-skill/README.md)

---

## Instalación completa del stack

```bash
npx skills add aiquaa-labs/postman-newman-skill
npx skills add aiquaa-labs/hurl-skill
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
| `P_` | Plan de prueba JMeter `.jmx` | jmeter |
| `D_` | Datos CSV JMeter `.csv` | jmeter |
| `R_` | Resultados JMeter `.jtl` | jmeter |
| `Y_` | Pipeline CI `.yml` (Azure / GitHub) | todas |
| `INFORME_DE_AUT_` | Informe PDF funcional | postman-newman |
| `INFORME_PERF_` | Informe PDF rendimiento | jmeter |

---

## Características comunes del stack

- **Context Intake** — el agente pregunta URL, endpoints, auth y datos antes de generar. Nunca inventa campos.
- **Caveman mode** — salidas comprimidas (~75% menos tokens) sin perder precisión técnica. Activar con `/caveman`.
- **Informe PDF** — cada skill genera su propio PDF con portada, métricas y detalle. Python + ReportLab.
- **Azure Pipelines ready** — todos los templates YML usan `ubuntu-latest` y `PublishBuildArtifacts@1`.
- **Sin hardcodeo** — URLs, tokens y credenciales siempre en variables. Nunca en los archivos generados.

---

## Estructura del monorepo

```
aiquaa-labs/
├── postman-newman-skill/    → Postman + Newman — pruebas funcionales GUI
├── hurl-skill/              → Hurl — pruebas funcionales declarativas
├── jmeter-skill/            → JMeter — pruebas de rendimiento y estrés
└── README.md                → este archivo
```

---

## Créditos

Creado por [aiquaa](https://aiquaa.com/) — *Saber es calidad*

Skills de caveman basadas en [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) — MIT License.

## Licencia

MIT
