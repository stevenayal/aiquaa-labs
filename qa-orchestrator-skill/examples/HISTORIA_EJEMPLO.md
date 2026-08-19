# Ejemplo — historia de usuario en texto plano

**Historia:** "Como cliente del sandbox de pagos (grupo 5), quiero poder ver el historial de
mis últimas 10 transacciones en el panel web, con filtro por estado (aprobada/rechazada/
pendiente), para poder revisar mi actividad reciente sin tener que llamar al soporte.

Criterios de aceptación:
- Dado que tengo transacciones registradas, cuando entro al panel, entonces veo las últimas
  10 ordenadas por fecha descendente.
- Dado que filtro por estado 'rechazada', cuando aplico el filtro, entonces solo veo
  transacciones con `status = REJECTED`.
- El listado debe verificarse contra la base de datos del sandbox (`sql/select`) para
  confirmar que coincide con lo persistido."

**Señales esperadas:** estructura "Dado/cuando/entonces" (Given/Cuando/Entonces, peso 8) →
`bdd-skill`; mención de "panel web" (peso 6, keyword de `playwright-skill` vía "pantalla web")
→ posible señal secundaria de media confianza; mención explícita de verificar contra BD via
`sql/select` → activa el patrón de verificación en base de datos que `bdd-skill` ya conoce
(no dispara `database-object-testing-skill`, que es para objetos de BD corporativa vía
gateway REST, un caso distinto). Resultado esperado: `bdd-skill` en confianza alta,
`playwright-skill` listado en confianza media — se pregunta si el criterio de aceptación
requiere además un spec E2E fuera de BDD antes de generar ambos.
