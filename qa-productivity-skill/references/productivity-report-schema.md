# Schema — `INFORME_PRODUCTIVIDAD_<EQUIPO-o-PERSONA>_<PERIODO>.md`

Producido por `/productividad:consolidar`. Markdown, auditable, nunca rellena huecos en
silencio. Ejemplo completo resuelto contra fixtures: `examples/INFORME_PRODUCTIVIDAD_EJEMPLO.md`.

## 1. Header

```markdown
# Informe de productividad QA — <equipo o persona> — <período>

- Organización / proyecto: <org> / <project>
- Modo: real (az login) | ejemplo (fixtures de examples/)
- Convención de filtro API/Web: Area Path (ADO_AREA_API/ADO_AREA_WEB) | Tags (ADO_TAG_API/ADO_TAG_WEB)
- Período: <fecha inicio> – <fecha fin>
- Generado: <timestamp ISO>
- Casos excluidos del universo API/Web (BD, escritorio, otros): <N>
```

## 2. Tabla resumen por persona

Las 5 métricas **nunca se promedian entre sí** — columnas separadas:

```markdown
| Persona | % autom. real (API/Web) | % autom. de calidad | Evidencia de ejecución | Estabilidad | Cantidad entregada (mes) |
|---|---|---|---|---|---|
| <nombre> | <N automatizados>/<N total filtrado> = <%> | <N Profunda>/<N total filtrado> = <%> | <N con evidencia>/<N automatizados> | <N estables>/<N con historial> | <N casos> |
```

- **% autom. real** = métrica 1, sobre el universo API/Web filtrado.
- **% autom. de calidad** = solo casos Profunda (métrica 3) + con evidencia de ejecución
  (métrica 2) + estables (métrica 4). Es intencionalmente ≤ % autom. real — la diferencia entre
  ambos números es la señal de inflación.
- **Cantidad entregada** = métrica 5, siempre en su propia columna, nunca combinada con calidad.

## 3. Detalle por persona

Por cada persona, listar los casos que **no** llegaron a "calidad" y por qué — esto es lo que
hace el informe accionable en vez de solo un score:

```markdown
### <nombre>

**Casos superficiales (validan solo transporte, no negocio):**
- <ID Test Case> — <título> — archivo `<H_/T_/F_/C_...>` — PR #<N>

**Casos sin evidencia de ejecución (marcados automatizados, no corren en pipeline):**
- <ID Test Case> — <título> — última corrida encontrada: <ninguna | fecha>

**Casos inestables (flaky, flakiness_rate ≥ umbral):**
- <ID Test Case> — <título> — flakiness_rate: <valor> — últimas 5 corridas: <pass/fail pattern>

**Casos marcados automatizados sin PR vinculado (dato inconsistente):**
- <ID Test Case> — <título>
```

Omitir una subsección si está vacía (no escribir "ninguno" en las 4 — solo mostrar las que
tienen contenido).

## 4. Rollup de equipo

```markdown
## Rollup de equipo

- % automatización real (API/Web), equipo: <N>/<N> = <%>
- % automatización de calidad, equipo: <N>/<N> = <%>
- Brecha real vs. calidad: <puntos porcentuales> — esto es lo que estaba oculto por medir solo cantidad
- Casos entregados en el período: <N>
- Personas con automatización 100% de calidad: <lista o "ninguna en este período">
- Personas con brecha real-vs-calidad > 30 puntos: <lista o "ninguna">
```

## 5. Advertencias / datos incompletos

Obligatoria si aplica — nunca se omite un dato faltante en silencio:

```markdown
## Advertencias / datos incompletos

- <descripción del hueco> — <por qué no se pudo completar> — <qué se necesitaría para cerrarlo>
```

Ejemplos típicos: pipeline sin `PublishTestResults@2` configurado (métrica 2 y 4 no calculables
para ese pipeline), Test Case sin capa API/Web asignable, identidad de PR no vinculable a
`System.AssignedTo`.

## 6. Metodología

```markdown
## Metodología

Convención de filtro: `references/api-web-filter-convention.md`
Heurística de profundidad: `references/validation-depth-heuristics.md`
Comandos y fuentes por métrica: `references/metrics-spec.md`
```

## Prefijo de archivo

`INFORME_PRODUCTIVIDAD_<EQUIPO-o-PERSONA>_<PERIODO>.md` — agregado a la tabla de convención de
nombres del `README.md` raíz del monorepo (columna Skill: `qa-productivity`).
