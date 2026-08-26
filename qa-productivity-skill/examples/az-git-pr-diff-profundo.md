# Ejemplo — diff de PR con validación profunda

Simula la salida combinada de `az devops invoke --area git --resource
pullrequestiterationchanges` + `az devops invoke --area git --resource items` para el PR #8803
("Automatiza TC-4104 login portal web"), aplicando la heurística de
`validation-depth-heuristics.md`.

## Archivos cambiados (PR #8803)

```
T_LoginPortal.spec.ts   (nuevo)
pages/LoginPage.ts       (nuevo)
```

## Contenido relevante de `T_LoginPortal.spec.ts`

```typescript
import { test, expect } from '@playwright/test';
import { LoginPage } from '../pages/LoginPage';
import { verificarEnBaseDeDatos } from '../support/sandbox-db';

test('login exitoso', async ({ page, request }) => {
  const login = new LoginPage(page);
  await login.goto();
  await login.ingresarCredenciales('cliente01', process.env.CLIENTE01_PASSWORD!);

  const response = await login.submit();
  expect(response.status()).toBe(200);

  const body = await response.json();
  expect(body.usuario.estado).toBe('activo');
  expect(body.token).toBeTruthy();

  const sesion = await verificarEnBaseDeDatos(
    `SELECT estado FROM sesiones WHERE usuario_id = '${body.usuario.id}'`
  );
  expect(sesion.rows[0].estado).toBe('iniciada');
});
```

## Clasificación aplicada

- **Paso 1 (ubicar archivo):** matchea prefijo `T_*.spec.ts` → skill de origen
  `playwright-skill`.
- **Paso 2 (grep de señal):** hay `expect(response.status())` pero **no es el único**
  `expect` — también valida `body.usuario.estado`, `body.token`, y encadena
  `verificarEnBaseDeDatos(...)` (patrón de verificación en BD del `sandbox-skill`) para
  confirmar el resultado real de negocio (sesión iniciada), no solo el transporte HTTP.
- **Paso 3 (clasificación final):** **Profunda** — cuenta como automatización de calidad en el
  informe de Marina López.

## Qué haría que este mismo caso clasificara como Superficial

```typescript
test('login exitoso', async ({ page }) => {
  const login = new LoginPage(page);
  await login.goto();
  await login.ingresarCredenciales('cliente01', process.env.CLIENTE01_PASSWORD!);

  const response = await login.submit();
  expect(response.status()).toBe(200);
});
```
