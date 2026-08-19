# Formato de la bitácora — `BITACORA_<PR-o-historia>.md`

Cada corrida de `/qa:analizar` escribe o actualiza un archivo con este nombre y estas
secciones, en este orden. Es el artefacto de auditoría: cualquier persona debe poder leerlo y
entender por qué se eligió (o no) cada skill, sin tener que reconstruir el razonamiento.

```markdown
# Bitácora — <PR #N | nombre de la historia>

## 1. Encabezado

- Fecha: <ISO 8601>
- Origen: PR #<N> (<GitHub|Azure DevOps>) | Historia: <nombre/ref>
- Hash de contenido: <sha256 corto del diff+historia concatenados>
- Agente/autor: <quién corrió /qa:analizar>

## 2. Entradas analizadas

- Archivos del diff: <lista ruta + extensión>
- Historia: <resumen de 2-3 líneas, o referencia al documento OCR de origen si vino de
  ocr-bdd-skill>

## 3. Señales detectadas

| Señal | Skill candidata | Peso |
|---|---|---|
| <ruta o keyword literal> | <skill> | <N> |

## 4. Puntajes por skill

| Skill | Puntaje total | Nivel de confianza |
|---|---|---|
| <skill> | <N> | Alta \| Media \| Ambigua \| Sin señales |

## 5. Decisión

- Seleccionadas: <lista, con motivo breve>
- Descartadas: <lista, con motivo — ej. "puntaje 0, sin señales de rendimiento en diff ni
  historia">
- Ambiguas: <qué se le preguntó al usuario y qué respondió, o "N/A" si no hubo>

## 6. Prerrequisitos

| Skill seleccionada | Check | Resultado |
|---|---|---|
| <skill> | <ver references/prerequisites-check.md> | Cumple \| No cumple — omitida, <motivo> |

## 7. Ejecución

| Skill | Comandos corridos | Archivos generados/actualizados | Resultado | Reporte nativo |
|---|---|---|---|---|
| <skill> | <lista> | <lista> | <pass/fail/parcial> | <ruta al PDF/XML/JSON/JTL> |

## 8. Confirmaciones humanas

| Timestamp | Qué se confirmó |
|---|---|
| <ISO 8601> | <ruteo ambiguo resuelto \| entrega confirmada \| ...> |

## 9. Estado final

<listo para consolidar | pendiente de confirmación | bloqueado (secretos) | bloqueado
(prerrequisito crítico faltante)>
```

## Reglas

- **Idempotencia**: si `/qa:analizar` corre de nuevo y el hash de la sección 1 no cambió,
  no se re-pregunta ni se re-genera nada — se agrega una línea "hash sin cambios,
  reutilizando decisión anterior" y se referencia la bitácora existente.
- La sección 5 (Decisión) siempre debe tener una entrada para **cada skill que tuvo puntaje >
  0**, incluidas las descartadas — nunca se omite una candidata en silencio.
- La sección 6 (Prerrequisitos) solo lista skills que llegaron a "Seleccionadas" en la
  sección 5.
- La sección 7 (Ejecución) se completa progresivamente por `/qa:generar` y `/qa:ejecutar` —
  no hace falta que `/qa:analizar` la deje completa, pero sí debe crear la fila vacía por cada
  skill seleccionada.
