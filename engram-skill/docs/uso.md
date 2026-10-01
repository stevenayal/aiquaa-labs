# Guía de uso — engram-skill

Ejemplos de antes/después en el contexto del curso. Todos asumen las herramientas `mem_*`
disponibles; si no lo están, la skill lo dice en una línea y sigue sin memoria.

---

## 1. Arrancar la sesión de la semana 4

**Sin memoria:** "¿qué prefijo usamos para los specs de Playwright?" → el agente vuelve a leer
el README raíz, tres skills y dos PRs anteriores.

**Con esta skill:**
```
mem_current_project              → { project: "entregas-qa", project_source: "git_remote" }
mem_search "prefijo spec playwright"
  → #42 "Fijada convención T_ para specs Playwright" (pattern)
mem_get_observation 42           → What/Why/Where completos
```

---

## 2. Guardar una decisión apenas el usuario la confirma

> Usuario: "dale, usemos Hurl para el smoke del login en vez de Postman"

**Sin criterio:** la decisión queda solo en el chat; la próxima sesión no la conoce.

**Con esta skill**, sin que lo pidan:
```
mem_save
  title:     Elegido Hurl sobre Postman para smoke de login
  type:      decision
  topic_key: decision/api-smoke-tool
  content:
    **What**: El smoke de /auth/login se escribe en Hurl (H_LOGIN.hurl)
    **Why**: Se revisa en el PR como texto plano; Postman queda para exploración
    **Where**: tests/api/H_LOGIN.hurl
    **Learned**: El rate limit del sandbox obliga a [Options] retry en Hurl
```

Si en la semana 6 cambia la decisión, se guarda con el **mismo** `topic_key` → actualiza la
memoria en vez de dejar dos contradictorias.

---

## 3. Bug con causa raíz

**Sin criterio:** `mem_save "arreglé el test"` — imposible de encontrar y sin el porqué.

**Con esta skill:**
```
title:   Fixed flaky T_CHECKOUT por toast que tapa el botón pagar
type:    bugfix
content:
  **What**: Se espera a que el toast desaparezca antes del click en btn-pagar
  **Why**: El toast de "carrito actualizado" interceptaba el click en CI (viewport chico)
  **Where**: tests/e2e/T_CHECKOUT.spec.ts, pages/CheckoutPage.ts
  **Learned**: Solo falla con viewport < 1280px — reproducir con --project=mobile
```

---

## 4. Conflicto entre memorias

```
mem_save "Usar Postgres para usuarios" ...  (semana 2)
mem_save "Migrar usuarios a MongoDB" ...    (semana 5)
  → candidates: [#17], judgment_required: true, judgment_id: "j_88"
mem_get_observation 17
mem_judge judgment_id="j_88" relation="supersedes" reason="Migración decidida en semana 5"
```

Las búsquedas futuras muestran `superseded_by: #<nuevo>` sobre la vieja.

---

## 5. Cerrar la sesión

> Usuario: "listo, eso es todo por hoy"

**Antes de responder**, `mem_session_summary`:
```
## Goal
Automatizar el flujo de checkout (semana 4)

## Instructions
El alumno prefiere POM con un archivo por página

## Discoveries
- El toast de carrito tapa btn-pagar en viewports chicos

## Accomplished
- T_CHECKOUT.spec.ts verde en CI
- CheckoutPage.ts con espera explícita del toast

## Next Steps
- Agregar caso de tarjeta rechazada
- Abrir PR semanal con course-pr-skill

## Relevant Files
- tests/e2e/T_CHECKOUT.spec.ts — spec nuevo
- pages/CheckoutPage.ts — page object
```

---

## 6. Después de una compactación

1. `mem_session_summary` con el resumen compactado.
2. `mem_context`.
3. Seguir.

---

## 7. Proyecto ambiguo

El agente arrancó en `~/curso/` que tiene `entregas-qa/` y `sandbox-api/`:

```
mem_save ... → error ambiguous_project, available_projects: ["entregas-qa", "sandbox-api"]
```

**Mal:** reintentar con `project: "entregas"` (inventado → falla).
**Bien:** preguntar al usuario, y con su elección:
```
mem_save ... project="entregas-qa" project_choice_reason="user_selected_after_ambiguous_project"
```
Y sugerir `.engram/config.json` con `{"project_name": "entregas-qa"}` para que no vuelva a pasar.

---

## 8. Lo que nunca se guarda

> Usuario: "guardá el token del sandbox para no pedírtelo de nuevo"

**Con esta skill:** no se guarda. Se explica que la memoria puede sincronizarse por git/cloud,
y se guarda en su lugar *dónde* vive el token:
```
title:   El token del sandbox se lee de SANDBOX_TOKEN en .env (no versionado)
type:    config
```
