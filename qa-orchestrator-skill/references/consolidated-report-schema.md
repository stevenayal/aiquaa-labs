# Formato del informe consolidado — `INFORME_CONSOLIDADO_<NOMBRE>.md`

Generado por `/qa:consolidar`, después de que todas las skills seleccionadas terminaron su
ejecución. Markdown plano — no PDF. Cada skill hija ya produce su propio reporte nativo
(PDF vía ReportLab, JUnit XML, NUnit3 XML, cucumber JSON, JTL); este archivo los **agrega**,
no los reemplaza ni reprocesa sus datos crudos.

```markdown
# Informe consolidado — <PR #N | historia>

Origen: <PR #N (link) | historia>
Fecha: <ISO 8601>
Bitácora: [`BITACORA_<...>.md`](./BITACORA_<...>.md)
Skills invocadas: <lista>

## Resultado por skill

### <skill-1>

- Veredicto: <escala nativa de la skill si existe, ej. VERDE / VERDE CON GAPS / FALLOS
  MENORES / REGRESIÓN CRÍTICA (flaui); si la skill no tiene escala propia, usar
  PASS / FALLOS MENORES / FALLOS CRÍTICOS>
- Resumen: <N escenarios/tests, M pasaron, K fallaron>
- Reporte nativo: <ruta al PDF/XML/JSON/JTL>
- Prerrequisito: <cumplido | omitida — motivo>

### <skill-2>

...

## Veredicto global

**<el peor veredicto individual entre todas las skills invocadas — no se promedia>**

Motivo: <cuál skill determinó el veredicto y por qué>

## Próximos pasos

1. Revisar <lo que haya quedado en FALLOS/gaps, si aplica>.
2. Entregar vía `course-pr-skill` — correr `/qa:entregar` (pide confirmación explícita antes
   de abrir el PR).
```

## Regla del veredicto global

Se usa un **gate pattern**: el veredicto global es el peor entre los individuales, nunca un
promedio ni una mayoría. Un PR que toca API y UI donde la API pasa VERDE pero la UI tiene una
REGRESIÓN CRÍTICA es, en conjunto, una REGRESIÓN CRÍTICA — no "mayormente verde". Esto evita
que una skill con buen resultado enmascare una falla real en otra capa del mismo cambio.

## Escala de fallback (skills sin veredicto propio)

Para skills que no definen su propia escala en su reporte nativo (hurl, postman-newman):

| Condición | Veredicto |
|---|---|
| `failed = 0` | PASS |
| `pass_rate >= 85%` | FALLOS MENORES |
| `pass_rate < 85%` | FALLOS CRÍTICOS |
