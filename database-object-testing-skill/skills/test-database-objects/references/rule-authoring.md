# Reglas Markdown

El runner carga todos los `.md` del directorio de reglas. El texto libre documenta la práctica para personas. Cada validación automática usa un bloque `dbtest-rule` con JSON válido.

```dbtest-rule
{
  "id": "DB-001",
  "severity": "error",
  "appliesTo": ["procedure", "function", "package"],
  "mode": "forbid",
  "pattern": "\\bCOMMIT\\b",
  "flags": "i",
  "message": "La transacción debe controlarla el consumidor."
}
```

Campos:

- `id`, `message`, `mode` y `pattern`: obligatorios.
- `mode`: `require` exige coincidencia; `forbid` la prohíbe.
- `severity`: `error` bloquea; `warning` informa.
- `appliesTo`: tipos de objeto o `*`; si falta, aplica a todos.
- `pattern` y `flags`: expresión regular de JavaScript aplicada al source retornado por `inspect` o al `statement` de la suite.

Mantener una regla por bloque. Probarla con `validate-rules` y con un source que pase y otro que falle. Las expresiones regulares no reemplazan un parser SQL; reservarlas para controles claros y auditables.
