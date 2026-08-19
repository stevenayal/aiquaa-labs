# Ejemplo — casos ambiguos (esperado: el pipeline pregunta, nunca adivina)

## Caso A — sin señales (esperado: detener, pedir al usuario)

PR #180 — "Actualiza el README del módulo de facturación"

```
diff --git a/docs/facturacion/README.md b/docs/facturacion/README.md
--- a/docs/facturacion/README.md
+++ b/docs/facturacion/README.md
@@ -1,4 +1,6 @@
 # Módulo de facturación
+
+Actualizado con el flujo de reintentos de cobro fallido (ver diagrama).
```

**Descripción del PR:** "Solo documentación, sin cambios de código."

**Señales esperadas:** ningún archivo con ruta/extensión reconocida por el mapa de señales
(solo `.md` fuera de `rules/`), ninguna keyword de las tablas de `signal-mapping.md` en la
descripción → todas las skills en 0 → nivel "Sin señales". El pipeline se detiene, no genera
nada, y pregunta al usuario qué probar o qué archivos señalar. La bitácora queda con
`ESTADO FINAL: pendiente de confirmación`.

## Caso B — empate hurl vs postman-newman (esperado: gate de confirmación)

Historia: "Necesito automatizar la verificación funcional del nuevo endpoint de facturación
electrónica." (sin PR, sin archivos, sin mención de herramienta específica)

**Señales esperadas:** keyword "verificación funcional" no aparece en ninguna tabla de
`signal-mapping.md` con peso propio de `hurl-skill` ni `postman-newman-skill` — ninguna de
las dos junta ni siquiera el umbral de 8 por keyword genérico de "API funcional". Si el repo
objetivo tampoco tiene `.hurl` ni `*.postman_collection.json` existentes, es un empate
genuino (0 vs 0, o ambas en el mismo puntaje bajo) → gate de confirmación: preguntar
explícitamente "¿Hurl (texto plano, diff-friendly) o Postman/Newman (GUI-first, colección
JSON)?" y registrar la respuesta en la bitácora.
