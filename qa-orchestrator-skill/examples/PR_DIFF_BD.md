# Ejemplo — PR objeto de BD (esperado: `database-object-testing-skill`, confianza alta)

PR #171 — "Nueva vista `vw_clientes_morosos` para el módulo de cobranzas"

```
diff --git a/migrations/0042_vw_clientes_morosos.sql b/migrations/0042_vw_clientes_morosos.sql
new file mode 100644
--- /dev/null
+++ b/migrations/0042_vw_clientes_morosos.sql
@@ -0,0 +1,12 @@
+CREATE OR REPLACE VIEW qa_training.vw_clientes_morosos AS
+SELECT c.id, c.nombre, SUM(f.monto_pendiente) AS deuda_total
+FROM qa_training.clientes c
+JOIN qa_training.facturas f ON f.cliente_id = c.id
+WHERE f.estado = 'VENCIDA'
+GROUP BY c.id, c.nombre
+HAVING SUM(f.monto_pendiente) > 0;

diff --git a/rules/vw_clientes_morosos.md b/rules/vw_clientes_morosos.md
new file mode 100644
--- /dev/null
+++ b/rules/vw_clientes_morosos.md
@@ -0,0 +1,5 @@
+# Regla — vw_clientes_morosos
+
+Comparar base vs candidata: mismas filas sin orden, sin regresión de costo > 15%.
```

**Descripción del PR:** "Agrega la vista para el módulo de cobranzas (grupo 9). Necesito
comparar el comportamiento base vs candidata antes de mergear — sin acceso directo al motor,
vía el gateway REST de siempre."

**Señales esperadas:** `migrations/0042_vw_clientes_morosos.sql` (ruta
`migrations/**/*.sql`, peso 15) + `rules/vw_clientes_morosos.md` (ruta `rules/*.md`, peso 10)
+ keywords "vista", "comparar base vs candidata" en la descripción (peso 8) →
`database-object-testing-skill`, puntaje ≥15, confianza alta. Sin señales de otra capa →
única skill seleccionada. La bitácora debe registrar explícitamente que el prerrequisito
verificado es `DBTEST_*_URL` (gateway REST) — nunca se propone conexión directa al motor.
