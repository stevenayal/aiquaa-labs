# Matriz de trazabilidad — ejemplo

Documento fuente → requisitos extraídos (paso 3 del flujo) → escenario que los verifica.
Generada a mano en este ejemplo; en un caso real, los comentarios `# criterio: ...` en el
`.feature` alimentan automáticamente la tabla equivalente dentro de `INFORME_BDD_*.pdf`
(generado por `bdd-skill` → `reporter/bdd_report.py`).

| # | Requisito extraído del documento | Confianza de extracción | Escenario | Estado |
|---|-----------------------------------|---------------------------|-----------|--------|
| 1 | El usuario puede pagar una factura con tarjeta o efectivo | alta (texto legible) | `Pago de factura con método válido` | cubierto |
| 2 | Existe un tercer método de pago | baja — palabra ilegible en el escaneo | — | **TODO — pendiente de confirmación** |
| 3 | Si la factura ya fue pagada, el sistema no debe reprocesar el pago | alta | `Pago de una factura ya pagada` | cubierto |
| 4 | Código de error esperado al pagar una factura ya pagada | media — el documento no especifica el código exacto | `Pago de una factura ya pagada` (asume 404, confirmar) | **TODO — verificar contra requisito real** |

## Cómo leer esta tabla

- **Confianza alta** → texto extraído con claridad, escenario generado sin marcas TODO.
- **Confianza baja/media** → el escenario existe pero lleva un comentario `TODO` explícito en
  el `.feature` — no se completó el vacío con un valor inferido.
- Una fila sin escenario (`—`) significa que el requisito quedó fuera hasta que se confirme
  qué dice realmente el documento — nunca se inventa el escenario para "completar" la matriz.

## Uso en clase

1. Alumno sube el documento de requisitos (PDF/imagen) del grupo asignado.
2. `ocr-bdd-skill` extrae y arma esta tabla — el alumno la revisa con el docente.
3. Filas con confianza alta pasan directo a `bdd-skill` para generar steps.
4. Filas `TODO` se resuelven en clase antes de escribir el escenario definitivo.
