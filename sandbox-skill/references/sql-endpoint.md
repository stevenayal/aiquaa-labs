# Endpoints de SQL — verificación en base de datos

Dos endpoints para cerrar el ciclo **API → BD** en cualquier prueba (funcional, BDD, rendimiento).
Ambos son `POST`, ambos reciben SQL crudo en el body, ambos requieren `x-api-key`.

| Método | Path | Rol de BD | Uso |
|--------|------|-----------|-----|
| POST | `/api/v1/sql/select` | `qa_reader` (solo SELECT) | verificar estado tras una acción |
| POST | `/api/v1/sql/update` | `qa_writer` (UPDATE + SELECT) | mutar datos directamente, para armar fixtures |

## Body

```json
{
  "sql": "SELECT id, nombre, email FROM usuarios WHERE activo = $1",
  "params": [true]
}
```

- `sql`: string, 1 a 5000 caracteres. **Una sola sentencia** (un `;` final se tolera, más de uno no).
- `params`: array opcional, máx 50 elementos. Placeholders `$1, $2, ...` estilo Postgres.
- La cantidad de `$N` en el SQL debe **coincidir exactamente** con `params.length`, o 400.

## Respuesta

```json
{ "data": [ { "id": 1, "nombre": "Ana Torres", "email": "ana.torres@example.com" } ], "rowCount": 1 }
```

`rowCount` es el dato que no tienen los endpoints REST — úsalo para assertions de cantidad
("debe existir exactamente 1 fila", "no debe existir ninguna").

## Guardrails — en qué orden se valida

1. `x-api-key` → 401 si falta o es inválida.
2. Rate limit (30/min) → 429.
3. Body con zod → 400 si `sql` vacío, muy largo, o `params` mal formado.
4. **Validación SQL** (`node-sql-parser`, dialecto PostgreSQL):
   - No parsea → 400 `VALIDATION_ERROR`, nunca revienta el server.
   - `statement.type` debe ser `select` en `/sql/select` y `update` en `/sql/update`.
   - **`/sql/update` exige `WHERE`** — sin cláusula, 400 (`"UPDATE statements must include a WHERE clause."`).
   - **Whitelist de tablas** — schema debe ser `qa_training` (o vacío) y la tabla debe estar en:
     `usuarios, sesiones, cuentas, transferencias, facturas, pagos, tarjetas, notificaciones,
     ordenes, items_orden, reservas, movimientos, roles, usuario_roles, tickets`.
     Cualquier otra tabla (incluidas `api_keys` y `sql_audit_log`) → 400.
5. Ejecución en Postgres. Error de BD → 400 `EXECUTION_ERROR` con el **mensaje crudo de Postgres**
   (útil para enseñar a leer errores de SQL reales).
6. **Cada intento, éxito o fallo, queda registrado en `public.sql_audit_log`** — no se puede
   verificar sin dejar rastro, y ese rastro es en sí mismo un buen caso de prueba.

## Qué NO está bloqueado (a propósito, para exploración en clase)

- Subqueries, CTEs y JOINs **entre tablas whitelisteadas**.
- Funciones como `pg_sleep()` — útil para ilustrar timeouts en pruebas de rendimiento.
- `SELECT` sin `LIMIT` — puede devolver toda la tabla.
- `UPDATE` de filas de cualquier alumno — no hay aislamiento por API key en los datos.

## Defensa en profundidad (documentado, no hace falta explicarlo en detalle en clase)

Los roles `qa_reader`/`qa_writer` no tienen permisos en el schema `public` aunque el AST
whitelist tuviera un hueco: no pueden tocar `api_keys` ni `sql_audit_log` ni con acceso directo.
RLS activo en todas las tablas de `qa_training`.

---

## Patrón de verificación API → BD

```
1. Acción       POST /api/v1/ordenes  { usuarioId, items:[...] }  →  guardar data.id
2. Verificación POST /api/v1/sql/select
                { "sql": "SELECT monto FROM ordenes WHERE id = $1", "params": [id] }
3. Assert       rowCount === 1  &&  data[0].monto === sum(items)
```

Cada paso de verificación es **una petición más contra el rate limit de 30/min** — contarla al
diseñar un escenario, sobre todo en BDD (una verificación por step) y rendimiento.

## Casos de verificación recomendados (con su porqué)

| Acción REST | Verificar en BD | Por qué enseña algo |
|---|---|---|
| `POST /api/v1/transferencias` | `transferencias.estado='pendiente'` **y** `cuentas.saldo` sin cambios | la API no mueve saldo — bug clásico invisible en la UI |
| `POST /api/v1/ordenes` | `ordenes.monto` = `SUM(items_orden.cantidad * items_orden.precio_unitario)` | el monto se calcula en el servidor, no lo manda el cliente |
| `PATCH /api/v1/usuarios/{id}/kyc` | `usuarios.kyc_estado` | confirmar que lo devuelto por la API es lo persistido |
| `POST /api/v1/facturas/{id}/pagar` | fila nueva en `pagos` + `facturas.estado='pagada'` | transacción con `SELECT ... FOR UPDATE` — el segundo intento da 404 |
| `DELETE .../usuarios/{id}/roles/{roleId}` | `usuario_roles.activo=false`, **la fila sigue existiendo** | soft delete, no borrado físico |

## Ejemplos listos

```json
// ¿cuántos usuarios activos hay?
{ "sql": "SELECT COUNT(*) AS total FROM usuarios WHERE activo = $1", "params": [true] }

// última notificación de un usuario
{ "sql": "SELECT * FROM notificaciones WHERE usuario_id = $1 ORDER BY created_at DESC LIMIT 1", "params": [7] }

// fixture: reactivar un usuario para una corrida de prueba (requiere /sql/update)
{ "sql": "UPDATE usuarios SET activo = $1 WHERE id = $2", "params": [true, 4] }
```

## Caso que debe fallar (para enseñar la whitelist)

```json
{ "sql": "SELECT * FROM api_keys" }
```
→ 400 `VALIDATION_ERROR` — tabla fuera del schema `qa_training`.
