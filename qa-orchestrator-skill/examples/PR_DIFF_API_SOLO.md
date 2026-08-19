# Ejemplo — PR solo API (esperado: `hurl-skill`, confianza alta)

PR #142 — "Agrega endpoint de reembolsos parciales al sandbox de pagos"

```
diff --git a/tests/H_PAGOS_REEMBOLSO.hurl b/tests/H_PAGOS_REEMBOLSO.hurl
new file mode 100644
--- /dev/null
+++ b/tests/H_PAGOS_REEMBOLSO.hurl
@@ -0,0 +1,18 @@
+POST {{base_url}}/api/v1/payments/{{payment_id}}/refund
+x-api-key: {{api_key}}
+Content-Type: application/json
+{
+  "amount": 500,
+  "reason": "producto defectuoso"
+}
+HTTP 200
+[Asserts]
+jsonpath "$.status" == "REFUNDED_PARTIAL"
+jsonpath "$.amount" == 500

diff --git a/tests/V_PAGOS.env b/tests/V_PAGOS.env
--- a/tests/V_PAGOS.env
+++ b/tests/V_PAGOS.env
@@ -1,3 +1,4 @@
 base_url=https://aiquaa-sandbox-api.vercel.app
 api_key={{SANDBOX_API_KEY}}
+payment_id=pay_demo_001
```

**Descripción del PR:** "Suma soporte de reembolso parcial al endpoint de pagos del sandbox
(grupo 5). Agrego el `.hurl` con el caso feliz — falta el negativo (monto mayor al pagado)."

**Señales esperadas:** `tests/H_PAGOS_REEMBOLSO.hurl` (ruta `H_*.hurl`, peso 15) y
`tests/V_PAGOS.env` (ruta `V_*.env`, peso 15) → `hurl-skill`, puntaje 30, confianza alta. Sin
señales de otra capa (no hay `.tsx`, `.sql`, `.jmx`, `.xaml` en el diff) → única skill
seleccionada.
