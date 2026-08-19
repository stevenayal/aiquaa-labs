# Generado por skill ocr-bdd a partir de un documento de requisitos escaneado.
# Cada Scenario lleva un comentario "# criterio: <requisito>" — usado por
# bdd_report.py (skill bdd) para armar la matriz de trazabilidad en el PDF.
# Ver TRAZA_EJEMPLO.md para la matriz completa requisito → escenario de este ejemplo.

@grupo-3 @api @db
Feature: Pagos de Servicios — extraído de documento de requisitos

  Background:
    Given que tengo una API key válida

  # criterio: El usuario puede pagar una factura con tarjeta o efectivo.
  Scenario Outline: Pago de factura con método válido
    When hago POST a "/api/v1/facturas/1/pagar" con body:
      """
      { "metodoPago": "<metodo>" }
      """
    Then la respuesta tiene status 200

    Examples:
      | metodo   |
      | tarjeta  |
      | efectivo |

  # TODO: confirmar con el docente — el documento original menciona un tercer método
  # de pago ilegible en el escaneo. El contrato del sandbox (skill sandbox) permite
  # "cuenta" además de tarjeta/efectivo — confirmar si es el método faltante antes
  # de agregar el escenario correspondiente.

  # criterio: Si la factura ya fue pagada, el sistema no debe reprocesar el pago.
  @negativo
  Scenario: Pago de una factura ya pagada
    Given que la factura con id "1" ya fue pagada
    When hago POST a "/api/v1/facturas/1/pagar" con body:
      """
      { "metodoPago": "tarjeta" }
      """
    Then la respuesta tiene status 404

  # TODO: confirmar con el docente — no se pudo leer en el documento qué código de
  # error espera el negocio en este caso. El sandbox devuelve 404 NOT_FOUND (no un
  # 409 Conflict, que sería lo esperable) — confirmar si el requisito real coincide
  # con este comportamiento antes de tomarlo como criterio de aceptación definitivo.
