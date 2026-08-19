# Front web — convención data-testid

Repo aparte: `aiquaa-sandbox-web`. Next.js 16 + SWR, dev en `http://localhost:3001`,
deploy Vercel separado. Selector para automatización: **siempre `data-testid`, nunca texto/CSS.**

## Arquitectura relevante para pruebas E2E

- Proxy same-origin: `app/api/proxy/[...path]/route.ts` reenvía a
  `${SANDBOX_API_BASE_URL}/api/v1/...`. El browser nunca llama a la API directamente →
  **no hay CORS que sortear**, pero sí un salto de red extra a considerar en timeouts de Playwright.
- Login en dos pasos, todo en `localStorage`, sin cookies ni JWT:
  1. `/login` — pegar la `x-api-key`.
  2. `/auth/login` — email de negocio (`POST /api/v1/auth/login`).
  Un 401 en cualquier pantalla limpia la key guardada y redirige a `/login`.
- Existe `SANDBOX_DEMO_API_KEY` (modo demo, server-only) — **no usarlo para el curso**: una key
  compartida rompe el rate limit por alumno y mezcla el audit log. Cada alumno con su propia key.

## Convención `data-testid` (`lib/testids.ts`)

Patrón: `{modulo}-{elemento}[-{id}][-{accion}]`

| Patrón | Ejemplo | Uso |
|--------|---------|-----|
| `{modulo}-list` | `ordenes-list` | contenedor de la lista |
| `{modulo}-row-{id}-{accion}` | `tarjetas-row-12-bloquear` | botón de acción en una fila |
| `{modulo}-field-{name}` | `usuarios-field-email` | input de formulario |
| `{modulo}-submit` | `reservas-submit` | botón de envío |
| `{modulo}-loading` | `facturas-loading` | estado de carga |
| `{modulo}-error` | `facturas-error` | estado de error |
| `{modulo}-empty` | `notificaciones-empty` | lista vacía |

`{modulo}` es el nombre en español del módulo (`usuarios`, `tarjetas`, `ordenes`, `reservas`, ...) —
coincide con el nombre de tabla, no con el número de grupo.

## Selector Playwright recomendado

```ts
await page.getByTestId('usuarios-field-email').fill('ana.torres@example.com');
await page.getByTestId('usuarios-submit').click();
await expect(page.getByTestId('usuarios-list')).toBeVisible();
```

Nunca `page.locator('.btn-primary')` ni `page.getByText('Guardar')` — el texto cambia con el idioma
o el copy, el `data-testid` no.

## Páginas

Existe una página por cada uno de los 10 módulos, con la misma convención de testids.
Confirmar la ruta exacta con el alumno o inspeccionando el repo — este documento no fija rutas
para no quedar desactualizado si cambian; sí fija la convención de testids, que es estable.
