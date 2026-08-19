# Guía de uso — flaui-skill

## Instalación

```bash
npx skills add aiquaa-labs/flaui-skill
```

Para agentes específicos:

```bash
npx skills add aiquaa-labs/flaui-skill -a cursor
npx skills add aiquaa-labs/flaui-skill -a windsurf
npx skills add aiquaa-labs/flaui-skill -a cline
```

---

## Instalar el stack localmente

```bash
dotnet new nunit -n MiApp.UiTests
cd MiApp.UiTests
dotnet add package FlaUI.Core
dotnet add package FlaUI.UIA3
dotnet add package Reqnroll.NUnit
dotnet add package NunitXml.TestLogger
dotnet add package Microsoft.Extensions.Configuration.Json
```

Reporter PDF:

```bash
pip install reportlab
```

`analyzer/ui_inventory.py` es Python stdlib puro — no necesita instalación.

---

## Comandos disponibles

| Comando | Qué hace |
|---------|----------|
| `/flaui:inventory` | Corre el analizador sobre el código y lista controles + `AutomationId` + advertencias |
| `/flaui:generate` | Genera `.feature` + steps + Window Object + tests NUnit desde un requerimiento |
| `/flaui:window` | Genera o actualiza un Window Object en `windows/` |
| `/flaui:from-pr` | Lee un Pull Request, clasifica los cambios y actualiza solo lo impactado |
| `/flaui:trace` | Genera o actualiza `MATRIZ_<PANTALLA>.md` |
| `/flaui:fix` | Analiza `TestResult.xml` + screenshot adjunto y repara el test |
| `/flaui:ci` | Genera el pipeline `Y_<NOMBRE>_flaui.yml` para Azure Pipelines |
| `/flaui:run` | Muestra los comandos `dotnet test` correctos para la suite |
| `/flaui:report` | Corre `flaui_report.py` sobre el XML y describe el PDF generado |

---

## Flujo típico — requerimiento nuevo

1. Compartir la ruta o el contenido de la pantalla (`.Designer.cs` o `.xaml`)
2. `/flaui:inventory` → confirmar qué controles tienen `AutomationId` estable
3. Compartir el requerimiento funcional (texto, doc o work item)
4. `/flaui:generate` → genera feature, steps, Window Object, tests y matriz
5. Correr `dotnet test --logger "nunit;LogFilePath=TestResult.xml"` (comando exacto vía `/flaui:run`)
6. `/flaui:report` → genera el PDF ejecutivo con la matriz de trazabilidad

## Flujo típico — cambios en un Pull Request

1. `/flaui:from-pr` con el número de PR (GitHub o Azure DevOps)
2. La skill corre `gh pr diff --name-only` (o `az repos pr show`) y el analizador acotado
   a los archivos tocados
3. Clasifica cada cambio (control nuevo / renombrado / eliminado / regla de negocio) y propone
   qué archivos actualizar
4. Confirmar antes de aplicar — nunca borra escenarios en silencio, los marca `@obsoleto`

---

## Inventario de controles UI — detalle

```bash
python analyzer/ui_inventory.py --src ./src/MiApp --format json
```

Salida por pantalla:

```json
{
  "screen": "LoginForm",
  "file": "src/MiApp/LoginForm.Designer.cs",
  "kind": "winforms",
  "controls": [
    {"field": "txtUsuario", "type": "TextBox", "automationId": "txtUsuario",
     "text": null, "stable": true}
  ],
  "warnings": []
}
```

`stable: false` → el control no tiene `Name`/`AccessibleName` (WinForms) o `x:Name`/
`AutomationProperties.AutomationId` (WPF) explícito. La skill recomienda la línea de código
exacta a agregar en la app antes de generar el locator.

---

## Informe PDF — detalle de argumentos

```bash
python reporter/flaui_report.py --results TestResult.xml [opciones]
```

| Argumento | Descripción | Default |
|---|---|---|
| `--results` | XML NUnit3 de resultados (obligatorio) | — |
| `--output` | Nombre del PDF de salida | `INFORME_UI_<APP>.pdf` |
| `--app-name` | Nombre de la aplicación | `App` |
| `--environment` | Ambiente (QA, Staging, Producción) | — |
| `--app-version` | Versión/release | — |
| `--repo-url` | URL del repositorio | — |
| `--author` | Autor de la automatización | — |
| `--pr` | Número de Pull Request de origen | — |

---

## Trazabilidad — cómo se vincula un test a un requerimiento

**Reqnroll (Gherkin):**
```gherkin
@RF-001
Escenario: Login exitoso con credenciales válidas
  ...
```

**NUnit puro:**
```csharp
[Test, Req("RF-001")]
public void Login_con_credenciales_validas() { ... }
```

Ambos se traducen a `<property name="ReqId">` / `<property name="Category">` en el
`TestResult.xml`, que `flaui_report.py` lee automáticamente — no hace falta mantener un
archivo de mapeo aparte.

---

## Pipeline Azure Pipelines

Ver `examples/Y_EXAMPLE_flaui.yml`. Requiere un **agente Windows self-hosted configurado para
correr de forma interactiva** (auto-logon + "Allow service to interact with desktop"), no el
pool hosted `windows-latest` — UIAutomation necesita una sesión de escritorio real.

---

## Créditos

Creado por [aiquaa](https://aiquaa.com/) — *Saber es calidad*
