# Extracción — cascada de métodos

Orden de preferencia: **visión del agente → `pdftotext -layout` → `tesseract`**. Nunca saltar
directo a OCR si la visión del agente puede leer la fuente — es más preciso con tablas,
capturas de UI y manuscrito, y no depende de instalar nada.

## 1. Visión del agente (primario)

Si el agente tiene capacidad multimodal (lee imágenes/PDFs directamente), usarla siempre que
sea posible. Ventajas: entiende tablas, layouts de dos columnas, capturas de pantalla con
contexto visual (botones, estados de UI), y manuscrito razonablemente legible.

Límite: PDFs muy largos pueden exceder lo que se puede leer de una — en ese caso, pedir el
rango de páginas relevante en vez de procesar todo el documento a ciegas.

## 2. `pdftotext -layout` — respaldo para PDF nativo

Solo sirve si el PDF tiene texto seleccionable (no es una imagen escaneada dentro de un PDF).

```bash
pdftotext -layout documento.pdf -
```

`-layout` preserva el espaciado de columnas/tablas — sin esta flag, el texto sale desordenado
en documentos con múltiples columnas. Para un rango de páginas:

```bash
pdftotext -layout -f 5 -l 12 documento.pdf -
```

Verificar disponibilidad: `pdftotext -v`. Si no está instalado, es parte del paquete
`poppler-utils` (Linux/macOS) — en Windows normalmente ya viene con Git Bash/MSYS2.

## 3. `tesseract` — último respaldo, solo imágenes o PDF escaneado

```bash
tesseract imagen.png salida -l spa
cat salida.txt
```

Para PDF escaneado, primero convertir a imagen (`pdftoppm`) y correr tesseract por página:

```bash
pdftoppm -png documento.pdf pagina
tesseract pagina-1.png salida-1 -l spa
```

Límites conocidos — revisar el resultado con más escepticismo que con los otros dos métodos:

- Tablas se leen como texto plano, sin estructura de columnas — reconstruir manualmente.
- Manuscrito: calidad muy variable, a veces ilegible.
- Baja resolución o fotos con ángulo: tasa de error alta — si el resultado tiene muchas
  palabras sin sentido, pedir mejor calidad de imagen en vez de forzar la lectura.
- `-l spa` es obligatorio para español — sin especificar idioma, tesseract asume inglés y el
  resultado es prácticamente inservible en texto en español con tildes/ñ.

## Cuándo ninguno alcanza

Si los tres métodos fallan o dan resultado de baja confianza: decirlo explícitamente al
usuario y pedir el documento en otro formato (texto plano, mejor foto, PDF nativo en vez de
escaneado) — no entregar una extracción de mala calidad como si fuera confiable.
