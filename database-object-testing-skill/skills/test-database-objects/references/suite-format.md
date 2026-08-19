# Formato de suite

Una suite JSON contiene `name`, `targets` y `cases`. Cada target usa nombres de variables de entorno; nunca secretos literales.

```json
{
  "name": "customer-package",
  "targets": {
    "baseline": { "baseUrlEnv": "DBTEST_BASELINE_URL", "tokenEnv": "DBTEST_TOKEN" },
    "candidate": { "baseUrlEnv": "DBTEST_CANDIDATE_URL", "tokenEnv": "DBTEST_TOKEN" }
  },
  "cases": []
}
```

Por seguridad, el informe omite las respuestas y los valores comparados. Para diagnóstico local puede habilitarse evidencia de forma explícita:

```json
{
  "reporting": {
    "includeEvidence": true,
    "includeResponses": false
  }
}
```

No habilitar `includeResponses` con datos personales o secretos. El runner nunca escribe tokens de autenticación.

Campos de un caso:

- `id`: identificador único.
- `objectType`: `sql`, `view`, `function`, `procedure`, `package` o `trigger`.
- `request`: cuerpo enviado a la API; `${ENV:NOMBRE}` inserta datos desde el entorno.
- `assertions`: validaciones contra la respuesta candidata, o contra baseline si es el único target.
- `compare.functional`: `false` para omitir; de lo contrario acepta `paths` y `unorderedRows`.
- `compare.cost`: acepta `metrics` y `thresholds`, cuyas claves son rutas JSON y valores son el incremento porcentual máximo.

Operadores de assertion: `equals`, `notEquals`, `contains`, `matches`, `greaterThan`, `greaterThanOrEqual`, `lessThan`, `lessThanOrEqual`, `exists`.

Ejemplo de costo:

```json
{
  "compare": {
    "functional": { "paths": ["$.data.out", "$.data.rows"], "unorderedRows": true },
    "cost": {
      "metrics": ["$.cost", "$.logicalReads"],
      "thresholds": { "$.cost": 10, "$.logicalReads": 15 }
    }
  }
}
```
