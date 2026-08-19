# Guía de uso — ocr-bdd-skill

## Instalación

```bash
npx skills add aiquaa-labs/ocr-bdd-skill
```

Para agentes específicos:

```bash
npx skills add aiquaa-labs/ocr-bdd-skill -a cursor
npx skills add aiquaa-labs/ocr-bdd-skill -a windsurf
npx skills add aiquaa-labs/ocr-bdd-skill -a cline
```

## Herramientas opcionales de respaldo

Solo necesarias si el agente no tiene visión (método primario) y la fuente no es texto plano:

```bash
# pdftotext — parte de poppler-utils
apt-get install -y poppler-utils     # Linux
brew install poppler                  # macOS
# Windows: suele venir con Git Bash / MSYS2

# tesseract
apt-get install -y tesseract-ocr tesseract-ocr-spa   # Linux
brew install tesseract tesseract-lang                 # macOS
winget install tesseract                                # Windows
```

## Flujo

1. Subir el documento (PDF, imagen, captura).
2. La skill clasifica la fuente y extrae con la cascada visión → pdftotext → tesseract
   (ver `references/extraccion.md`).
3. Normaliza a una lista numerada de requisitos verificables — lo ilegible queda como `TODO`.
4. **Confirmar la lista con el docente/alumno antes de generar nada.**
5. Genera `.feature` con `@grupo-N` y matriz de trazabilidad, listo para pasar a `bdd-skill`.

## Cuándo se activa

Al mencionar OCR, conversión de documento a BDD, o al adjuntar un PDF/imagen de requisitos.

## Salidas

`F_GRUPO_NN_MODULO.feature` (mismo patrón que `bdd-skill`) + matriz de trazabilidad en
comentarios `# criterio: ...` sobre cada `Scenario`.
