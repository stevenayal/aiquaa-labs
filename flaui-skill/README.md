# flaui-skill

> Automatización funcional de pantallas de escritorio C# (WinForms/WPF) — powered by [aiquaa](https://aiquaa.com/)

Skill para Claude Code, Cursor, Windsurf y más de 40 agentes de IA. Lee requerimientos
funcionales, código fuente de las pantallas y cambios de un Pull Request para generar features
Gherkin (Reqnroll), Window Objects, tests NUnit, matriz de trazabilidad, pipeline Azure Pipelines
e informe PDF ejecutivo.

---

## ¿Qué problema resuelve?

Automatizar pantallas de escritorio C# a mano implica: descubrir los `AutomationId` reales
en el código (o inventarlos y que el test se rompa en runtime), escribir el Window Object,
mapear cada test a su requerimiento para trazabilidad de negocio, y armar el pipeline con
un agente Windows interactivo — todo antes de escribir el primer `[Test]`. Esta skill:

1. **Lee el código real de la pantalla** (`.Designer.cs` / `.xaml`) con un analizador propio
   y extrae los `AutomationId` reales — nunca genera un selector inventado.
2. **Lee un Pull Request** y clasifica qué cambió (control nuevo, renombrado, eliminado, regla
   de negocio nueva) para actualizar solo lo que corresponde.
3. **Vincula cada test a un requerimiento funcional (`RF-XXX`)** y genera un PDF ejecutivo con
   matriz de trazabilidad, para que negocio vea qué está cubierto y qué no.

---

## ¿Qué incluye?

| Componente | Descripción |
|------------|-------------|
| `skills/flaui/SKILL.md` | Instrucciones del agente — context intake, generación, `/flaui:from-pr` |
| `analyzer/ui_inventory.py` | Inventario de controles reales — WinForms (`.Designer.cs`) y WPF (`.xaml`), sin dependencias |
| `reporter/flaui_report.py` | PDF ejecutivo desde `TestResult.xml` (NUnit3) con matriz de trazabilidad RF↔tests |
| `examples/` | Proyecto de ejemplo completo: `.feature`, steps, Window Object, tests NUnit, `.csproj`, pipeline |

---

## Instalación

```bash
# Claude Code
npx skills add aiquaa-labs/flaui-skill

# Cursor
npx skills add aiquaa-labs/flaui-skill -a cursor

# Windsurf
npx skills add aiquaa-labs/flaui-skill -a windsurf

# Cualquier otro agente
npx skills add aiquaa-labs/flaui-skill
```

---

## Instalar el stack localmente

```bash
# Proyecto de tests
dotnet new nunit -n MiApp.UiTests
cd MiApp.UiTests
dotnet add package FlaUI.Core
dotnet add package FlaUI.UIA3
dotnet add package Reqnroll.NUnit
dotnet add package NunitXml.TestLogger

# Reporter PDF
pip install reportlab
```

`analyzer/ui_inventory.py` no requiere instalación — es Python stdlib puro.

---

## Uso rápido

```
/flaui:inventory   → correr el analizador sobre el código y listar controles + advertencias
/flaui:generate     → generar feature + steps + window object + tests desde un requerimiento
/flaui:window       → generar o actualizar un Window Object
/flaui:from-pr      → leer un PR, mapear cambios a tests impactados, generar/actualizar
/flaui:trace        → generar o actualizar la matriz de trazabilidad
/flaui:fix          → analizar TestResult.xml + screenshot y reparar
/flaui:ci           → generar pipeline Azure Pipelines
/flaui:run          → mostrar comandos dotnet test correctos
/flaui:report       → analizar el XML y generar el PDF ejecutivo
```

La skill pregunta antes de generar: cómo se lanza la app, WinForms o WPF, requerimiento a
automatizar, código de la pantalla, login, datos de prueba y origen del cambio (requerimiento
nuevo o PR).

---

## Convención de nombres

| Tipo | Patrón | Ejemplo |
|------|--------|---------|
| Feature Gherkin | `F_NOMBRE_DE_PANTALLA.feature` | `F_LOGIN.feature` |
| Step definitions | `S_NOMBRE_DE_PANTALLA_Steps.cs` | `S_LOGIN_Steps.cs` |
| Test NUnit puro | `N_NOMBRE_DE_PANTALLA_Tests.cs` | `N_LOGIN_Tests.cs` |
| Window Object | `windows/W_NombrePantalla.cs` | `windows/W_LoginWindow.cs` |
| Matriz de trazabilidad | `MATRIZ_NOMBRE_DE_PANTALLA.md` | `MATRIZ_LOGIN.md` |
| Pipeline CI | `Y_NOMBRE_flaui.yml` | `Y_PORTAL_flaui.yml` |
| Informe PDF | `INFORME_UI_NOMBRE.pdf` | `INFORME_UI_PORTAL.pdf` |

---

## Inventario de controles UI

```bash
python analyzer/ui_inventory.py --src ./src/MiApp --format json
python analyzer/ui_inventory.py --src ./src/MiApp --format md

# Acotado a los archivos que cambiaron en un PR
gh pr diff 123 --name-only > pr_files.txt
python analyzer/ui_inventory.py --src ./src/MiApp --changed-files pr_files.txt --format json
```

Marca `stable: false` en cualquier control sin `AutomationId`/`AccessibleName` (WinForms) o sin
`x:Name`/`AutomationProperties.AutomationId` (WPF) explícito, con la recomendación de código
exacta para volverlo estable.

---

## Informe PDF ejecutivo

```bash
pip install reportlab

python reporter/flaui_report.py \
  --results     TestResult.xml \
  --app-name    "Sistema de Gestión" \
  --environment "QA" \
  --app-version "v3.2.0" \
  --author      "Nombre — email@empresa.com" \
  --repo-url    "https://dev.azure.com/org/repo" \
  --pr          "123"
```

El informe incluye portada con estadísticas, veredicto automático, **matriz de trazabilidad
Requerimiento↔Tests** y detalle de fallos con captura de pantalla embebida.

| Veredicto | Condición |
|-----------|-----------|
| ✅ Suite verde | 0 fallos, sin RF sin cobertura |
| ⚠️ Suite verde con gaps | 0 fallos, pero hay RF sin ningún test ejecutado |
| ⚠️ Fallos menores | Tasa de éxito ≥ 85% |
| ❌ Regresión crítica | Tasa de éxito < 85% |

Salida: `INFORME_UI_NOMBRE.pdf`

---

## Estructura recomendada

```
tests/flaui/
  F_LOGIN.feature
  S_LOGIN_Steps.cs
  N_LOGIN_Tests.cs
  windows/
    W_LoginWindow.cs
  support/
    AppDriver.cs
    UiWait.cs
    ScreenshotHooks.cs
    ReqAttribute.cs
  appsettings.uitests.json
MiApp.UiTests.csproj
results/
  TestResult.xml
  screenshots/
  INFORME_UI_PORTAL.pdf
azure-pipelines/
  Y_PORTAL_flaui.yml
MATRIZ_LOGIN.md
```

---

## Créditos

Creado por [aiquaa](https://aiquaa.com/) — *Saber es calidad*

## Licencia

MIT
