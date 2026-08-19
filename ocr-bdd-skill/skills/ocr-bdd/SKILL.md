---
name: ocr-bdd
description: >
  Convierte documentos de requisitos (PDF, imagen, captura de pantalla,
  historia de usuario escaneada) en escenarios Gherkin BDD, con matriz de
  trazabilidad requisito → escenario. Usa visión del agente como método
  primario de extracción y cae a pdftotext/tesseract cuando no hay visión
  disponible. Nunca completa un campo ilegible por su cuenta — lo marca como
  TODO para que el docente/alumno lo confirme. Complementa la skill bdd.
  Usar cuando el usuario mencione "OCR", "convertir documento a BDD", "extraer
  requisitos de un PDF/imagen", "historia de usuario escaneada", "generar
  features desde un documento", o suba un archivo PDF/imagen con requisitos.
---

Document read. Claude extract requirements. No invent. Terse output.

---

## ¿Qué es esta skill?

Convierte una fuente no estructurada (PDF, imagen, captura de pantalla, foto de un pizarrón)
en Gherkin estructurado, con trazabilidad explícita entre lo que el documento pide y lo que el
`.feature` verifica. No es la skill que escribe steps — eso lo hace `bdd-skill`, que se invoca
después con la lista de requisitos ya extraída y confirmada.

**Regla número uno, sin excepciones: el OCR no inventa.** Todo campo, valor o regla que no se
pueda leer con confianza queda como `# TODO: confirmar con el docente` dentro del `.feature`
— nunca se completa con un valor razonable ni se omite en silencio.

---

## Flujo — 5 pasos, en orden

### 1. Clasificar la fuente

| Tipo | Cómo se ve |
|------|------------|
| PDF nativo (texto seleccionable) | copiar/pegar el texto funciona en un lector normal |
| PDF escaneado | es una imagen dentro de un PDF — no se puede seleccionar texto |
| Imagen / foto | `.png`, `.jpg`, foto de documento o pizarrón |
| Captura de pantalla | UI, ticket de Jira, email, chat |

No asumir el tipo por la extensión — un `.pdf` puede ser cualquiera de los dos primeros.
Verificar antes de elegir el método de extracción.

### 2. Extraer — cascada, en este orden

Ver `references/extraccion.md` para el detalle de cada método y sus límites.

1. **Visión del agente (primario)** — leer la imagen o el PDF directamente si el agente tiene
   capacidad multimodal. Sin dependencias, funciona con capturas y tablas, es el método
   preferido siempre que esté disponible.
2. **`pdftotext -layout`** (respaldo, solo PDF nativo) — cuando no hay visión disponible o el
   PDF es muy largo para procesar entero. Preserva el layout de columnas/tablas razonablemente.
3. **`tesseract`** (último respaldo, solo imágenes o PDF escaneado sin visión disponible) —
   `tesseract imagen.png salida -l spa`. Calidad variable con tablas, manuscrito o baja
   resolución — revisar el resultado con más cuidado que con los otros dos métodos.

Si ninguno de los tres da un resultado legible, **decirlo** y pedir el documento en otro
formato — no forzar una extracción de baja confianza.

### 3. Normalizar a requisitos verificables

Convertir el texto extraído en una lista numerada. Cada ítem debe ser una afirmación
verificable (una condición que se puede convertir en un `Then`), no un párrafo descriptivo.

```
1. El sistema debe rechazar el login si el usuario está inactivo.
2. El pago de una factura ya pagada debe devolver un error, no reprocesar el pago.
3. TODO: confirmar con el docente — el documento menciona "límite de reintentos" sin especificar el número.
```

Cada ítem ilegible, ambiguo o incompleto se marca `TODO` explícitamente — no se resuelve por
inferencia, aunque parezca obvio.

### 4. Confirmar con el usuario

Mostrar la lista numerada completa (incluidos los `TODO`) y esperar confirmación o
correcciones antes de generar nada. Nunca saltar este paso, incluso si la extracción se ve
completa — el usuario conoce el contexto que el documento no explicita.

### 5. Generar `.feature` + matriz de trazabilidad

Recién con la lista confirmada, invocar el catálogo de steps de `bdd-skill` (o generar el
`.feature` directamente si `bdd-skill` no está instalada) con tags `@grupo-N` según corresponda,
y la matriz requisito → escenario. Ver `examples/F_DESDE_DOCUMENTO.feature` y
`examples/TRAZA_EJEMPLO.md`.

Cada `Scenario` lleva un comentario `# criterio: <texto del requisito>` inmediatamente arriba
— es lo que `bdd_report.py` de `bdd-skill` usa para construir la matriz de trazabilidad en el
PDF automáticamente.

---

## Context Intake

1. **¿Qué documento?** — pedir el archivo o la ruta si no se compartió ya.
2. **¿Qué grupo del curso corresponde?** — para resolver el tag `@grupo-N` y, si aplica,
   cruzar contra `sandbox-skill` → `references/grupos.md`.
3. Ejecutar los pasos 1-4 del flujo.
4. Confirmar la lista de requisitos (paso 4) — **esperar respuesta explícita**, no asumir OK.
5. Generar.

---

## Ejemplo — extracción con TODO explícito

Documento fuente (fragmento, mal escaneado):

```
El usuario debe poder pagar una factura con [ilegible] o efectivo.
Si la factura ya fue pagada, el sistema [ilegible].
```

Salida correcta:

```
1. El usuario puede pagar una factura con tarjeta o efectivo.
   # TODO: confirmar con el docente — el documento menciona un tercer método de pago
   # ilegible en el escaneo (¿"cuenta"? ver contrato del sandbox, grupo 3).
2. TODO: confirmar con el docente — no se pudo leer qué pasa si la factura ya fue pagada.
   El sandbox devuelve 404 en ese caso (POST /api/v1/facturas/{id}/pagar) — confirmar si
   coincide con el requisito real antes de escribir el escenario.
```

Salida incorrecta (no hacer esto):

```
1. El usuario puede pagar una factura con tarjeta, efectivo o cuenta.
2. Si la factura ya fue pagada, el sistema devuelve un error.
```
— asume el método de pago faltante y el comportamiento de error sin haberlos leído.

---

## Boundaries

Lee documentos, extrae texto, normaliza a requisitos, genera `.feature` con trazabilidad.
NO instala tesseract ni pdftotext — asume que están disponibles o usa visión del agente.
NO completa campos ilegibles con valores inferidos, aunque coincidan con el sandbox — siempre
`TODO` explícito.
NO genera steps de implementación — eso lo hace `bdd-skill` con la lista ya confirmada.
"stop ocr-bdd" o "normal mode": volver a estilo verbose.
