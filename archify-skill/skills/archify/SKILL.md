---
name: archify
description: >
  Diagramas técnicos interactivos como HTML autocontenido — arquitectura, workflow,
  secuencia, flujo de datos y ciclo de vida. Motor Archify vendorizado (Node >=18,
  cero dependencias de runtime). Versión completa: usa JetBrains Mono desde CDN de
  Google Fonts. Genera JSON IR tipado, valida con 9 checks deterministas y entrega
  HTML con tema claro/oscuro, búsqueda, trazado de rutas, presentación y export
  PNG/SVG/WebM. Usar cuando el usuario pida diagramar arquitectura, infraestructura,
  topología cloud/seguridad/red, workflows técnicos, secuencias de llamadas API,
  ciclos de vida de request, pipelines de datos, ETL/ELT, linaje, máquinas de estado,
  o convertir Mermaid. Para entornos sin internet usar `archify-offline`.
license: MIT
metadata:
  version: "2.16"
  upstream: tt-a1i/archify
  based_on: Cocoon-AI/architecture-diagram-generator (MIT, v1.0)
  variant: online
---

Archify render diagram. Claude write JSON. Motor valida. Terse output.

---

## Qué es esta skill

Motor de renderizado determinista **vendorizado dentro de aiquaa-labs**. No se instala
nada: el runtime completo vive en `archify-skill/`. Requisito único: **Node ≥18**.

Vos escribís una especificación JSON pequeña y tipada. El motor la compila a un HTML
autocontenido con SVG inline. El HTML no depende de ningún servidor.

**Variante `online`** — el artefacto generado carga JetBrains Mono desde Google Fonts
de forma asíncrona (no bloquea el primer render). Si necesitás cero peticiones
externas, usá la skill hermana `archify-offline`.

## Raíz del paquete

Todos los comandos se ejecutan desde `archify-skill/` (la carpeta que contiene `bin/`):

```bash
cd archify-skill
node bin/archify.mjs doctor
```

## Ruta rápida de autoría

Ruta acotada para generación normal. No leas la referencia de Viewer Runtime salvo que
el usuario pregunte por esas funciones.

1. **Elegí el tipo**: `architecture`, `workflow`, `sequence`, `dataflow` o `lifecycle`.

2. **Leé solo lo necesario**: un schema en `schemas/`, más `schemas/common.schema.json`,
   más un ejemplo JSON en `examples/`. Nada más. El ejemplo sirve para la **forma de los
   campos**, no para copiar hechos. Autoría fresca = IDs nuevos y estables, vocabulario
   del dominio real, layout propio. Workflows nuevos usan `schema_version: 2`; mantené
   `schema_version: 1` solo al preservar la geometría fija de un workflow existente.

3. **Artefacto primero**: la siguiente acción escribe el candidato JSON. No planifiques
   coordenadas en prosa. Arrancá con un camino principal claro, ramas cortas, etiquetas
   escasas y máximo 12 nodos primarios. Poné `meta.quality_profile: "showcase"` salvo
   que el usuario pida explícitamente un mapa denso `standard`. Empezá con rutas y
   etiquetas automáticas. No agregues `via`, `channelX`, `channelY` ni `labelAt` antes
   de que un diagnóstico lo pida; como mucho un control de geometría por reparación.

4. **Validá después de cada edición** y justo antes de entregar:

   ```bash
   node bin/archify.mjs validate <tipo> <candidato.json> --quality showcase --json
   ```

   Un recibo con solo 4 checks es validación básica, **no** aceptación showcase. Un pase
   showcase reporta **9 checks, 0 errores, 0 warnings**. Si falta o está mal escrito el
   campo `meta.quality_profile`, corregí eso antes que la geometría. Para diagnosticar
   geometría de workflow v2: `node bin/archify.mjs validate workflow <candidato.json> --layout-json`.
   Una validación final que pasa **congela** el candidato: no lo edites después.

5. **Entregá** — `deliver` es el comando de aceptación final:

   ```bash
   node bin/archify.mjs deliver <tipo> <candidato.json> <salida.html> --quality showcase --json
   ```

   Exit distinto de cero **nunca** se reporta como éxito. Una entrega fallida preserva el
   output anterior — no corras `visual-check` sobre esa ruta: inspeccionaría el artefacto
   viejo. Si falla la validación, cambiá solo el `subject` diagnosticado, verificá
   `evidence`, elegí de `supportedFixes` y reintentá. Seguí mientras el conteo objetivo de
   errores baje a un mínimo nuevo. Si dos rondas seguidas no mejoran ese mínimo, pará y
   reportá los diagnósticos sin adornos.

**No leas** `renderers/shared/geometry.mjs`, código de renderers, del validador, tests ni
benchmarks antes del primer candidato. Inspeccioná implementación solo ante un diagnóstico
interno no soportado o después de dos reparaciones enfocadas fallidas.

## Router de tipo

| Tipo | Para |
|---|---|
| `architecture` | Componentes, servicios, límites cloud/seguridad, infraestructura |
| `workflow` | Procesos, gates de aprobación, tool calls, runbooks, CI/CD |
| `sequence` | Cadenas de llamadas API, ciclos de vida de request, trazas async, retornos |
| `dataflow` | Pipelines, ETL/ELT, linaje, gobernanza, consumidores |
| `lifecycle` | Transiciones de estado, reintentos, estados de espera y terminales |

Si hay ambigüedad: `node bin/archify.mjs guide "<escenario>" --json`.

## Entrada Mermaid

Leé Mermaid por topología y significado, después escribí JSON Archify fresco. No traduzcas
estilos de Mermaid mecánicamente.

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
  viewer queda en inglés. Preservá exactos los nombres de producto, identificadores de
  código, comandos, protocolos, rutas de API y nombres de ambiente.

Leé `references/authoring-contract.md` solo cuando necesites enums de campos, matemática
de espaciado, reglas de reparación de geometría o evidencia de repositorio.

## Marcas de producto

Identidad de marca es opcional y explícita.

```bash
node bin/archify.mjs brands "<nombre>" --json
```

Si no hay preset y el usuario aportó la URL oficial HTTP(S):

```bash
node bin/archify.mjs brands capture "<url>" --json
```

Esto **sí sale a internet**. Devuelve un objeto `brand` con digest pinneado. Nunca
infieras una marca desde un rol vago como "base de datos". El badge nunca reemplaza el
`type`, la etiqueta ni la relación.

## Red — qué hace esta variante

| Ruta | Cuándo | Control |
|---|---|---|
| Chequeo de versión (`scripts/check-update.mjs`) | tras el primer candidato | `ARCHIFY_UPDATE_CHECK_DISABLED=1` lo apaga |
| `brands capture <url>` | solo si vos lo invocás | no lo invoques |
| Google Fonts en el HTML generado | al abrir el artefacto | carga asíncrona, no bloquea |

**Vendorizado**: el chequeo de versión nunca descarga ni instala nada. Como esta copia
está congelada en el repo, apagalo:

```bash
export ARCHIFY_UPDATE_CHECK_DISABLED=1
```

## Entrega y evidencia

`deliver` congela los bytes exactos de la especificación en un snapshot privado, renderiza,
verifica, commitea el HTML de forma atómica y reporta SHA-256 y bytes de especificación y
artefacto. Eso es **evidencia determinista de artefacto** — no prueba el viewer en un navegador.

Evidencia de navegador acotada, sin modificar ni re-renderizar el HTML entregado:

```bash
node bin/archify.mjs visual-check <salida.html> --json
```

Mantené las tres afirmaciones separadas:

1. `deliver` prueba checks deterministas de artefacto
2. `visual-check` prueba comportamiento acotado en un navegador real
3. La revisión visual perceptual requiere una persona o un revisor con visión

Nunca declares una inspección visual que no hiciste.

Preview local durante autoría activa (nunca por defecto):

```bash
node bin/archify.mjs preview <tipo> <entrada>.json <salida>.html --quality showcase
```

## Verificación del entorno

```bash
node bin/archify.mjs doctor
node bin/archify.mjs demo <directorio-salida>
```

## Salida a reportar

Ruta del HTML verificado, tipo de diagrama, resumen de validación, recibo de
especificación/artefacto, estado de evidencia de navegador, estado de revisión visual —
honesto. Un comando con exit distinto de cero nunca es éxito.
