# Control de transacciones

Los procedimientos, funciones y paquetes reutilizables no deben confirmar transacciones. El consumidor debe decidir si confirma o revierte la unidad de trabajo.

```dbtest-rule
{
  "id": "DB-TRANS-001",
  "severity": "error",
  "appliesTo": ["procedure", "function", "package", "trigger"],
  "mode": "forbid",
  "pattern": "\\bCOMMIT\\b",
  "flags": "i",
  "message": "No incluir COMMIT dentro del objeto reutilizable."
}
```
