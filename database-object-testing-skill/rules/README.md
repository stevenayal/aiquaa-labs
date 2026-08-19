# Reglas y buenas prácticas

Agregar aquí archivos `.md` con las normas internas de base de datos. El texto puede ser documentación libre. Para que una norma también se ejecute automáticamente, incluir un bloque `dbtest-rule` según `skills/test-database-objects/references/rule-authoring.md`.

El runner recorre todos los `.md` de esta carpeta. Las reglas con severidad `error` fallan el caso; las de severidad `warning` quedan como observaciones.
