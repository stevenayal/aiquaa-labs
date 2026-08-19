# ocr-bdd-skill — CLAUDE.md

## Project

Document-to-BDD extraction skill for the aiquaa automation course. Owned by aiquaa-labs.
Hands off confirmed requirements to `bdd-skill` — does not write step definitions itself.

## Structure

```
skills/ocr-bdd/  ← main skill (extraction cascade + confirmation flow)
references/      ← extraccion.md (method cascade and limits)
examples/        ← F_DESDE_DOCUMENTO.feature, TRAZA_EJEMPLO.md
docs/            ← usage guide in Spanish
```

## Key rule — the whole point of this skill

Never infer a value for an illegible/ambiguous field. Always emit
`# TODO: confirmar con el docente` and stop short of guessing, even when a plausible value
is obvious from context (e.g. the sandbox contract). Confidence-graded extraction
(references/extraccion.md) exists specifically to make this distinction visible.

## Extraction cascade

1. Agent vision (primary) — multimodal read of image/PDF directly
2. `pdftotext -layout` (fallback, native-text PDF only)
3. `tesseract -l spa` (last resort, images / scanned PDF)

Never skip straight to OCR when agent vision can read the source.
