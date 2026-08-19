# Especificación de ampliación

El archivo JSON define la columna, el cambio, la API y los perfiles de prueba:

```json
{
  "name": "customer-display-name-impact",
  "target": { "schema": "CRM", "table": "CUSTOMER", "column": "DISPLAY_NAME" },
  "change": {
    "dataType": "VARCHAR2",
    "fromLength": 50,
    "toLength": 100,
    "lengthSemantics": "CHAR"
  },
  "targets": {
    "candidate": { "baseUrlEnv": "DBTEST_CANDIDATE_URL", "tokenEnv": "DBTEST_API_TOKEN" }
  },
  "probe": {
    "operations": ["INSERT", "UPDATE"],
    "boundaries": ["oldMax", "oldMaxPlusOne", "newMax", "newMaxPlusOne"],
    "profiles": [
      { "name": "ascii", "character": "A" },
      { "name": "unicode", "character": "Ñ" }
    ]
  }
}
```

`lengthSemantics` puede ser `CHAR` o `BYTE`. Cada perfil debe usar un solo carácter Unicode. Para `BYTE`, el runner completa el valor hasta la cantidad exacta de bytes UTF-8.

El resultado falla ante brechas de cobertura, longitudes efectivas menores, transformaciones truncantes, rechazo dentro del nuevo límite, alteración del valor o aceptación por encima del límite nuevo.
