# Contrato REST de dependencias

`POST /v1/database/dependencies` recibe:

```json
{
  "target": { "schema": "CRM", "table": "CUSTOMER", "column": "DISPLAY_NAME" },
  "change": { "dataType": "VARCHAR2", "fromLength": 50, "toLength": 100, "lengthSemantics": "CHAR" },
  "operations": ["INSERT", "UPDATE"],
  "includeObjectTypes": ["procedure", "package", "trigger", "view"]
}
```

La respuesta normaliza las relaciones y cómo probarlas:

```json
{
  "discoveredAt": "2026-08-19T00:00:00Z",
  "dependencies": [
    {
      "id": "CRM.PKG_CUSTOMER.UPSERT_CUSTOMER",
      "object": { "schema": "CRM", "name": "PKG_CUSTOMER.UPSERT_CUSTOMER", "type": "package" },
      "operations": ["INSERT", "UPDATE"],
      "invocations": [
        {
          "id": "insert-customer",
          "operation": "INSERT",
          "effectiveLength": 100,
          "transformations": [],
          "request": {
            "object": { "schema": "CRM", "name": "PKG_CUSTOMER.UPSERT_CUSTOMER" },
            "operation": "execute",
            "arguments": { "customerId": 900001, "displayName": "" }
          },
          "valuePath": "$.arguments.displayName",
          "resultPath": "$.data.persistedValue"
        }
      ]
    }
  ],
  "unresolved": []
}
```

## Responsabilidades del gateway

- Descubrir dependencias con metadata nativa del motor y source autorizado; en Oracle combinar diccionario de datos, dependencias, constraints y source PL/SQL.
- Diferenciar lectura, inserción y actualización.
- Resolver package/procedure hasta una operación invocable.
- Informar `effectiveLength` del parámetro o variable que transporta el dato.
- Informar transformaciones como `SUBSTR`, `CAST` o conversiones.
- Proveer fixtures sintéticos e idempotentes en `request`.
- Ejecutar `/v1/database/execute` con rollback y devolver el valor efectivamente escrito en `data.persistedValue`.
- Devolver dependencias no resolubles en `unresolved`; SQL dinámico no debe omitirse silenciosamente.
