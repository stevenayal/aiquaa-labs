# ocr-bdd-skill

Convierte documentos de requisitos (PDF, imagen, captura de pantalla) en escenarios Gherkin
BDD, con matriz de trazabilidad requisito → escenario. Usa visión del agente como método
primario; cae a `pdftotext`/`tesseract` cuando no hay visión disponible. Complementa
[`bdd-skill`](../bdd-skill), que toma la lista de requisitos ya confirmada y genera los steps.

**Regla dura: nunca completa un campo ilegible por inferencia** — todo lo que no se puede leer
con confianza queda como `# TODO: confirmar con el docente` en el `.feature`.

## Instalación

```bash
npx skills add aiquaa-labs/ocr-bdd-skill
```

## Flujo

1. Clasificar la fuente (PDF nativo / escaneado / imagen / captura)
2. Extraer — visión del agente → `pdftotext -layout` → `tesseract`
3. Normalizar a requisitos verificables, marcando lo ilegible
4. Confirmar con el usuario
5. Generar `.feature` + matriz de trazabilidad

## Contenido

- `skills/ocr-bdd/SKILL.md` — el flujo completo y las reglas de extracción
- `references/extraccion.md` — cascada de métodos, límites de cada uno
- `examples/F_DESDE_DOCUMENTO.feature` — ejemplo con `TODO` explícitos
- `examples/TRAZA_EJEMPLO.md` — matriz de trazabilidad de ejemplo

→ [Guía de uso](./docs/uso.md) · [Skill bdd](../bdd-skill) · [Skill sandbox](../sandbox-skill)

## Licencia

MIT
