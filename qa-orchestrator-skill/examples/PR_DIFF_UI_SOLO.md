# Ejemplo — PR solo UI web (esperado: `playwright-skill`, confianza alta)

PR #158 — "Agrega botón de cancelar suscripción en el panel de cuenta"

```
diff --git a/src/components/AccountPanel.tsx b/src/components/AccountPanel.tsx
--- a/src/components/AccountPanel.tsx
+++ b/src/components/AccountPanel.tsx
@@ -40,6 +40,13 @@ export function AccountPanel() {
   return (
     <section>
       <h2>Mi cuenta</h2>
+      <button
+        data-testid="btn-cancelar-suscripcion"
+        onClick={handleCancelSubscription}
+      >
+        Cancelar suscripción
+      </button>
+      {showConfirmModal && (
+        <div data-testid="modal-confirmar-cancelacion">...</div>
+      )}
     </section>
   );
 }
```

**Descripción del PR:** "El usuario ahora puede cancelar su suscripción desde el panel de
cuenta — pide confirmación en un modal antes de ejecutar la baja. Flujo E2E: click en botón →
modal → confirmar → toast de éxito."

**Señales esperadas:** `src/components/AccountPanel.tsx` (ruta `src/components/**/*.tsx`, peso
15) + `data-testid` nuevo (`btn-cancelar-suscripcion`, `modal-confirmar-cancelacion`, peso 12)
+ keyword "flujo E2E" en la descripción (peso 8) → `playwright-skill`, puntaje ≥15, confianza
alta. Sin señales de API/BD/perf/escritorio en el diff → única skill seleccionada.
