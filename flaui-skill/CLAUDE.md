# flaui-skill — CLAUDE.md

## Project

Automatización funcional de pantallas de escritorio C# (WinForms/WPF) skill. Owned by aiquaa-labs.
Lives at `Z:\Proyectos\aiquaa-labs\flaui-skill`.
Complementary to postman-newman-skill (funcional JSON), hurl-skill (declarativo CLI),
playwright-skill (E2E web) y jmeter-skill (rendimiento). FlaUI = escritorio Windows en C#.

## Structure

```
skills/flaui/       ← skill principal (context intake + generación de tests)
analyzer/            ← ui_inventory.py — inventario de controles reales (WinForms/WPF)
reporter/            ← flaui_report.py — PDF ejecutivo + matriz de trazabilidad (NUnit3 XML)
examples/            ← F_, S_, N_, W_, support/, fixtures/, Y_, .csproj, appsettings
docs/                ← guía de uso en español
.github/workflows/   ← CI para la skill en sí (valida analyzer, reporter y YML)
```

## File naming convention

- Feature Gherkin:      `F_NOMBRE_DE_PANTALLA.feature`
- Step definitions:     `S_NOMBRE_DE_PANTALLA_Steps.cs`
- Test NUnit puro:      `N_NOMBRE_DE_PANTALLA_Tests.cs`
- Window Object:        `windows/W_NombrePantalla.cs`
- Matriz trazabilidad:  `MATRIZ_NOMBRE_DE_PANTALLA.md`
- Pipeline Azure:       `Y_NOMBRE_flaui.yml`
- Informe PDF:          `INFORME_UI_NOMBRE.pdf`

## Key rules

- SIEMPRE correr `analyzer/ui_inventory.py` sobre el código real antes de generar un
  Window Object — nunca inventar `AutomationId`
- Orden de locators: `ByAutomationId` > `ByName+ByControlType` > `ByClassName acotado` >
  posición/índice (PROHIBIDO)
- Cada escenario/test lleva un `RF-XXX` — vía tag `@RF-XXX` (Reqnroll) o `[Req("RF-XXX")]`
  (NUnit puro, `support/ReqAttribute.cs`)
- Nunca hardcodear credenciales, rutas de exe ni datos de prueba — siempre variables de entorno
  (`APP_EXE_PATH`, `TEST_USER`, `TEST_PASSWORD`)
- Prohibido `Thread.Sleep` — usar `support/UiWait.cs` (`Retry.WhileNull/WhileTrue`)
- Screenshot automático en fallo vía `support/ScreenshotHooks.cs` — se adjunta al
  `TestContext` para llegar al `TestResult.xml` y de ahí al PDF
- Pipeline: agente Windows self-hosted **interactivo** (no `windows-latest` hosted) —
  UIAutomation no funciona en sesión de servicio ni headless
- Reporter: mismo patrón visual que `playwright-skill/reporter/playwright_report.py`
  (misma paleta/estilos), parser distinto (NUnit3 XML) + sección nueva de trazabilidad
- Veredicto: `failed=0` y sin RF sin cobertura = VERDE | `failed=0` con gaps = VERDE CON GAPS |
  `pass_rate>=85%` = FALLOS MENORES | resto = REGRESIÓN CRÍTICA
