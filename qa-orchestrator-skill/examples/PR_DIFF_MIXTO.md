# Ejemplo — PR mixto API + UI (esperado: multi-skill, `hurl-skill` + `playwright-skill`)

PR #163 — "Muestra el nuevo campo `fecha_estimada_entrega` en el detalle de pedido"

```
diff --git a/tests/H_PEDIDOS_DETALLE.hurl b/tests/H_PEDIDOS_DETALLE.hurl
--- a/tests/H_PEDIDOS_DETALLE.hurl
+++ b/tests/H_PEDIDOS_DETALLE.hurl
@@ -8,6 +8,7 @@ HTTP 200
 [Asserts]
 jsonpath "$.order_id" == "{{order_id}}"
 jsonpath "$.status" exists
+jsonpath "$.fecha_estimada_entrega" exists

diff --git a/src/components/OrderDetail.tsx b/src/components/OrderDetail.tsx
--- a/src/components/OrderDetail.tsx
+++ b/src/components/OrderDetail.tsx
@@ -22,6 +22,9 @@ export function OrderDetail({ order }: Props) {
   return (
     <article>
       <h3>Pedido #{order.id}</h3>
+      <p data-testid="fecha-estimada-entrega">
+        Entrega estimada: {formatDate(order.fecha_estimada_entrega)}
+      </p>
     </article>
   );
 }
```

**Descripción del PR:** "El backend ya expone `fecha_estimada_entrega` en el detalle de
pedido (grupo 7, logística). Este PR agrega la assertion en el `.hurl` existente y muestra el
dato en el componente de detalle."

**Señales esperadas:**
- `tests/H_PEDIDOS_DETALLE.hurl` (ruta `H_*.hurl`, peso 15) → `hurl-skill`.
- `src/components/OrderDetail.tsx` (ruta `src/components/**/*.tsx`, peso 15) + `data-testid`
  nuevo (peso 12) → `playwright-skill`.

Ambas quedan en confianza alta (≥15) → **selección múltiple**: se generan y ejecutan las dos,
`hurl-skill` primero (tocó el archivo existente) y `playwright-skill` después, en el orden en
que fueron puntuadas. El informe consolidado lista ambas con su propio veredicto.
