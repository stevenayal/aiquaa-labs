---
name: course-pr
description: >
  Entrega semanal del curso de automatización vía Pull Request, contra el
  repositorio propio del alumno. Detecta la plataforma (GitHub vía gh, Azure
  DevOps vía az repos) por el remote, corre un pre-flight (escaneo de
  secretos, tests, artefactos esperados) antes de commitear, crea rama por
  grupo/semana, y abre el PR con plantilla — pidiendo confirmación explícita
  antes de la acción externa. Incluye modo revisión entre pares.
  Usar cuando el usuario mencione "entregar", "hacer PR", "subir mi tarea",
  "entrega de la semana", "pull request del curso", o pida abrir un PR con lo
  trabajado en el curso.
---

PR flow. Claude check first, ask before push. Terse output. No fluff.

---

## ¿Qué es esta skill?

Automatiza la entrega semanal del curso cuando el alumno ya tiene su propio repositorio
(GitHub o Azure DevOps). No reemplaza el criterio del alumno — corre las verificaciones que
evitan el error típico de entrega (secretos commiteados, tests rotos, artefactos faltantes) y
arma rama + commit + PR con plantilla, pero **nunca abre el PR sin confirmación explícita**.

---

## Comandos

| Comando | Acción |
|---------|--------|
| `/curso:entregar` | Flujo completo: pre-flight → rama → commit → PR (con confirmación) |
| `/curso:revisar` | Corre el checklist de `references/checklist-entrega.md` sobre un PR ajeno |
| `/curso:pr` | Solo arma el PR (asume que rama y commit ya existen) |

---

## Flujo — `/curso:entregar`

### Paso 0 — Detectar plataforma

```bash
git remote get-url origin
```

| Patrón en la URL | Plataforma | CLI |
|-------------------|------------|-----|
| `github.com` | GitHub | `gh` |
| `dev.azure.com` o `visualstudio.com` | Azure DevOps | `az repos` |

Si no hay remote configurado, o el CLI correspondiente no está instalado/autenticado —
**decirlo y parar**. No asumir, no intentar configurar un remote nuevo por cuenta propia.

```bash
gh auth status        # GitHub
az account show        # Azure DevOps
```

### Paso 1 — Pre-flight (siempre, antes de tocar git)

Esto es lo que evita el desastre típico de una entrega apurada. En orden:

1. **Escaneo de secretos en el diff** — buscar antes de cualquier `git add`:
   - Archivos `.env`, `.env.local` (deberían estar en `.gitignore`, verificar que lo estén)
   - Patrones de API key del sandbox: `sbx_[a-z0-9_]+`
   - Connection strings (`postgres://`, `postgresql://` con credenciales embebidas)
   - Tokens genéricos: `Bearer [A-Za-z0-9\-_.]{20,}`, `api[_-]?key\s*[:=]\s*['"]?[A-Za-z0-9]{16,}`

   ```bash
   git diff --cached --name-only | xargs grep -lE "sbx_[a-z0-9_]+|postgres(ql)?://[^/]*:[^/]*@|Bearer [A-Za-z0-9._-]{20,}" 2>/dev/null
   ```

   Si algo aparece: **abortar el flujo**, mostrar el archivo y la línea, y explicar cómo
   sacarlo (`git restore --staged <archivo>`, agregar a `.gitignore`, rotar la key si ya se
   había commiteado antes). No continuar hasta que esté resuelto.

2. **Tests** — correr lo que exista en el repo del alumno, sin asumir un único stack:
   ```bash
   [ -f package.json ] && npm test
   [ -f cucumber.js ] && npx cucumber-js --dry-run
   [ -f pytest.ini ] || [ -f setup.cfg ] && pytest
   ```
   Si fallan, mostrarlo y preguntar si igual se quiere continuar (a veces el alumno entrega
   con un fallo conocido y documentado) — no bloquear silenciosamente, pero tampoco ocultarlo.

3. **Artefactos esperados de la semana** — según lo que se esté enseñando (ver
   `references/checklist-entrega.md`): `.feature`, `.steps.ts`, `.jmx`, capturas/evidencias,
   informe PDF. Listar qué falta, si falta algo — no bloquea, pero se avisa antes del PR.

### Paso 2 — Rama

```
grupo-<n>/semana-<n>-<tema-corto>
```

Ejemplo: `grupo-3/semana-4-pruebas-bdd`. **Nunca commitear directo en `main`/`master`** — si el
alumno está en esa rama, crear y cambiar a la rama de entrega antes de seguir.

### Paso 3 — Commit

Conventional Commits, en español, mensaje corto + cuerpo si hace falta explicar el porqué:

```
git commit -m "feat(grupo-3): agrega BDD para pago de facturas — semana 4"
```

### Paso 4 — PR

Usar `examples/PULL_REQUEST_TEMPLATE.md`. Completar con lo que se sabe del contexto de la
conversación — grupo, semana, qué se automatizó, cómo correrlo. **Pedir confirmación explícita
antes de crear el PR** — es una acción hacia afuera, no se abre por default.

```bash
# GitHub
gh pr create --title "Grupo 3 — Semana 4: BDD Pagos de Servicios" \
  --body-file PULL_REQUEST_TEMPLATE.md --base main

# Azure DevOps
az repos pr create --title "Grupo 3 — Semana 4: BDD Pagos de Servicios" \
  --description "$(cat PULL_REQUEST_TEMPLATE.md)" --target-branch main
```

Después de crear el PR, devolver el link al usuario — no asumir que ya lo vio.

---

## Flujo — `/curso:revisar`

Para revisión entre pares: dado un número de PR (o su URL), correr el checklist de
`references/checklist-entrega.md` sobre los archivos que cambia, sin tocar el repo del autor.

```bash
gh pr diff <numero>              # GitHub
az repos pr show --id <numero>   # Azure DevOps
```

Reportar hallazgos organizados por severidad (secretos > tests rotos > artefactos faltantes >
estilo), igual formato que usan las otras skills del stack para "Fallos comunes".

---

## Context Intake

1. **¿Grupo y semana?** — si no viene de la conversación previa, preguntar.
2. **¿Qué se automatizó esta semana?** — un resumen corto para el cuerpo del PR.
3. Ejecutar pre-flight (paso 1) — sin preguntar, es parte del flujo, pero reportar resultados.
4. Si el pre-flight encuentra secretos: parar y resolver antes de seguir.
5. Confirmar rama + mensaje de commit antes de commitear.
6. **Confirmar explícitamente antes de abrir el PR.**

---

## Fallos comunes y fixes

| Síntoma | Causa | Fix |
|---------|-------|-----|
| `gh: command not found` | CLI no instalado | `winget install GitHub.cli` / `brew install gh` / `apt install gh` |
| `gh auth status` falla | no autenticado | `gh auth login` — el alumno lo hace, esta skill no pide credenciales |
| Escaneo de secretos da falso positivo | un valor de ejemplo coincide con el patrón (ej. `sbx_alumno01_xxxxxxxxxxxx` de la doc) | revisar manualmente — si es un placeholder de ejemplo, no una key real, continuar |
| PR se abre contra la rama equivocada | `--base`/`--target-branch` no especificado | siempre pasar `--base main` explícito, nunca confiar en el default del CLI |
| Commit en `main` por error | el alumno no había cambiado de rama | `git branch grupo-n/semana-n-tema && git reset --soft HEAD~1` en la rama nueva, nunca `--hard` |

---

## Boundaries

Crea ramas, commits y PRs — siempre con confirmación antes del PR (acción hacia afuera).
NO hace `git push --force` bajo ninguna circunstancia.
NO commitea si el escaneo de secretos encuentra algo sin resolver primero.
NO pide credenciales de `gh`/`az` — asume que el alumno ya se autenticó.
NO mergea PRs — solo los crea o los revisa.
"stop course-pr" o "normal mode": volver a estilo verbose.
