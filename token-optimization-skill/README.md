# token-optimization-skill

Hábitos y elección de herramienta para reducir consumo de tokens en sesiones largas del curso
— cuándo preferir `codegraph` (búsqueda estructural) a `grep`, cuándo consultar `engram`
(memoria persistente) antes de re-explorar, y cuándo activar `caveman` (salida comprimida).
Degrada con gracia si esos MCP no están configurados — nunca los instala ni bloquea el
trabajo por su ausencia.

## Instalación

```bash
npx skills add aiquaa-labs/token-optimization-skill
```

## Por qué existe

Una sesión del curso corre varias skills en secuencia — Postman, JMeter, BDD, informes PDF —
y cada una lee y escribe archivos grandes. Sin un criterio explícito de qué herramienta usar
primero, el agente termina haciendo `grep` manual donde había un MCP de código disponible, o
re-explorando algo que una sesión anterior ya resolvió. Esta skill no genera archivos: fija
ese criterio para que la sesión llegue más lejos antes de necesitar `/compact` o empezar de
cero.

## Comandos / triggers

No define comandos `/` propios — es una skill de criterio que se activa cuando el usuario
menciona "optimizar tokens", "ahorrar tokens", "reducir consumo", "modo eficiente", "sesión
larga", o cuando el contexto se acerca a su límite.

Para comprimir la salida en sí, se sigue usando `/caveman` (skill separada, vive en
`postman-newman-skill`).

## Contenido

- `skills/token-optimization/SKILL.md` — criterio de herramienta (codegraph / engram /
  caveman) y recomendaciones propias que no dependen de MCP.

→ [Guía de uso](./docs/uso.md)

## Licencia

MIT
