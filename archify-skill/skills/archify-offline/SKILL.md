---
name: archify-offline
description: >
  Diagramas técnicos interactivos como HTML autocontenido, en modo aislado — cero
  peticiones de red, ni al generar ni al abrir el artefacto. Arquitectura, workflow,
  secuencia, flujo de datos y ciclo de vida. Motor Archify vendorizado (Node >=18,
  cero dependencias de runtime). Mismo compilador determinista y mismos 9 checks que
  `archify`; la única diferencia es que el HTML usa el stack monoespaciado del sistema
  en vez de bajar JetBrains Mono de un CDN. Usar en entornos air-gapped, redes
  corporativas restringidas, auditoría, banca, o cuando el usuario pida explícitamente
  que nada salga a internet. Para la variante con webfont usar `archify`.
license: MIT
metadata:
  version: "2.16"
  upstream: tt-a1i/archify
  based_on: Cocoon-AI/architecture-diagram-generator (MIT, v1.0)
  variant: offline
---

Archify render diagram. No red. Nunca. Claude write JSON. Motor valida. Terse output.

---

## Qué es esta skill

Idéntica a `archify` en compilador, schemas, validación y capacidades del viewer.
La diferencia es **una sola**: el contrato de red.

| | `archify` | `archify-offline` |
|---|---|---|
| Peticiones del artefacto generado | 2 (Google Fonts) | **0** |
| Tipografía | JetBrains Mono vía CDN | stack monoespaciado del sistema |
| `brands capture <url>` | permitido | **prohibido** |
| Chequeo de versión | apagable | **apagado por contrato** |
| Compilador / schemas / 9 checks | idénticos | idénticos |

Ambas comparten el mismo runtime vendorizado en `archify-skill/`. La variante se
selecciona con la variable `ARCHIFY_TEMPLATE`.

## Contrato de aislamiento — obligatorio

Exportá esto **antes** de cualquier comando. No es opcional en esta skill:

```bash
export ARCHIFY_UPDATE_CHECK_DISABLED=1
export ARCHIFY_TEMPLATE=offline
```

Qué garantiza cada una:

- `ARCHIFY_UPDATE_CHECK_DISABLED=1` — corta el chequeo de versión antes de tocar la red
  (`scripts/check-update.mjs`, retorno temprano).
- `ARCHIFY_TEMPLATE=offline` — usa `assets/template.offline.html`, sin el `<link>` a
  Google Fonts. El HTML resultante no emite ninguna petición externa.

**Prohibido en esta variante**: `node bin/archify.mjs brands capture "<url>"` — es la
única ruta del motor que baja un recurso remoto. Usá solo los brand-marks empaquetados:

```bash
node bin/archify.mjs brands "<nombre>" --json
```

Si no hay preset para esa marca, **omití el campo `brand`**. Nunca inventes una marca ni
la infieras de un rol vago como "base de datos".

## Verificación del aislamiento

Comprobá que el artefacto no tiene URLs externas:

```bash
grep -oE 'https?://[a-zA-Z0-9./_?&=;+-]+' <salida.html> | grep -v 'w3.org' | sort -u
```

Salida vacía = cero peticiones externas. `w3.org` se excluye porque es el namespace XML
de SVG, no una descarga.

## Raíz del paquete

```bash
cd archify-skill
export ARCHIFY_UPDATE_CHECK_DISABLED=1 ARCHIFY_TEMPLATE=offline
node bin/archify.mjs doctor
```

## Ruta rápida de autoría

1. **Elegí el tipo**: `architecture`, `workflow`, `sequence`, `dataflow` o `lifecycle`.

2. **Leé solo lo necesario**: un schema en `schemas/`, más `schemas/common.schema.json`,
   más un ejemplo JSON en `examples/`. Nada más. El ejemplo sirve para la **forma de los
   campos**, no para copiar hechos. Autoría fresca = IDs nuevos y estables, vocabulario
   del dominio real, layout propio. Workflows nuevos usan `schema_version: 2`; mantené
   `schema_version: 1` solo al preservar la geometría fija de un workflow existente.

3. **Artefacto primero**: la siguiente acción escribe el candidato JSON. No planifiques
   coordenadas en prosa. Camino principal claro, ramas cortas, etiquetas escasas, máximo
   12 nodos primarios. `meta.quality_profile: "showcase"` salvo pedido explícito de mapa
   denso `standard`. Rutas y etiquetas automáticas primero. No agregues `via`, `channelX`,
   `channelY` ni `labelAt` antes de que un diagnóstico lo pida; un control de geometría
   por reparación como máximo.

4. **Validá después de cada edición** y justo antes de entregar:

   ```bash
   node bin/archify.mjs validate <tipo> <candidato.json> --quality showcase --json
   ```

   Un recibo con solo 4 checks es validación básica, **no** aceptación showcase. Un pase
   showcase reporta **9 checks, 0 errores, 0 warnings**. Si falta o está mal escrito
   `meta.quality_profile`, corregí eso antes que la geometría. Geometría de workflow v2:
   `node bin/archify.mjs validate workflow <candidato.json> --layout-json`.
   Una validación final que pasa **congela** el candidato.

5. **Entregá** con el template offline:

   ```bash
   ARCHIFY_TEMPLATE=offline node bin/archify.mjs deliver <tipo> <candidato.json> <salida.html> --quality showcase --json
   ```

   Exit distinto de cero **nunca** se reporta como éxito. Una entrega fallida preserva el
   output anterior — no corras `visual-check` sobre esa ruta. Si falla la validación,
   cambiá solo el `subject` diagnosticado, verificá `evidence`, elegí de `supportedFixes`
   y reintentá. Seguí mientras el conteo de errores baje a un mínimo nuevo. Si dos rondas
   seguidas no mejoran ese mínimo, pará y reportá los diagnósticos sin adornos.

**No leas** `renderers/shared/geometry.mjs`, código de renderers, del validador, tests ni
benchmarks antes del primer candidato.

## Router de tipo

| Tipo | Para |
|---|---|
| `architecture` | Componentes, servicios, límites cloud/seguridad, infraestructura |
| `workflow` | Procesos, gates de aprobación, tool calls, runbooks, CI/CD |
| `sequence` | Cadenas de llamadas API, ciclos de vida de request, trazas async, retornos |
| `dataflow` | Pipelines, ETL/ELT, linaje, gobernanza, consumidores |
| `lifecycle` | Transiciones de estado, reintentos, estados de espera y terminales |

Si hay ambigüedad: `node bin/archify.mjs guide "<escenario>" --json` (comando local, sin red).

## Entrada Mermaid

Leé Mermaid por topología y significado, después escribí JSON Archify fresco.

- `flowchart` / `graph` → `workflow`, o `architecture` para mapa de componentes
- `sequenceDiagram` → `sequence`
- `stateDiagram` → `lifecycle`

## Invariantes de autoría

- Un camino principal obvio. Las ramas salen del nodo más cercano del camino principal.
  Sacá aristas de bajo valor antes de agregar controles de ruteo.
- Omití `meta.visual_preset` por defecto (abre en `classic`). Modo de color y preset son
  independientes: cambiar Claro/Oscuro debe preservar el preset.
- Omití `meta.subtitle` por defecto. No inventes subtítulos que repitan el título.
- Tipos de componente: `frontend`, `backend`, `database`, `cloud`, `security`,
  `messagebus`, `external`. Variantes: `default`, `emphasis`, `security`, `dashed`.
- Las etiquetas de relación son **datos semánticos**. Ante colisión: mové la etiqueta,
  ajustá ruta o espaciado, y recién después acortá el texto preservando el significado.
  Borrar una etiqueta no es una reparación de geometría.
- Omití `meta.engineering_profile` por defecto. Activá `deployment-ownership` solo si el
  usuario pide topología de despliegue productivo y los hechos se conocen — falla cerrado.
- Espaciado significa **hueco libre**, no distancia entre centros.
- Nunca aceptes una arista cruzando un nodo opaco no relacionado, un corredor compartido
  ambiguo, o una etiqueta tapando otra ruta.
- Idioma: seguí el dominante de la conversación. `meta.locale` solo controla la UI del
  viewer y admite `"en"` o `"zh-CN"`; para español omitilo y avisá que la UI fija del
  viewer queda en inglés. Preservá exactos nombres de producto, identificadores de código,
  comandos, protocolos, rutas de API y nombres de ambiente.

Leé `references/authoring-contract.md` solo cuando necesites enums de campos, matemática
de espaciado, reglas de reparación de geometría o evidencia de repositorio.

## Nota de tipografía

Sin el webfont, el artefacto usa la primera fuente disponible del stack:

```
ui-monospace, SFMono-Regular, Menlo, Consolas, 'DejaVu Sans Mono',
'Liberation Mono', 'Noto Sans Mono CJK SC', ... monospace
```

En Windows resuelve a **Consolas**, en macOS a **SF Mono**, en Linux a **DejaVu Sans Mono**.
Cambia el tipo de letra. Layout, colores semánticos, geometría, interactividad y exports
son idénticos a la variante online — validado con los 5 tipos de diagrama, 9/9 checks.

## Entrega y evidencia

`deliver` congela los bytes exactos de la especificación en un snapshot privado, renderiza,
verifica, commitea el HTML de forma atómica y reporta SHA-256 y bytes. Eso es **evidencia
determinista de artefacto** — no prueba el viewer en un navegador.

Evidencia de navegador acotada, sin modificar ni re-renderizar el HTML entregado:

```bash
node bin/archify.mjs visual-check <salida.html> --json
```

`visual-check` usa un navegador local. No requiere internet, pero sí un Chrome/Chromium
disponible en la máquina. Si no hay, reportá esa limitación en vez de inventar evidencia.

Mantené las tres afirmaciones separadas:

1. `deliver` prueba checks deterministas de artefacto
2. `visual-check` prueba comportamiento acotado en un navegador real
3. La revisión visual perceptual requiere una persona o un revisor con visión

Nunca declares una inspección visual que no hiciste.

## Salida a reportar

Ruta del HTML verificado, tipo de diagrama, resumen de validación, recibo de
especificación/artefacto, **confirmación de cero URLs externas**, estado de evidencia de
navegador, estado de revisión visual — honesto. Un comando con exit distinto de cero nunca
es éxito.
