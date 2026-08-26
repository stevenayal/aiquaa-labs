# Convención de filtro API/Web

No existe un estándar universal de Azure DevOps para marcar un Test Case como "API" o "Web" —
cada organización lo modela distinto. Esta skill **nunca asume** cuál convención usa el proyecto
del usuario: la pregunta en el intake (`/productividad:configurar`) y la deja explícita en el
header de todo informe generado.

## Por qué existe este filtro

El diagnóstico de negocio es claro: hay deuda técnica de automatización en objetos de base de
datos Oracle y en aplicaciones de escritorio, donde hoy no existe una forma madura de
automatizar. Si el % de automatización se calculara sobre *todos* los Test Case del proyecto,
ese universo no-automatizable distorsionaría el número real hacia abajo, dando una imagen falsa
de bajo desempeño incluso en equipos que sí automatizan bien lo que es automatizable hoy (API y
Web). Aislar el filtro a API/Web es lo que hace que el % sea una medida justa.

## Convención A — Area Path

El Test Case work item vive bajo una ruta de Area Path que codifica la capa:

```
<Proyecto>\QA\API
<Proyecto>\QA\Web
```

Variables de entorno:

```bash
export ADO_AREA_API="<Proyecto>\QA\API"
export ADO_AREA_WEB="<Proyecto>\QA\Web"
```

Un Test Case cuyo `System.AreaPath` no empieza con ninguno de los dos valores queda **excluido**
del cálculo — no se cuenta ni como automatizado ni como manual.

## Convención B — Tags

El Test Case lleva un tag de capa en `System.Tags` (campo de texto separado por `;` en Azure
DevOps):

```
capa:api
capa:web
```

Variables de entorno:

```bash
export ADO_TAG_API="capa:api"
export ADO_TAG_WEB="capa:web"
```

Un Test Case sin ninguno de los dos tags queda **excluido** del cálculo, igual que en la
convención A.

## Regla dura

- Solo se activa **una** convención por corrida (la que confirme el usuario en el intake) — no
  se combinan A y B "por si acaso", eso generaría doble conteo si un Test Case matchea ambas
  parcialmente.
- Todo Test Case fuera de la convención activa (BD, escritorio, u otra categoría no cubierta) se
  reporta en el informe como "excluido del universo API/Web — N casos", visible pero fuera del
  denominador. Nunca se descarta en silencio.
- Si el usuario no sabe qué convención usa su org: no adivinar. Sugerir correr
  `az boards query --wiql "SELECT [System.AreaPath],[System.Tags] FROM WorkItems WHERE
  [System.WorkItemType]='Test Case'"` y mirar los valores reales antes de decidir.
