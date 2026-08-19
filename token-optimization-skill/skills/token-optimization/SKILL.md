---
name: token-optimization
description: >
  Hábitos y elección de herramienta para reducir consumo de tokens en sesiones largas del
  curso — cuándo preferir codegraph (búsqueda estructural) a grep, cuándo consultar engram
  (memoria persistente) antes de re-explorar, y cuándo activar caveman (salida comprimida).
  Degrada con gracia si esos MCP no están configurados — nunca bloquea ni los instala.
  Usar cuando el usuario mencione "optimizar tokens", "ahorrar tokens", "reducir consumo",
  "modo eficiente", "sesión larga", o cuando el contexto se acerca a su límite.
---

Elegir herramienta barata antes que cara. Memoria antes que re-explorar. Comprimir salida cuando pese.

---

## ¿Qué es esta skill?

Una sesión del curso corre varias skills en secuencia — genera colecciones Postman, planes
JMeter, features Gherkin, informes PDF — y cada una lee y escribe archivos grandes. Los
tokens se acumulan rápido. Esta skill no genera archivos: es una capa de criterio sobre **qué
herramienta usar primero** y **cuándo comprimir la salida**, para que la sesión llegue más
lejos antes de necesitar `/compact` o una sesión nueva.

No reemplaza a `caveman` (ese es el mecanismo de compresión) ni depende de que codegraph o
engram estén instalados — funciona igual sin ellos, solo que con más trabajo manual.

---

## Principios

| Mecanismo | Cuándo preferirlo | Si no está disponible |
|---|---|---|
| **codegraph** (MCP) | Buscar un símbolo, ver quién llama a qué, medir el impacto de un cambio, o entender un módulo — antes de `grep`/`Read` a ciegas por el repo | Usar `Grep`/`Glob`/`Read` normalmente — no bloquear el trabajo ni pedirle al alumno que lo instale |
| **engram** (MCP) | Antes de re-explorar algo que la sesión (u otra anterior) ya investigó — `mem_search`/`mem_context`. Guardar decisiones con `mem_save` para no repetir la exploración la próxima vez | Seguir sin memoria persistente — ninguna otra skill del stack la requiere |
| **caveman** | Sesiones largas, salida repetitiva (varias corridas de `/postman:fix`, `/jmeter:fix`, etc.), o cuando se pide explícitamente menos tokens | El resto del stack funciona igual, solo con salida más verbosa. Activar con `/caveman` — ver `postman-newman-skill/skills/caveman/SKILL.md` |

Regla dura: **nunca instalar ni configurar servidores MCP por cuenta propia.** Si codegraph o
engram no están disponibles, decirlo en una línea y seguir con las herramientas nativas — no
es un bloqueo, es una alternativa más lenta.

---

## Recomendaciones propias

Hábitos que no dependen de tooling externo, útiles con o sin MCP:

- Leer con `offset`/`limit` cuando ya se sabe la línea (de un resultado de `Grep`) en vez de
  el archivo completo.
- No releer un archivo recién editado — `Edit`/`Write` ya confirman el resultado; si fallaran,
  el error lo dice.
- Preferir `Edit` sobre reescribir el archivo entero con `Write` para cambios chicos.
- Acotar `Grep` con `head_limit` o `output_mode: files_with_matches` antes de pedir el
  contenido completo de cada coincidencia.
- Delegar exploración amplia (más de 3 búsquedas independientes) a un subagente en vez de
  acumularla en el contexto principal.
- Referenciar `archivo:línea` en la respuesta en vez de pegar el archivo completo.
- Fijar convenciones que se repiten (naming, endpoints, credenciales de entorno) en el
  `CLAUDE.md` del proyecto en vez de reexplicarlas cada vez.
- Cerrar sesiones largas con un resumen corto en vez de dejar que el historial crezca sin
  necesidad — más fácil de retomar y más barato de releer.

---

## Boundaries

Nunca sacrificar corrección o completitud por ahorrar tokens: código, commits, PRs, y
contenido técnico (asserts, valores esperados, credenciales, nombres de campos) siempre van
completos y exactos — la compresión es de prosa, no de sustancia técnica (mismo límite que
`caveman`).

No instala ni configura servidores MCP.
No compite con `caveman` — esta skill decide *qué herramienta usar primero*; `caveman` decide
*cómo se ve la salida*. Ambas se pueden usar juntas.
"stop token-optimization" o "normal mode": volver a explorar sin este criterio de prioridad
(no afecta a `caveman`, que se controla con su propio comando).
