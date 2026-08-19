# Manejo explícito de errores

Los objetos procedurales deben declarar cómo manejan o propagan errores. Esta regla inicial es una aproximación ajustable a las convenciones internas.

```dbtest-rule
{
  "id": "DB-ERR-001",
  "severity": "warning",
  "appliesTo": ["procedure", "function", "package"],
  "mode": "require",
  "pattern": "\\bEXCEPTION\\b",
  "flags": "i",
  "message": "Revisar que exista una estrategia explícita de manejo de errores."
}
```
