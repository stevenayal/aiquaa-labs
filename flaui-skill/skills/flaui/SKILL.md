---
name: flaui
description: >
  Automatización de pruebas funcionales de pantallas de escritorio C# (WinForms/WPF)
  con FlaUI + Reqnroll (BDD) + NUnit. Lee requerimientos funcionales, código fuente
  de las pantallas (.Designer.cs / .xaml) y cambios de un Pull Request para generar
  o actualizar la automatización — features Gherkin, Window Objects, tests NUnit,
  matriz de trazabilidad requerimiento↔test, pipeline Azure Pipelines e informe PDF
  ejecutivo. Compatible con el stack aiquaa (caveman mode incluido).
  Usar cuando el usuario mencione "winforms", "wpf", "flaui", "reqnroll", "specflow",
  "pantalla de escritorio", "automatizar pantalla C#", "pruebas de UI de escritorio",
  "UIAutomation", "window object", o pida automatizar formularios/pantallas de una
  app de escritorio C# a partir de requerimientos, código o un PR.
  Auto-activa para cualquier flujo FlaUI: autoría, ejecución, debug, trazabilidad o CI.
---

FlaUI test write. Claude generate feature + steps + window object. Terse output. No fluff.

---

## ¿Qué es FlaUI en este contexto?

FlaUI es una librería .NET que automatiza aplicaciones Windows (WinForms, WPF, WinUI) sobre
UIAutomation (UIA3) — el mismo mecanismo que usa el Narrador de Windows. No hay driver externo
(a diferencia de WinAppDriver, deprecado) ni navegador: FlaUI habla directo con el proceso .NET
de la app bajo prueba, en el mismo lenguaje que la app.

Combinado con:
- **Reqnroll** — sucesor mantenido de SpecFlow (discontinuado). Traduce requerimientos en
  Gherkin (`.feature`, español) a steps C# ejecutables. Trazabilidad requerimiento→test directa.
- **NUnit** — runner + assertions. Para casos técnicos, data-driven y regresión que no necesitan
  la ceremonia de un escenario de negocio.

Casos de uso cubiertos por esta skill:
- **Automatización funcional de pantallas** — formularios, grillas, diálogos modales, menús
- **Trazabilidad** — cada escenario/test vinculado a un `RF-XXX` (requerimiento funcional)
- **Detección de impacto de un PR** — qué pantallas cambiaron y qué tests hay que tocar
- **Prevención de selectores frágiles** — inventario real de `AutomationId` antes de generar

No cubre: apps web (usar `playwright-skill`), apps móviles MAUI/Xamarin, WinUI 3 puro (FlaUI
soporta WinForms/WPF de forma madura; WinUI 3 es experimental — avisar si se detecta).

---

## Herramientas propias de esta skill

| Herramienta | Qué hace | Cuándo se corre |
|---|---|---|
| `analyzer/ui_inventory.py` | Parsea `.Designer.cs` / `.xaml` reales y lista controles + `AutomationId` + advertencias de selectores frágiles | Antes de generar cualquier Window Object — SIEMPRE |
| `reporter/flaui_report.py` | Lee `TestResult.xml` (NUnit3) y genera el PDF ejecutivo con matriz de trazabilidad RF↔tests | Después de correr la suite |

Ninguna de las dos requiere Windows para correr (son Python puro) — se pueden ejecutar en el
agente de CI o en la máquina del desarrollador sin depender del entorno de escritorio.

---

## Context Intake — SIEMPRE ejecutar primero

**Antes de generar cualquier archivo, recolectar contexto.** Sin excepciones.
El usuario puede dar nada, una ruta de proyecto, un requerimiento en texto, un PR o código fuente.
Identificar qué falta y preguntar — una pregunta a la vez, en orden de prioridad.

### Paso 1 — Detectar qué ya dio el usuario

| Señal | Qué aporta |
|-------|-----------|
| Ruta al `.sln` / proyecto de la app | dónde buscar `.Designer.cs` / `.xaml` para el analyzer |
| WinForms o WPF mencionado | qué parser del analyzer usar |
| Requerimiento funcional (texto, `.md`, work item pegado) | contenido del `.feature` y el `RF-XXX` |
| Número de PR (`gh pr` o Azure DevOps) | activa el flujo `/flaui:from-pr` |
| Código de la pantalla (`.Designer.cs` / `.xaml`) | correr el analyzer sobre eso directamente |
| Credenciales de prueba mencionadas | usuario/clave para variables de entorno |
| "quiero automatizar mi pantalla" sin más | casi nada — preguntar |

### Paso 2 — Preguntar lo que falta (una pregunta a la vez)

#### Prioridad 1 — Cómo se lanza la aplicación (siempre obligatoria)

> ¿Cómo se abre la aplicación bajo prueba?
> - Ruta al `.exe` compilado (ej: `bin/Release/net8.0-windows/MiApp.exe`)
> - O: se adjunta a un proceso ya corriendo (Attach por PID)
>
> Sin esto no se puede generar `AppDriver` ni correr ningún test.

#### Prioridad 2 — WinForms o WPF

> ¿La pantalla es WinForms o WPF?
> - **WinForms** → controles en `*.Designer.cs`, `AutomationId` = `Control.Name`
> - **WPF** → controles en `*.xaml`, `AutomationId` = `AutomationProperties.AutomationId` o `x:Name`
>
> Si no sabés, compartí la ruta del archivo de la pantalla y lo detecto por extensión.

#### Prioridad 3 — Requerimiento funcional

> ¿Cuál es el requerimiento a automatizar? Puede ser:
> - Texto libre ("el usuario debe poder iniciar sesión con usuario y clave")
> - Un archivo `.md`/`.docx` con la especificación
> - Un work item de Azure Boards / Jira pegado como texto
>
> Le asigno un id `RF-XXX` (o usá el que ya tenga tu proyecto) para la trazabilidad.
> Si el requerimiento tiene varios criterios de aceptación, genero un escenario por criterio.

#### Prioridad 4 — Código fuente de la pantalla

> Compartí la ruta o el contenido de:
> - WinForms: `NombrePantalla.Designer.cs`
> - WPF: `NombrePantalla.xaml`
>
> Corro `analyzer/ui_inventory.py` sobre esto para sacar los `AutomationId` reales — nunca
> invento selectores. Si un control no tiene identificador estable, te aviso antes de generar
> el Window Object y te doy la línea de código para agregarlo.

#### Prioridad 5 — Login / autenticación de la app (si aplica)

> ¿La app pide login al abrir?
> - No
> - Sí → ¿usuario y clave de test? (van a `TEST_USER` / `TEST_PASSWORD`, nunca hardcodeados)

#### Prioridad 6 — Datos y BD de prueba

> ¿El flujo depende de datos en base de datos (un pedido existente, un cliente cargado)?
> - No, todo se crea en el flujo del test
> - Sí → ¿hay una forma de resetear/sembrar esos datos antes de correr? (script SQL, API interna,
>   snapshot de BD)
>
> Sin esto, documento el test como dependiente de datos externos y lo marco en el reporte.

#### Prioridad 7 — Origen del cambio: ¿PR o requerimiento nuevo?

> ¿Esto es...
> - Un requerimiento nuevo (pantalla o flujo que no existía)
> - Cambios en un Pull Request ya abierto → activar `/flaui:from-pr` con el número
>
> Si es un PR: ¿GitHub (`gh pr`) o Azure DevOps (`az repos pr`)?

#### Prioridad 8 — Metadata del informe ejecutivo (opcional)

> Para el PDF, ¿tenés esta info? (todo opcional)
> - Nombre de la app, versión, ambiente (QA/Staging/Prod), repo, autor, número de PR

### Paso 3 — Confirmar antes de generar

```
CONTEXTO DETECTADO:
  APP:              <nombre>
  LANZAMIENTO:      <ruta .exe | Attach PID>
  TIPO UI:          <WinForms | WPF>
  REQUERIMIENTO:    <RF-XXX — descripción>
  PANTALLA:         <nombre del .Designer.cs/.xaml>
  INVENTARIO UI:    <N controles, M advertencias — ver detalle>
  LOGIN:            <sí/no — variables de entorno>
  DATOS DE PRUEBA:  <cómo se siembran/resetean o "no aplica">
  ORIGEN:           <requerimiento nuevo | PR #N (GitHub|Azure DevOps)>
  AMBIENTE:         <QA | Staging | Producción | no especificado>
  SALIDA:           F_<PANTALLA>.feature + S_<PANTALLA>_Steps.cs
                    + N_<PANTALLA>_Tests.cs (casos técnicos)
                    + windows/W_<PANTALLA>.cs
                    + MATRIZ_<PANTALLA>.md
                    + Y_<NOMBRE>_flaui.yml (si se pide CI)
                    + INFORME_UI_<NOMBRE>.pdf (tras ejecución)

¿Confirmás o corregís algo antes de que genere?
```

Esperar confirmación. Luego generar.

### Escalation rules

- Usuario dice "quiero automatizar mi pantalla" → preguntar Prioridad 1
- Usuario da ruta de pantalla sin decir WinForms/WPF → detectar por extensión, confirmar
- Usuario pide automatizar sin dar requerimiento → preguntar Prioridad 3, no inventar criterios
- Usuario menciona un número de PR → activar Prioridad 7, saltar directo a `/flaui:from-pr`
- Usuario dice "la app pide login" sin dar credenciales de test → preguntar Prioridad 5
- Usuario pide "arreglá el test roto" sin adjuntar `TestResult.xml` ni error → pedir el XML o el
  mensaje exacto de `dotnet test`
- Usuario comparte código de la pantalla sin haber corrido el analyzer → correrlo antes de generar
  cualquier Window Object, nunca generar `ByAutomationId` a ojo

---

## Protocolo anti-selector-inventado (desktop)

**El fallo #1 en suites FlaUI es un `AutomationId` que no existe en runtime.** WinForms y WPF no
garantizan que todo control tenga un identificador estable — a diferencia del rol/label semántico
de HTML, acá hay que leer el código fuente real.

### Regla de oro

**NUNCA generar `ByAutomationId(...)` sin haberlo confirmado con `analyzer/ui_inventory.py`.**
Si el analyzer no está disponible o el código fuente no fue compartido, usar el protocolo de
fallback (más abajo) y declarar explícitamente que los selectores son estimados.

### Paso 1 — Correr el analyzer

```bash
python analyzer/ui_inventory.py --src ./src/MiApp --format json
```

O acotado a los archivos que cambiaron en un PR:

```bash
gh pr diff <PR> --name-only > pr_files.txt
python analyzer/ui_inventory.py --src ./src/MiApp --changed-files pr_files.txt --format json
```

### Paso 2 — Orden de prioridad de locators

```
1. ByAutomationId("txtUsuario")                              ← MÁS ESTABLE
2. ByName("Iniciar sesión") + ByControlType(Button)           ← texto visible + tipo
3. ByClassName + ByControlType, acotado al panel/ventana padre
4. índice / posición en el árbol (FindAllChildren()[2])       ← PROHIBIDO
```

### Paso 3 — Si el analyzer marca `stable: false`

Emitir la recomendación de código en la app (no en el test) antes de generar el locator:

- **WinForms** sin `Name`/`AccessibleName` explícito:
  ```csharp
  this.btnAceptar.AccessibleName = "btnAceptar";
  ```
- **WPF** sin `x:Name` ni `AutomationProperties.AutomationId`:
  ```xml
  <Button AutomationProperties.AutomationId="btnAceptar" Content="Aceptar" />
  ```

Mientras el control siga inestable, usar el fallback de prioridad 2/3 y advertir explícitamente
en el output que ese locator puede romperse con un cambio de layout o de texto.

### Paso 4 — Protocolo cuando NO hay código fuente

```csharp
// Fallback por rol + texto — declarar como estimado
window.FindFirstDescendant(cf => cf.ByControlType(ControlType.Button)
    .And(cf.ByName("Ingresar")));
```

**Advertencia obligatoria:**
```
⚠️  SELECTORES ESTIMADOS — sin código fuente disponible.
    Corré analyzer/ui_inventory.py sobre la pantalla real antes de confiar en este test,
    o inspeccioná con FlaUInspect (https://github.com/FlaUI/FlaUInspect).
```

---

## Requerimiento → test — trazabilidad

Cada requerimiento recibe un id `RF-XXX`. Por cada requerimiento se genera:

1. **`F_<PANTALLA>.feature`** — Gherkin en español, un escenario por criterio de aceptación,
   tag `@RF-XXX` por escenario. `Reqnroll` configurado con `language: es` (ver `examples/`).
2. **`S_<PANTALLA>_Steps.cs`** — orquesta llamadas al Window Object. Cero UIAutomation directo acá.
3. **`N_<PANTALLA>_Tests.cs`** — casos técnicos/regresión y validaciones data-driven
   (`[TestCase]`) con `[Req("RF-XXX")]` (ver `support/ReqAttribute.cs`). No todo necesita ser
   Gherkin — un smoke test o un `[TestCase]` de 8 combinaciones de validación de campo no aporta
   valor como escenario de negocio.
4. **`MATRIZ_<PANTALLA>.md`** — tabla `RF | Descripción | Escenario/Test | Archivo`.

El `RF-XXX` viaja hasta el `TestResult.xml` como `<property name="ReqId">` (NUnit) o
`<property name="Category">` (tag Reqnroll) — `reporter/flaui_report.py` lo lee de ahí para
armar la matriz de trazabilidad del PDF sin ningún archivo adicional que mantener sincronizado.

---

## Flujo `/flaui:from-pr` — automatización desde un Pull Request

Objetivo: leer los cambios reales de un PR y generar/actualizar solo lo que corresponde,
no regenerar toda la suite.

### Paso 1 — Obtener el diff y la descripción

```bash
# GitHub
gh pr diff <N> --name-only
gh pr view <N> --json title,body,url

# Azure DevOps
az repos pr show --id <N> --output json
```

### Paso 2 — Correr el analyzer acotado a los archivos tocados

```bash
gh pr diff <N> --name-only > pr_files.txt
python analyzer/ui_inventory.py --src ./src --changed-files pr_files.txt --format json
```

### Paso 3 — Clasificar el cambio y decidir acción

| Cambio detectado en el diff | Acción |
|---|---|
| Control nuevo en `.Designer.cs` / `.xaml` | Nuevo escenario en el `.feature` + campo nuevo en `W_<Pantalla>.cs` |
| Control renombrado (mismo tipo, `AutomationId` distinto) | Actualizar solo `W_<Pantalla>.cs` — los `.feature`/steps no cambian |
| Control eliminado | Marcar el escenario afectado con `@obsoleto`, reportarlo — **NO borrar en silencio** |
| Regla de validación nueva en código de negocio (`.cs` fuera del Designer) | Agregar/actualizar assertion en el step o `[TestCase]` negativo correspondiente |
| Pantalla completamente nueva | Generar el set completo: feature + steps + window object + entrada en la matriz |
| Solo cambios de estilo/layout sin tocar `Name`/`AutomationId`/`x:Name` | Sin impacto — reportarlo y no tocar nada |

### Paso 4 — Salida del flujo

```
PR #<N> — <título>
ARCHIVOS ANALIZADOS: <lista de .Designer.cs / .xaml tocados>
IMPACTO DETECTADO:
  <pantalla> — <tipo de cambio> → <acción tomada>
TESTS IMPACTADOS:
  <lista de escenarios/tests que hay que correr>
REQUERIMIENTOS SIN COBERTURA DETECTADOS:
  <RF-XXX mencionado en la descripción del PR sin escenario asociado, si aplica>
ARCHIVOS GENERADOS/ACTUALIZADOS:
  <lista>
```

Si la descripción del PR menciona un `RF-XXX` que no tiene escenario/test asociado, avisarlo
explícitamente — es la señal más fuerte de que falta cobertura.

---

## Patrones de código — referencia

Los archivos completos y compilables están en `examples/` (`support/`, `windows/`,
`F_EXAMPLE_LOGIN.feature`, `S_EXAMPLE_LOGIN_Steps.cs`, `N_EXAMPLE_LOGIN_Tests.cs`). Resumen:

- **`AppDriver`** (`support/AppDriver.cs`) — `Application.Launch`/`Attach`, `UIA3Automation`,
  espera la ventana principal con `Retry.WhileNull` (nunca asume que aparece instantáneo),
  `Dispose()` cierra proceso + libera automation.
- **`UiWait`** (`support/UiWait.cs`) — `WaitForElement`, `WaitUntilClickable`, `WaitUntilGone`,
  `WaitForModal`. **Prohibido `Thread.Sleep`** — UIA es asincrónico (binding WPF, animaciones,
  carga de datos), un sleep fijo es lento cuando sobra tiempo y flaky cuando falta.
- **`W_LoginWindow`** (`windows/W_LoginWindow.cs`) — Window Object: propiedades privadas que
  resuelven el `AutomationElement` bajo demanda + métodos públicos por acción de negocio
  (`Login(usuario, clave)`), nunca exponer el árbol UIA crudo al step.
- **`ScreenshotHooks`** (`support/ScreenshotHooks.cs`) — captura automática en fallo, para
  Reqnroll (`[AfterScenario]`) y NUnit puro (`[TearDown]`); adjunta el archivo al
  `TestContext` para que llegue al `TestResult.xml` y de ahí al PDF.
- **`ReqAttribute`** (`support/ReqAttribute.cs`) — `[Req("RF-001")]` → propiedad `ReqId` en el XML.

### Window Object — plantilla

```csharp
public sealed class W_<Pantalla>
{
    private readonly Window _window;
    public W_<Pantalla>(Window window) => _window = window;

    private TextBox Campo =>
        _window.FindFirstDescendant(cf => cf.ByAutomationId("<automationId real>")).AsTextBox();

    public void AccionDeNegocio(...) { /* orquesta interacción con los controles */ }
}
```

---

## Pipeline Azure Pipelines — template estándar

Ver `examples/Y_EXAMPLE_flaui.yml` completo. Puntos clave:

- **Pool self-hosted Windows interactivo** — NO `windows-latest` hosted. UIAutomation requiere
  sesión de escritorio real (auto-logon + agente corriendo como proceso interactivo, no servicio).
- `dotnet build` **antes** de `dotnet test` — Reqnroll genera el code-behind de los `.feature`
  recién en build; si se salta, `dotnet test` no encuentra los steps.
- `dotnet test --logger "nunit;LogFilePath=...\TestResult.xml"` — formato NUnit3, el que lee
  `reporter/flaui_report.py`.
- `PublishTestResults@2` con `testResultsFormat: NUnit`.
- Reporter con `--pr "$(System.PullRequest.PullRequestId)"` cuando corre disparado por un PR.

---

## Fallos comunes y fixes

| Síntoma | Causa | Fix |
|---------|-------|-----|
| `ElementNotAvailableException` | Elemento existía pero la ventana se repintó/cerró | Volver a resolver el `AutomationElement` en vez de cachear la referencia |
| `FindFirstDescendant` devuelve `null` | `AutomationId` no coincide con runtime | Re-correr `analyzer/ui_inventory.py` — el Designer pudo cambiar |
| Timeout esperando ventana principal | App tarda en levantar (splash, conexión a BD) | Aumentar `AppStartupSeconds` en `appsettings.uitests.json` |
| Click no llega al control | Diálogo modal previo robó el foco | `UiWait.WaitForModal` antes de interactuar, cerrar el modal primero |
| `DataGridView`/`DataGrid` no muestra filas fuera de pantalla | Virtualización — UIA solo expone lo renderizado | Hacer `ScrollIntoView` antes de buscar la celda |
| Tests pasan local, fallan en el agente CI | Agente corre como servicio, no interactivo | Configurar el servicio del Azure Pipelines Agent con "Allow service to interact with desktop" o auto-logon |
| `dotnet test` no encuentra los steps de Reqnroll | Faltó `dotnet build` antes de `dotnet test`, o falta el `Generator` en el `.csproj` | Verificar `<Generator>ReqnrollSingleFileGenerator</Generator>` en el `.feature` y correr build primero |
| WPF: elemento con `x:Name` pero UIA no lo encuentra | Algunos controles no exponen `x:Name` como `AutomationId` por defecto | Agregar `AutomationProperties.AutomationId` explícito |
| Screenshot no aparece en el PDF | `TestContext.AddTestAttachment` no se llamó, o la ruta no es accesible desde donde corre el reporter | Verificar `ScreenshotHooks` conectado en `[AfterScenario]`/`[TearDown]`, y que `--results` apunte al XML con las rutas correctas |
| DPI scaling rompe coordenadas | Monitor con escalado >100% | FlaUI usa `AutomationId`, no coordenadas — si algo depende de posición, migrar a locator por id |

---

## Comandos

| Trigger | Acción |
|---------|--------|
| `/flaui:inventory` | Correr `ui_inventory.py` sobre el código y listar controles + advertencias |
| `/flaui:generate` | Generar feature + steps + window object + tests NUnit desde un requerimiento |
| `/flaui:window` | Generar o actualizar un Window Object |
| `/flaui:from-pr` | Leer un PR, mapear cambios a tests impactados, generar/actualizar |
| `/flaui:trace` | Generar o actualizar `MATRIZ_<PANTALLA>.md` |
| `/flaui:fix` | Analizar `TestResult.xml` + screenshot adjunto y reparar el test |
| `/flaui:ci` | Generar pipeline Azure Pipelines |
| `/flaui:run` | Emitir los comandos `dotnet test` correctos |
| `/flaui:report` | Correr `flaui_report.py` sobre el XML y describir el PDF resultante |

---

## Formato de salida — autoría (`/flaui:generate`)

```
INVENTARIO UI: <N controles detectados, M advertencias — ver detalle>
FEATURE:   F_<PANTALLA>.feature
STEPS:     S_<PANTALLA>_Steps.cs
TESTS:     N_<PANTALLA>_Tests.cs
WINDOW:    windows/W_<PANTALLA>.cs
MATRIZ:    MATRIZ_<PANTALLA>.md
ESCENARIOS GENERADOS:
  ✅ <RF-XXX — descripción del escenario>
SELECTORES USADOS:
  <lista de AutomationId con su origen (analyzer | estimado)>
ADVERTENCIAS:
  ⚠️  <controles sin AutomationId estable>
  💡  <recomendaciones de código en la app>
```

---

## Auto-Clarity

Salir de caveman para: hallazgos de seguridad encontrados durante la automatización (credenciales
visibles en pantalla, datos sensibles sin enmascarar), regresiones críticas que bloquean release,
explicaciones de cómo configurar el agente Azure Pipelines como proceso interactivo, y cualquier
recomendación de cambio de código en la app bajo prueba (agregar `AutomationId`) — eso siempre se
explica en claro, nunca en caveman. Retomar caveman después.

## Boundaries

Escribe `.feature`, `_Steps.cs`, `_Tests.cs`, Window Objects, `appsettings.uitests.json`,
pipelines Azure, y corre los scripts Python propios (`analyzer/`, `reporter/`).
NO ejecuta la aplicación bajo prueba ni `dotnet test` directamente — da los comandos listos.
NO inventa `AutomationId` sin haber corrido el analyzer o declarar explícitamente "estimado".
NO hardcodea credenciales, rutas de exe ni datos de prueba — siempre variables de entorno.
NO accede directamente a la base de datos de la app — siempre a través de un script/API que el
usuario provea.
NO borra escenarios en silencio cuando un control desaparece en un PR — los marca `@obsoleto`
y lo reporta.
Ante control con `stable:false` → recomendar cambio de código en la app (`AccessibleName` /
`AutomationProperties.AutomationId`), no inventar un locator frágil.
"stop flaui" o "normal mode": volver a estilo verbose.
