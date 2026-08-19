# Contrato de API — aiquaa Sandbox

Base URL: `https://aiquaa-sandbox-api.vercel.app` (prod) · `http://localhost:3000` (local)

Auth: header `x-api-key` en toda ruta bajo `/api/v1/` excepto `/api/v1/docs`.
Envelope: éxito `{ "data": ... }` · error `{ "error": { code, message, details? } }`.
Ver `../skills/sandbox/SKILL.md` para rate limit, precedencia de params y datos sembrados.

Convención en este documento: `?` = opcional. Enums entre `|`.

---

## Público (sin `x-api-key`)

| Método | Path | Qué hace |
|--------|------|----------|
| GET | `/` | landing estática |
| GET | `/docs` | UI Scalar del spec OpenAPI |
| GET | `/api/v1/docs` | spec OpenAPI 3.1 en JSON |

---

## Grupo 1 — Autenticación y Acceso

| Método | Path | Body / Query | `data` de respuesta |
|--------|------|---------------|----------------------|
| POST | `/api/v1/auth/login` | `email` | `{id, nombre, email, activo}` · 400 si no existe o inactivo |
| POST | `/api/v1/auth/logout` | `usuarioId` (int > 0) | fila completa de `sesiones` · 404 si no existe el usuario |
| POST | `/api/v1/auth/forgot-password` | `email` | fila `sesiones` con `tipo_evento='password_reset_solicitado'` |
| POST | `/api/v1/auth/reset-password` | `usuarioId` | fila `sesiones` con `tipo_evento='password_reset_completado'` |

## Grupo 2 — Transferencias entre Cuentas

| Método | Path | Body / Query | `data` de respuesta |
|--------|------|---------------|----------------------|
| GET | `/api/v1/cuentas` | `usuarioId?` | array `cuentas` (LIMIT 100 sin filtro) |
| GET | `/api/v1/cuentas/{id}` | — | fila `cuentas` / 404 |
| POST | `/api/v1/transferencias` | `cuentaOrigenId`, `cuentaDestinoId`, `monto`, `descripcion?` | **201** fila `transferencias`, `estado='pendiente'` — **no mueve `cuentas.saldo`** |
| GET | `/api/v1/transferencias/{id}` | — | fila / 404 |

## Grupo 3 — Pagos de Servicios

| Método | Path | Body / Query | `data` de respuesta |
|--------|------|---------------|----------------------|
| GET | `/api/v1/facturas` | `usuarioId?`, `estado?` ∈ `pendiente\|pagada\|vencida` | array `facturas`, LIMIT 100 |
| GET | `/api/v1/facturas/{id}` | — | fila / 404 |
| POST | `/api/v1/facturas/{id}/pagar` | `metodoPago` ∈ `tarjeta\|cuenta\|efectivo` | `{factura, pago}` — transaccional con `SELECT ... FOR UPDATE`, 404 si ya estaba pagada |

## Grupo 4 — Registro de Usuario / Onboarding

| Método | Path | Body / Query | `data` de respuesta |
|--------|------|---------------|----------------------|
| POST | `/api/v1/usuarios` | `nombre`, `email`, `documentoTipo` ∈ `CI\|pasaporte\|RUC`, `documentoNumero`, `fechaNacimiento?`, `direccion?` | **201** fila `usuarios`, `kyc_estado='pendiente'` — `email` y `documentoNumero` son UNIQUE |
| GET | `/api/v1/usuarios/{id}` | — | fila / 404 |
| PATCH | `/api/v1/usuarios/{id}/kyc` | `kycEstado` ∈ `pendiente\|verificado\|rechazado` | fila actualizada / 404 |

## Grupo 5 — Tarjetas de Crédito/Débito

| Método | Path | Body / Query | `data` de respuesta |
|--------|------|---------------|----------------------|
| GET | `/api/v1/tarjetas` | `usuarioId?` | array, LIMIT 100 |
| POST | `/api/v1/tarjetas` | `usuarioId`, `tipo` ∈ `credito\|debito`, `marca` ∈ `visa\|mastercard` | **201**, `estado='activa'`, número enmascarado aleatorio |
| PATCH | `/api/v1/tarjetas/{id}/bloquear` | — | fila `estado='bloqueada'` |
| PATCH | `/api/v1/tarjetas/{id}/activar` | — | fila `estado='activa'` |

## Grupo 6 — Notificaciones y Alertas

| Método | Path | Body / Query | `data` de respuesta |
|--------|------|---------------|----------------------|
| GET | `/api/v1/notificaciones` | `usuarioId?`, `leido?` (literal `"true"`/`"false"`, **no** boolean) | array, LIMIT 100 |
| POST | `/api/v1/notificaciones` | `usuarioId`, `canal` ∈ `push\|email\|sms`, `asunto`, `mensaje` | **201**, `estado='enviada'` |
| PATCH | `/api/v1/notificaciones/{id}/leer` | — | fila `leido=true` |

## Grupo 7 — Carrito de Compras / E-commerce

| Método | Path | Body / Query | `data` de respuesta |
|--------|------|---------------|----------------------|
| GET | `/api/v1/ordenes` | `usuarioId?` | array |
| POST | `/api/v1/ordenes` | `usuarioId`, `items[]` de `{producto, cantidad, precioUnitario}` (mín 1) | **201**, orden + `items[]` — `monto` se calcula server-side, transaccional |
| GET | `/api/v1/ordenes/{id}` | — | orden con `items[]` anidado / 404 |

## Grupo 8 — Reservas / Turnos

| Método | Path | Body / Query | `data` de respuesta |
|--------|------|---------------|----------------------|
| GET | `/api/v1/reservas` | `usuarioId?` | array |
| POST | `/api/v1/reservas` | `usuarioId`, `servicio`, `fechaHora`, `notas?` | **201**, `estado='pendiente'` |
| PATCH | `/api/v1/reservas/{id}/confirmar` | — | `estado='confirmada'` |
| PATCH | `/api/v1/reservas/{id}/cancelar` | — | `estado='cancelada'` |

## Grupo 9 — Reportes y Dashboard

| Método | Path | Body / Query | `data` de respuesta |
|--------|------|---------------|----------------------|
| GET | `/api/v1/reportes/movimientos` | `usuarioId?`, `desde?`, `hasta?` | `[{tipo_movimiento, cantidad, total}]` |
| GET | `/api/v1/reportes/resumen` | `usuarioId?` | `{cantidad_movimientos, total, primero, ultimo}` |

## Grupo 10 — Administración de Roles y Permisos

| Método | Path | Body / Query | `data` de respuesta |
|--------|------|---------------|----------------------|
| GET | `/api/v1/roles` | — | 4 filas `roles` |
| GET | `/api/v1/usuarios/{id}/roles` | — | `[{id, usuario_id, role_id, activo, asignado_en, nombre, descripcion}]` (solo activos) |
| POST | `/api/v1/usuarios/{id}/roles` | `roleId` | **201**, upsert `ON CONFLICT ... DO UPDATE SET activo=true` |
| DELETE | `/api/v1/usuarios/{id}/roles/{roleId}` | — | soft-delete `activo=false` / 404 — **la fila no se borra** |

## Roster del curso (no es un grupo de práctica)

| Método | Path | Body / Query | `data` de respuesta |
|--------|------|---------------|----------------------|
| GET | `/api/v1/roster` | `email` (obligatorio, se normaliza a minúsculas y sin espacios) | `{nombre, email, grupo}` / 404 |

---

## Casos negativos ya disponibles sin crear datos

- `POST /api/v1/auth/login` con `email` de usuario id 4, 8 o 13 → 400 `VALIDATION_ERROR` (inactivo).
- Cualquier `GET .../{id}` con id inexistente → 404 `NOT_FOUND`.
- `POST /api/v1/usuarios` repitiendo `email` o `documentoNumero` sembrado → 400 `EXECUTION_ERROR` (UNIQUE).
- `POST /api/v1/facturas/{id}/pagar` sobre una factura ya pagada → 404.
- Sin header `x-api-key` en cualquier ruta protegida → 401 `UNAUTHORIZED`.
