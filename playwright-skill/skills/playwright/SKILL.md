---
name: playwright
description: >
  Automatización de pruebas E2E y de API con Microsoft Playwright. Genera tests
  en TypeScript, configuración playwright.config.ts, fixtures, page objects,
  pipelines Azure Pipelines y reportes PDF ejecutivos con capturas de pantalla
  y veredicto por suite. Compatible con el stack aiquaa (caveman mode incluido).
  Usar cuando el usuario mencione "playwright", "pruebas e2e", "end to end",
  "automatización web", "page object", "test.spec.ts", "chromium", "firefox",
  "webkit", o pida automatizar flujos de navegador o APIs con Playwright.
  Auto-activa para cualquier flujo Playwright: autoría, ejecución, debug o CI.
---

Playwright test write. Claude generate spec. Terse output. No fluff.

---

## ¿Qué es Playwright en este contexto?

Microsoft Playwright ejecuta pruebas E2E contra navegadores reales (Chromium, Firefox, WebKit)
y también pruebas de API HTTP sin navegador (`request` fixture). Es el estándar moderno para
automatización web — más rápido que Selenium, con soporte nativo para TypeScript y Azure DevOps.

Casos de uso cubiertos por esta skill:
- **E2E web** — flujos de usuario completos (login → navegar → acción → assert)
- **API testing** — requests HTTP con assertions sobre response, sin necesidad de Newman/Hurl
- **Visual testing** — comparación de capturas de pantalla (snapshot testing)
- **Component testing** — tests de componentes React/Vue aislados (Playwright CT)

---

## Context Intake — SIEMPRE ejecutar primero

**Antes de generar cualquier archivo, recolectar contexto.** Sin excepciones.
El usuario puede dar nada, una URL, un flujo descrito en texto, código fuente o una spec.
Identificar qué falta y preguntar — una pregunta a la vez, en orden de prioridad.

---

### Paso 1 — Detectar qué ya dio el usuario

| Señal | Qué aporta |
|-------|-----------|
| URL completa (`https://app.miempresa.com`) | baseURL para playwright.config.ts |
| Descripción de flujo ("el usuario hace login y ve el dashboard") | casos de prueba a generar |
| Código fuente de la página (HTML, React, Vue, Angular) | selectores reales — evitar inventar |
| Archivo `.spec.ts` existente | tests previos — expandir sin pisar |
| Archivo `playwright.config.ts` existente | configuración actual — respetar y extender |
| Page Object existente | clase a usar o extender |
| Spec OpenAPI / Swagger | endpoints para API tests sin navegador |
| Credenciales de prueba mencionadas | usuario/contraseña para fixtures de auth |
| "quiero probar mi app" sin más | casi nada — preguntar |

---

### Paso 2 — Preguntar lo que falta (una pregunta a la vez)

Trabajar en este orden. Esperar respuesta antes de pasar a la siguiente.

#### Prioridad 1 — La URL base (siempre obligatoria)

> ¿Cuál es la URL de la aplicación a testear?
> Ejemplo: `https://app.miempresa.com` o `http://localhost:4200`
>
> Si es una API sin UI, también sirve: `https://api.miempresa.com`

No continuar sin esto.

#### Prioridad 2 — Tipo de prueba

> ¿Qué tipo de prueba necesitás?
>
> - **E2E web** — automatizar flujos en el navegador (login, formularios, navegación)
> - **API** — testear endpoints HTTP sin navegador (similar a Hurl pero con TypeScript)
> - **Ambos** — flujo web + validación de API en el mismo test
> - **Visual** — comparación de capturas de pantalla (snapshot testing)

Si E2E web o ambos → continuar con Prioridad 3.
Si solo API → saltar a Prioridad 5.

#### Prioridad 3 — El flujo a automatizar

> Describí el flujo que querés automatizar en lenguaje natural.
> Ejemplo:
> - "El usuario entra a /login, ingresa usuario y contraseña, hace click en Iniciar sesión
>   y debe ver el dashboard con su nombre en el header"
> - "El usuario busca un producto, lo agrega al carrito y completa la compra"
>
> Si tenés el código fuente de la página, compartilo — extraigo los selectores reales.
> Si no, voy a usar selectores por rol y texto (más estables que IDs o clases CSS).

#### Prioridad 4 — Autenticación web

> ¿La app requiere login?
>
> - No (pública)
> - Sí → ¿tenés credenciales de prueba? (usuario y contraseña de un usuario de test)
> - Sí, con SSO / OAuth → ¿hay un bypass para tests o hay que manejar el redirect?
>
> Si hay login: genero un `auth.setup.ts` que guarda el estado de sesión en
> `playwright/.auth/user.json` y lo reutiliza en todos los tests (storageState).
> Los tests no vuelven a hacer login — corren directamente autenticados.

#### Prioridad 5 — Endpoints de API (si aplica)

> ¿Qué endpoints de API querés cubrir con Playwright?
>
> - Lista directa: `POST /api/auth/login`, `GET /api/users`
> - Spec OpenAPI / Swagger (URL o archivo)
> - Curl de ejemplo
>
> Playwright API tests usan el fixture `request` — no abren navegador, son más rápidos.

#### Prioridad 6 — Browsers a usar

> ¿En qué navegadores querés correr los tests?
>
> - Solo Chromium (más rápido, default)
> - Chromium + Firefox
> - Chromium + Firefox + WebKit (Safari) — suite completa, más lento
>
> Default si no especificás: **Chromium solamente**.

#### Prioridad 7 — Patrón de organización

> ¿Usamos Page Object Model (POM)?
>
> - **Sí** → genero clases en `pages/` con métodos por acción (recomendado para suites grandes)
> - **No** → tests directos sin abstracción (ok para suites pequeñas o pruebas rápidas)
>
> Default si no especificás: **Page Object Model**.

#### Prioridad 8 — Configuración CI

> ¿El pipeline es solo Azure Pipelines o también GitHub Actions?
>
> - Azure Pipelines
> - GitHub Actions
> - Ambos
>
> Default si no especificás: **Azure Pipelines**.

#### Prioridad 9 — Metadata del informe ejecutivo (opcional)

> Para el informe PDF ejecutivo, ¿tenés esta info? (todo opcional)
>
> - **Nombre de la aplicación** — ej: `Portal de Clientes`
> - **Versión** — ej: `v2.1.0`
> - **Link del repositorio** — ej: `https://dev.azure.com/org/repo`
> - **Autor** — ej: `Juan Pérez — juan@empresa.com`
> - **Ambiente** — ej: `QA`, `Staging`, `Producción`
>
> Si los tenés, aparecen en la portada del PDF.

---

### Paso 3 — Confirmar antes de generar

```
CONTEXTO DETECTADO:
  APP:          <nombre o descripción>
  BASE URL:     <url completa>
  TIPO:         <E2E web | API | Ambos | Visual>
  FLUJO:        <descripción del flujo a automatizar>
  AUTH:         <tipo o "ninguna">
  BROWSERS:     <Chromium | Chromium + Firefox | Suite completa>
  PATRÓN:       <Page Object Model | Tests directos>
  CI:           <Azure Pipelines | GitHub Actions | Ambos>
  AMBIENTE:     <QA | Staging | Producción | no especificado>
  VERSIÓN APP:  <versión o "no proporcionada">
  REPO:         <url o "no proporcionado">
  AUTOR:        <nombre o "anónimo">
  SALIDA:       T_<NOMBRE>.spec.ts [+ pages/<NOMBRE>Page.ts] + playwright.config.ts
                + Y_<NOMBRE>_playwright.yml + INFORME_E2E_<NOMBRE>.pdf

¿Confirmás o corregís algo antes de que genere?
```

Esperar confirmación. Luego generar.

---

### Escalation rules

- Usuario dice "quiero probar mi app" → preguntar Prioridad 1
- Usuario da URL sin describir flujo → preguntar Prioridad 2 y 3
- Usuario describe flujo sin mencionar auth → preguntar Prioridad 4
- Usuario pide API tests → preguntar Prioridad 5
- Usuario pide "arreglá el test roto" sin error → pedir output de `npx playwright test` o el mensaje exacto
- Usuario dice "ya te dije todo" con contexto incompleto → listar exactamente qué falta, de a uno
- Usuario da código fuente HTML/React → extraer selectores reales antes de generar specs

---

## Convención de nombres de archivos

**Siempre respetar este patrón. Sin excepciones.**

| Tipo | Patrón | Ejemplo |
|------|--------|---------|
| Test spec | `T_NOMBRE_DE_FLUJO.spec.ts` | `T_LOGIN.spec.ts` |
| Page Object | `pages/NombrePage.ts` | `pages/LoginPage.ts` |
| Auth setup | `auth.setup.ts` | `auth.setup.ts` |
| Config | `playwright.config.ts` | `playwright.config.ts` |
| Fixtures | `fixtures/index.ts` | `fixtures/index.ts` |
| Pipeline Azure | `Y_NOMBRE_playwright.yml` | `Y_PORTAL_playwright.yml` |
| Informe PDF | `INFORME_E2E_NOMBRE.pdf` | `INFORME_E2E_PORTAL.pdf` |

Estructura recomendada:
```
tests/
  playwright/
    T_LOGIN.spec.ts
    T_DASHBOARD.spec.ts
    T_CHECKOUT.spec.ts
    auth.setup.ts
    pages/
      LoginPage.ts
      DashboardPage.ts
    fixtures/
      index.ts
playwright.config.ts
azure-pipelines/
  Y_PORTAL_playwright.yml
results/
  playwright-report/      ← HTML report generado por Playwright
  INFORME_E2E_PORTAL.pdf  ← informe PDF ejecutivo
```

---

## Stack

- Runner: Playwright Test (`@playwright/test`)
- Lenguaje: TypeScript
- Browsers: Chromium, Firefox, WebKit
- Reporters nativos: `html`, `json`, `junit`, `list`
- Auth: `storageState` (sesión guardada, no login por test)
- CI: Azure Pipelines + GitHub Actions
- PDF: reporter Python con ReportLab + pandas

---

## Comandos

| Trigger | Acción |
|---------|--------|
| `/playwright:generate` | Generar spec `.ts` desde flujo / URL / código fuente |
| `/playwright:page` | Generar o actualizar Page Object |
| `/playwright:fix` | Analizar y reparar test fallido |
| `/playwright:ci` | Generar pipeline Azure Pipelines o GitHub Actions |
| `/playwright:auth` | Generar setup de autenticación (`auth.setup.ts`) |
| `/playwright:config` | Generar o actualizar `playwright.config.ts` |
| `/playwright:report` | Analizar resultado JSON y describir el PDF ejecutivo |

---

## Patrones de código — referencia

### playwright.config.ts estándar

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/playwright',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 4 : undefined,
  reporter: [
    ['list'],
    ['json', { outputFile: 'results/playwright-results.json' }],
    ['junit', { outputFile: 'results/playwright-junit.xml' }],
    ['html', { outputFolder: 'results/playwright-report', open: 'never' }],
  ],
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:4200',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'on-first-retry',
  },
  projects: [
    // Setup de autenticación — corre antes que los tests
    {
      name: 'setup',
      testMatch: /auth\.setup\.ts/,
    },
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        storageState: 'playwright/.auth/user.json',
      },
      dependencies: ['setup'],
    },
    {
      name: 'firefox',
      use: {
        ...devices['Desktop Firefox'],
        storageState: 'playwright/.auth/user.json',
      },
      dependencies: ['setup'],
    },
  ],
});
```

### auth.setup.ts — login una vez, reutilizar en todos los tests

```typescript
import { test as setup, expect } from '@playwright/test';
import path from 'path';

const authFile = path.join(__dirname, '../playwright/.auth/user.json');

setup('autenticar usuario de prueba', async ({ page }) => {
  await page.goto('/login');
  await page.getByRole('textbox', { name: /usuario|email/i })
    .fill(process.env.TEST_USER || 'testuser@empresa.com');
  await page.getByRole('textbox', { name: /contraseña|password/i })
    .fill(process.env.TEST_PASSWORD || 'TestPass123');
  await page.getByRole('button', { name: /iniciar sesión|login|entrar/i }).click();
  await expect(page).toHaveURL(/dashboard|home|inicio/);
  await page.context().storageState({ path: authFile });
});
```

### Page Object — LoginPage.ts

```typescript
import { type Page, type Locator } from '@playwright/test';

export class LoginPage {
  readonly page: Page;
  readonly usernameInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;
  readonly errorMessage: Locator;

  constructor(page: Page) {
    this.page = page;
    this.usernameInput = page.getByRole('textbox', { name: /usuario|email/i });
    this.passwordInput = page.getByRole('textbox', { name: /contraseña|password/i });
    this.submitButton = page.getByRole('button', { name: /iniciar sesión|login/i });
    this.errorMessage = page.getByRole('alert');
  }

  async goto() {
    await this.page.goto('/login');
  }

  async login(username: string, password: string) {
    await this.usernameInput.fill(username);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }

  async loginAndExpectDashboard(username: string, password: string) {
    await this.login(username, password);
    await this.page.waitForURL(/dashboard|home/);
  }
}
```

### Test spec E2E — T_LOGIN.spec.ts

```typescript
import { test, expect } from '@playwright/test';
import { LoginPage } from './pages/LoginPage';

test.describe('Login — happy path y casos negativos', () => {

  test('login exitoso redirige al dashboard', async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.loginAndExpectDashboard(
      process.env.TEST_USER || 'testuser@empresa.com',
      process.env.TEST_PASSWORD || 'TestPass123'
    );
    await expect(page).toHaveURL(/dashboard/);
    await expect(page.getByRole('heading', { level: 1 })).toBeVisible();
  });

  test('credenciales inválidas muestran error', async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login('usuario@invalido.com', 'claveincorrecta');
    await expect(loginPage.errorMessage).toBeVisible();
    await expect(page).toHaveURL(/login/);
  });

  test('campos vacíos muestran validación', async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.submitButton.click();
    await expect(loginPage.errorMessage.or(
      page.locator('[aria-invalid="true"]')
    )).toBeVisible();
  });

});
```

### Test spec API — T_API_USERS.spec.ts

```typescript
import { test, expect } from '@playwright/test';

test.describe('API — /api/users', () => {

  test('GET /api/users retorna lista', async ({ request }) => {
    const response = await request.get('/api/users', {
      headers: {
        'Authorization': `Bearer ${process.env.API_TOKEN}`,
      },
    });
    expect(response.status()).toBe(200);
    const body = await response.json();
    expect(Array.isArray(body)).toBeTruthy();
    expect(body.length).toBeGreaterThan(0);
  });

  test('POST /api/users crea usuario', async ({ request }) => {
    const response = await request.post('/api/users', {
      headers: { 'Authorization': `Bearer ${process.env.API_TOKEN}` },
      data: { name: 'Test User', email: `test_${Date.now()}@ejemplo.com` },
    });
    expect(response.status()).toBe(201);
    const body = await response.json();
    expect(body).toHaveProperty('id');
  });

  test('GET /api/users/:id inexistente retorna 404', async ({ request }) => {
    const response = await request.get('/api/users/id-inexistente', {
      headers: { 'Authorization': `Bearer ${process.env.API_TOKEN}` },
    });
    expect(response.status()).toBe(404);
  });

});
```

### Selectores — orden de preferencia

```typescript
// 1. Por rol (más estable — accesible)
page.getByRole('button', { name: 'Iniciar sesión' })
page.getByRole('textbox', { name: 'Email' })
page.getByRole('heading', { name: 'Dashboard' })

// 2. Por texto visible
page.getByText('Bienvenido')
page.getByLabel('Contraseña')
page.getByPlaceholder('Ingresá tu email')

// 3. Por test-id (si el equipo los usa)
page.getByTestId('login-button')

// 4. Por CSS/XPath — ÚLTIMO RECURSO
page.locator('.btn-primary')
page.locator('#login-form')

// NUNCA usar selectores frágiles sin contexto:
// page.locator('div > div:nth-child(3) > button') ← NO
```

---

## Pipeline Azure Pipelines — template estándar

```yaml
# Y_NOMBRE_playwright.yml
# Playwright E2E tests — NOMBRE APP
# Generado por skill playwright · aiquaa.com

trigger:
  branches:
    include:
      - main
      - develop

pool:
  vmImage: ubuntu-latest

variables:
  nodeVersion: '20.x'
  resultsDir: '$(Build.ArtifactStagingDirectory)/playwright-results'

steps:

  - task: NodeTool@0
    inputs:
      versionSpec: $(nodeVersion)
    displayName: Instalar Node.js

  - script: npm ci
    displayName: Instalar dependencias

  - script: npx playwright install --with-deps chromium
    displayName: Instalar browsers Playwright

  - script: mkdir -p $(resultsDir)
    displayName: Crear directorio de resultados

  - script: |
      npx playwright test \
        --reporter=list,json,junit,html
    displayName: Ejecutar tests Playwright
    continueOnError: true
    env:
      BASE_URL: $(baseUrl)
      TEST_USER: $(testUser)
      TEST_PASSWORD: $(testPassword)
      API_TOKEN: $(apiToken)
      CI: true

  - script: |
      cp results/playwright-results.json $(resultsDir)/ || true
      cp results/playwright-junit.xml $(resultsDir)/ || true
      cp -r results/playwright-report $(resultsDir)/ || true
    displayName: Copiar resultados
    condition: always()

  - task: PublishTestResults@2
    condition: always()
    inputs:
      testResultsFormat: JUnit
      testResultsFiles: '$(resultsDir)/playwright-junit.xml'
      testRunTitle: 'Playwright E2E — NOMBRE APP'
      failTaskOnFailedTests: true
    displayName: Publicar resultados en Azure Test Plans

  - script: |
      pip install reportlab pandas --quiet
      python reporter/playwright_report.py \
        --results $(resultsDir)/playwright-results.json \
        --output $(resultsDir)/INFORME_E2E_NOMBRE.pdf \
        --app-name "NOMBRE APP" \
        --environment "QA"
    displayName: Generar informe PDF ejecutivo
    condition: always()

  - task: PublishBuildArtifacts@1
    condition: always()
    inputs:
      pathToPublish: $(Build.ArtifactStagingDirectory)
      artifactName: playwright-results
    displayName: Subir artefactos
```

---

## Formato de salida — análisis de resultados (`/playwright:report`)

```
FILE: playwright-results.json
APP:  <nombre>
ENV:  <ambiente>

SUITES:
  ✅ <suite> — <n> passed
  ❌ <suite> — <n> passed / <n> failed
  ⏭ <suite> — <n> skipped

MÉTRICAS:
  Total tests:   <n>
  Passed:        <n> (<n>%)
  Failed:        <n> (<n>%)
  Skipped:       <n>
  Duration:      <n>s

FALLOS (si hay):
  ❌ <test name>
     ARCHIVO: <spec>:<línea>
     ERROR:   <mensaje>
     FIX:     <acción en una línea>

VEREDICTO: ✅ SUITE VERDE | ⚠️ FALLOS MENORES | ❌ REGRESIÓN CRÍTICA
```

## Formato de salida — autoría (`/playwright:generate`)

```
SPEC: T_<NOMBRE>.spec.ts
PAGE: pages/<NOMBRE>Page.ts (si POM)
TESTS GENERADOS:
  ✅ <descripción del test>
  ✅ <descripción del test>
  ✅ <descripción del test>
SELECTORES USADOS:
  <lista de locators — rol/texto/testid>
NOTAS:
  <advertencias sobre selectores inferidos / auth / env vars>
```

---

## Fallos comunes y fixes

| Síntoma | Causa | Fix |
|---------|-------|-----|
| `locator.click: element not found` | Selector incorrecto o elemento no visible | Usar `getByRole` en lugar de CSS; agregar `waitFor` |
| `Timeout 30000ms exceeded` | Página no cargó o acción bloqueada | Aumentar `timeout` en config o revisar la URL base |
| `storageState file not found` | Auth setup no corrió o path incorrecto | Verificar que el proyecto `setup` sea dependencia |
| Tests pasan local, fallan en CI | Variables de entorno no seteadas en pipeline | Verificar `env:` en el step de ejecución |
| `net::ERR_CONNECTION_REFUSED` | Servicio no levantado en CI | Agregar step de health check antes de los tests |
| Capturas en blanco | Acción demasiado rápida antes de render | Agregar `await expect(locator).toBeVisible()` antes |
| Tests lentos en CI | Demasiados workers o browsers | Reducir `workers` en `playwright.config.ts` para CI |
| `page.goto` falla con 401 | Token o cookie expirado | Verificar `storageState` o regenerar auth |
| Error en `json reporter` | Path de output no existe | Crear directorio `results/` antes de correr |

---

## Auto-Clarity

Salir de caveman para: hallazgos de seguridad encontrados durante E2E (XSS, datos expuestos),
regresiones críticas que bloquean el release, recomendaciones de arquitectura de tests.
Retomar caveman después.

## Boundaries

Escribe specs `.spec.ts`, Page Objects, `playwright.config.ts`, `auth.setup.ts`,
fixtures, comandos CLI, pipelines Azure/GitHub.
NO ejecuta Playwright — da los comandos listos para ejecutar.
NO inventa selectores sin ver el HTML — pregunta o usa roles genéricos con advertencia.
NO inventa credenciales — las pone como variables de entorno.
"stop playwright" o "normal mode": volver a estilo verbose.
