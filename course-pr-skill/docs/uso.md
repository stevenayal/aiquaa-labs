# Guía de uso — course-pr-skill

## Instalación

```bash
npx skills add aiquaa-labs/course-pr-skill
```

Para agentes específicos:

```bash
npx skills add aiquaa-labs/course-pr-skill -a cursor
npx skills add aiquaa-labs/course-pr-skill -a windsurf
npx skills add aiquaa-labs/course-pr-skill -a cline
```

## Requisitos

Uno de los dos CLI, ya autenticado por el alumno:

```bash
# GitHub
gh auth login

# Azure DevOps
az login
az devops configure --defaults organization=<org> project=<proyecto>
```

La skill detecta cuál usar leyendo `git remote get-url origin` — no pregunta cuál preferís.

## Flujo

1. `/curso:entregar` — pre-flight (secretos, tests, artefactos) → rama → commit → PR
2. Revisar el resumen del pre-flight — si encontró secretos, resolverlos antes de seguir
3. Confirmar el mensaje de commit y el contenido del PR
4. **Confirmar explícitamente** antes de que la skill abra el PR — no se abre solo

## Comandos

| Comando | Acción |
|---------|--------|
| `/curso:entregar` | Flujo completo de entrega |
| `/curso:revisar` | Checklist sobre un PR ajeno (revisión entre pares) |
| `/curso:pr` | Solo arma el PR (rama y commit ya existen) |

## Salidas

Rama `grupo-<n>/semana-<n>-<tema>`, commit conventional, PR con
`examples/PULL_REQUEST_TEMPLATE.md`.
