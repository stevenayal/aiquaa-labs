# Contratos de digest

Formato de salida de cada extractor tier 0. Estable: las otras skills parsean estos digests,
cambiarlos rompe a quien los consume.

## Invariantes — valen para todos

1. **Primera línea = identidad.** `TIPO · <nombre o archivo> · <timestamp UTC>`.
2. **Segunda línea = totales.** Siempre, aunque no haya fallos.
3. **Última línea = `CRUDO: <ruta> (<tamaño>)`.** El digest nunca es un callejón sin salida:
   siempre se puede volver al archivo original.
4. **El 100% de los fallos está representado.** Se agrupan en clusters con conteo (`×N`);
   nunca se descarta un fallo por brevedad. Si se cortan clusters por
   `QA_ROUTER_MAX_CLUSTERS`, la línea `… N clusters más (M fallos)` lo declara.
5. **Valores técnicos exactos.** Códigos, milisegundos, nombres de assert, rutas y mensajes
   de error van textuales. Se comprime la prosa, nunca la sustancia.
6. **Sin fallos ⇒ `FALLOS: ninguno`.** Nunca se omite la sección.
7. **≤ 60 líneas** en condiciones normales.

## Por tipo

### `NEWMAN`
```
NEWMAN · <colección> · <ts>
TOTALES: <N> requests · <N> asserts · <N> fallos · <N>s
FALLOS (<N>):
  <MÉTODO> <url> · "<assert>" · <mensaje>[ ×<N>]
CLUSTERS: <N>/<N> fallos (<P>%) son "<assert>" en <item>
CRUDO: <ruta> (<tamaño>)
```

### `JMETER`
```
JMETER · <archivo> · <ts>
MUESTRAS: <N> · errores <N> (<P>%) · duración <N>s · throughput <N>/s
LATENCIA (ms): p50 <N> · p90 <N> · p95 <N> · p99 <N> · max <N>
TOP <N> SAMPLERS POR p95:
  <label> · n=<N> · p95 <N>ms · p99 <N>ms · max <N>ms
ERRORES (<N> en <N> clusters):
  <label> · <código> · ×<N> · <mensaje>
VS BASELINE (<archivo>): p95 <±N>ms · errores <P>% → <P>%      ← solo con --baseline
CRUDO: <ruta> (<tamaño>)
```
Percentiles por interpolación lineal sobre el total de muestras (exactos, no muestreados).

### `JUNIT` / `NUNIT`
```
<JUNIT|NUNIT> · <archivo> · <ts>
TOTALES: <N> casos · <N> ok · <N> fallos · <N> omitidos · <N>s
FALLOS (<N>):
  <caso> [<categoría>] · <mensaje>[ ×<N>]
      ↳ <primera línea del stack>
CRUDO: <ruta> (<tamaño>)
```

### `PLAYWRIGHT`
```
PLAYWRIGHT · <archivo> · <ts>
TOTALES: <N> tests · <N> ok · <N> fallos · <N> flaky · <N>s
FALLOS (<N>):
  <suite> › <spec> · <archivo>:<línea>[ · <N> retries][ ×<N>]
      ↳ <mensaje de error>
FLAKY: <N> test(s) pasaron recién tras retry — revisar espera/estado
CRUDO: <ruta> (<tamaño>)
```

### `JMX`
```
JMX · <plan> · <ts>
ESTRUCTURA: <N> thread group(s) · <N> sampler(s) · <N> assertion(s) · <N> variable(s)
VARIABLES: / THREAD GROUPS: / SAMPLERS: / ASSERTIONS: / CSV DATA SET: / SALIDA:
CRUDO: <ruta> (<tamaño>)
```
Un plan sin assertions se declara explícito (`ASSERTIONS: ninguna — el plan no valida
respuestas`): es un hallazgo, no una omisión.

### `POSTMAN`
```
POSTMAN · <colección> · <ts>
ESTRUCTURA: <N> carpeta(s) · <N> request(s) · <N> test(s)
ÁRBOL:
  <carpeta>/
    <MÉTODO> <url> · "<nombre>" · <N> test(s)
SIN TESTS (<N>): <lista>
CRUDO: <ruta> (<tamaño>)
```

### `OPENAPI`
```
OPENAPI · <título> v<versión> · <ts>
ENDPOINTS: <N> de <N> (filtro: <tag|grep>)
  <MÉTODO> <ruta> · <summary> · req: <params> · body · → <códigos>
SCHEMAS (<N>):                                    ← solo con --schemas
CRUDO: <ruta> (<tamaño>)
```

### `AZURE DEVOPS`
```
AZURE DEVOPS · <archivo> · <ts>
RESULTADOS POR TEST (<N>):
  <test> · <N> corridas · <N> ok / <N> fallo(s)[  ⚠ inestable]
<COLECCIÓN> (<N>):
  <campo>=<valor> · …
CRUDO: <ruta> (<tamaño>)
```

### `DIFF`
```
DIFF · <rango> · <ts>
ARCHIVOS: <N>
  <ruta> · +<N>/-<N>          (o "· binario")
EXTENSIONES:
  <.ext> ×<N>
HUNKS:
  <ruta> @@ -<a>,<b> +<c>,<d> @@
CRUDO: <rango> (<N> B)
```
Nunca imprime una línea de contenido del diff. Máximo 3 hunks por archivo.

## Contratos de tier 1

Los subagentes tienen su contrato en su propio `agents/*.md`. Invariante compartida: bullets
estructurados, nombres exactos, número de línea siempre, y `FUERA DE ALCANCE: <motivo>`
cuando el pedido exige decidir o diagnosticar.
