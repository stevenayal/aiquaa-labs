# Contrato REST normalizado

La URL base y el token se leen de las variables definidas en cada target. Todas las operaciones usan `POST`, JSON y `Authorization: Bearer <token>` cuando corresponde.

## Execute

`POST /v1/database/execute`

Solicitud:

```json
{
  "object": { "schema": "CRM", "name": "PKG_CUSTOMER.GET_STATUS" },
  "objectType": "package",
  "operation": "execute",
  "arguments": { "customerId": 42 },
  "transactionMode": "rollback"
}
```

Respuesta normalizada:

```json
{
  "data": { "rows": [], "rowCount": 0, "out": { "status": "ACTIVE" } },
  "metrics": { "elapsedMs": 12, "logicalReads": 8 }
}
```

También puede enviarse `statement` y `binds` para SQL controlado. El gateway debe usar binds, listas permitidas de esquemas/operaciones y un usuario de privilegios mínimos.

## Explain

`POST /v1/database/explain`, con el mismo objeto de solicitud. Responder métricas numéricas comparables:

```json
{ "cost": 105, "cardinality": 1, "bytes": 64, "logicalReads": 9, "planHash": "abc" }
```

El gateway define cómo obtiene el plan en cada motor. No ejecutar el objeto si el motor permite explicarlo sin ejecución.

## Inspect

`POST /v1/database/inspect`

```json
{ "object": { "schema": "CRM", "name": "PKG_CUSTOMER.GET_STATUS" } }
```

```json
{ "source": "CREATE OR REPLACE ...", "metadata": { "status": "VALID" } }
```

`inspect` permite aplicar reglas estáticas. Restringir qué esquemas y objetos pueden inspeccionarse.

## Dependencies

`POST /v1/database/dependencies` descubre objetos que leen o escriben una tabla o columna y entrega invocaciones reproducibles para pruebas de impacto. La skill especializada `assess-database-column-impact` documenta el contrato completo.

## Errores

Usar un código HTTP no exitoso y una respuesta sin secretos:

```json
{ "error": { "code": "OBJECT_NOT_FOUND", "message": "Objeto no disponible" } }
```
