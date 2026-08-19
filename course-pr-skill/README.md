# course-pr-skill

Entrega semanal del curso de automatización vía Pull Request, contra el repositorio propio
del alumno (GitHub o Azure DevOps — autodetectado por el remote). Corre un pre-flight
(escaneo de secretos, tests, artefactos esperados) antes de commitear, y nunca abre el PR sin
confirmación explícita.

## Instalación

```bash
npx skills add aiquaa-labs/course-pr-skill
```

## Por qué existe

Es habitual que una entrega apurada commitee un `.env` o una API key por error, o abra un PR
sin haber corrido los tests. El pre-flight de esta skill corre esas verificaciones **antes**
de tocar git, no después.

## Comandos

| Comando | Acción |
|---------|--------|
| `/curso:entregar` | Pre-flight → rama → commit → PR (con confirmación) |
| `/curso:revisar` | Checklist de entrega sobre un PR ajeno |
| `/curso:pr` | Solo arma el PR |

## Contenido

- `skills/course-pr/SKILL.md` — el flujo completo
- `references/checklist-entrega.md` — artefactos esperados por semana (3 a 8)
- `examples/PULL_REQUEST_TEMPLATE.md` — plantilla de PR

→ [Guía de uso](./docs/uso.md)

## Licencia

MIT
