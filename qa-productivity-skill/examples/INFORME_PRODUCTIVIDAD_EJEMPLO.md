# Informe de productividad QA — Equipo API/Web — julio 2026

- Organización / proyecto: `continental` / `Continental`
- Modo: **ejemplo** (fixtures de `examples/`, sin `az login`)
- Convención de filtro API/Web: **Area Path** (`ADO_AREA_API=Continental\QA\API`,
  `ADO_AREA_WEB=Continental\QA\Web`)
- Período: 2026-07-01 – 2026-07-31
- Generado: 2026-08-25T00:00:00Z
- Casos excluidos del universo API/Web (BD, escritorio, otros): 2
  (TC-4107 `Continental\QA\BaseDatos`, TC-4108 `Continental\QA\Escritorio`)

Este informe reproduce, con datos simulados, el resultado esperado de correr
`/productividad:completo` en modo ejemplo contra los fixtures de esta carpeta. Sirve para
validar la skill sin credenciales reales y como referencia del formato de salida.

## Tabla resumen por persona

| Persona | % autom. real (API/Web) | % autom. de calidad | Evidencia de ejecución | Estabilidad | Cantidad entregada (mes) |
|---|---|---|---|---|---|
| Ana Torres | 2/3 = 66.7% | 1/3 = 33.3% | 1/2 automatizados con evidencia | 1/1 con historial, estable | 3 casos |
| Carlos Ruiz | 2/3 = 66.7% | 1/3 = 33.3% | 2/2 automatizados válidos con evidencia | 2/2 estables | 3 casos |
| Marina López | 2/2 = 100% | 1/2 = 50% | 2/2 con evidencia | 1/2 estable (1 inestable) | 2 casos |

> `% autom. real` excluye casos marcados `Automated` sin PR vinculado (ver Carlos Ruiz,
> TC-4102). `% autom. de calidad` solo cuenta casos Profunda + con evidencia + estables — es
> intencionalmente menor al % real en los tres casos. Esa brecha es la señal que este informe
> existe para exponer.

## Detalle por persona

### Ana Torres

**Casos sin evidencia de ejecución (marcados automatizados, no corren en pipeline):**
- TC-4110 "Descargar estado de cuenta PDF web" — archivo `T_DescargarEstadoCuenta.spec.ts` — PR
  #8806 — última corrida encontrada: ninguna en la ventana de 30 días

### Carlos Ruiz

**Casos superficiales (validan solo transporte, no negocio):**
- TC-4103 "Actualizar límite de tarjeta API" — archivo `H_ActualizarLimite.hurl` — PR #8802 —
  ver ejemplo completo en `az-git-pr-diff-shallow.md`

**Casos marcados automatizados sin PR vinculado (dato inconsistente):**
- TC-4102 "Consultar saldo API - respuesta 200" — `Microsoft.VSTS.TCM.AutomationStatus =
  Automated`, sin PR asociado en `az-repos-pr-list.json` y sin corridas en
  `az-test-runs-results.json` — no se cuenta como automatización real ni de calidad.

### Marina López

**Casos superficiales (validan solo transporte, no negocio):**
- TC-4106 "Cambio de clave portal web" — archivo `T_CambioClave.spec.ts` — PR #8804

**Casos inestables (flaky, flakiness_rate ≥ umbral):**
- TC-4106 "Cambio de clave portal web" — `T_CambioClave.spec.ts` — flakiness_rate: 1.0 (5/5
  transiciones) — últimas 6 corridas: P, F, P, F, P, F

## Rollup de equipo

- % automatización real (API/Web), equipo: 6/8 = 75%
- % automatización de calidad, equipo: 3/8 = 37.5%
- Brecha real vs. calidad: 37.5 puntos — esto es lo que estaba oculto por medir solo cantidad
- Casos entregados en el período: 8 (filtrados API/Web)
- Personas con automatización 100% de calidad: ninguna en este período
- Personas con brecha real-vs-calidad > 30 puntos: Ana Torres (33.4 pts), Carlos Ruiz (33.4
  pts), Marina López (50 pts)

## Advertencias / datos incompletos

- TC-4102 (Carlos Ruiz) figura `Automated` en Azure DevOps pero no tiene Pull Request asociado
  ni corridas de pipeline — posible dato desactualizado en Test Plans. Se recomienda confirmar
  manualmente antes de la reunión, no se asumió automatización real ni falsa por inferencia.
- TC-4110 (Ana Torres) tiene PR válido y clasifica Profunda por código, pero no aparece en
  ningún resultado de Test Run dentro de la ventana de 30 días — puede indicar que el pipeline
  que la ejecuta no publica resultados vía `PublishTestResults@2`, o que el test está deshabilitado.

## Metodología

Convención de filtro: `references/api-web-filter-convention.md`
Heurística de profundidad: `references/validation-depth-heuristics.md`
Comandos y fuentes por métrica: `references/metrics-spec.md`
