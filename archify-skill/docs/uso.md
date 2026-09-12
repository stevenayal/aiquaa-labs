# Guía de uso — archify-skill

## 0. Verificar el entorno

```bash
cd archify-skill
node --version          # debe ser >= 18
export ARCHIFY_UPDATE_CHECK_DISABLED=1
node bin/archify.mjs doctor
```

Esperado: 15 líneas `[ok]` y `Archify is ready.`

No hay paso de instalación. El motor está vendorizado en el repo.

---

## 1. Elegir variante

```bash
# Online — el HTML baja JetBrains Mono de Google Fonts (carga asíncrona)
unset ARCHIFY_TEMPLATE

# Offline — cero peticiones externas
export ARCHIFY_TEMPLATE=offline
```

Todo lo demás es idéntico: mismo compilador, mismos schemas, mismos 9 checks.

---

## 2. Elegir tipo de diagrama

| Necesitás mostrar… | Tipo |
|---|---|
| Componentes, servicios, storage, límites de confianza | `architecture` |
| Un proceso con pasos, gates y ramas | `workflow` |
| Quién llama a quién, en qué orden, con retornos | `sequence` |
| Origen → transformación → destino de datos | `dataflow` |
| Estados y transiciones de una entidad | `lifecycle` |

Si dudás:

```bash
node bin/archify.mjs guide "reintentos de un job de carga nocturna" --json
```

---

## 3. Escribir la especificación

Leé **solo** tres archivos: el schema del tipo, `schemas/common.schema.json`, y un ejemplo
JSON del mismo tipo en `examples/`.

El ejemplo sirve para la **forma de los campos**. No copies sus hechos: IDs nuevos,
vocabulario del dominio real, layout propio.

Reglas de arranque:

- Un camino principal claro, ramas cortas
- Máximo 12 nodos primarios
- `meta.quality_profile: "showcase"`
- Rutas y etiquetas automáticas — sin `via`, `channelX`, `channelY` ni `labelAt`
- Sin `meta.visual_preset`, sin `meta.subtitle`, sin `meta.engineering_profile`

Workflows nuevos: `schema_version: 2`.

---

## 4. Validar

```bash
node bin/archify.mjs validate architecture mi-spec.json --quality showcase --json
```

Leer el recibo:

| Campo | Qué esperar |
|---|---|
| `checksPassed` / `checkCount` | **9 / 9** — si dice 4, no es aceptación showcase |
| `errors` | **0** |
| `warnings` | **0** |
| `compositionStatus` | `"pass"` |

Si falla: cambiá solo el `subject` diagnosticado, verificá `evidence`, elegí un arreglo de
`supportedFixes`. Un control de geometría por reparación.

Si dos rondas seguidas no bajan el conteo de errores, pará y reportá los diagnósticos.

Diagnóstico de geometría en workflow v2:

```bash
node bin/archify.mjs validate workflow mi-spec.json --layout-json
```

---

## 5. Entregar

```bash
node bin/archify.mjs deliver architecture mi-spec.json salida.html --quality showcase --json
```

`deliver` congela los bytes de la especificación, renderiza, verifica y commitea el HTML de
forma atómica. Devuelve SHA-256 y bytes de ambos.

**Exit ≠ 0 nunca es éxito.** Una entrega fallida conserva el HTML anterior — no corras
`visual-check` sobre esa ruta o inspeccionarías el artefacto viejo.

Después de un `deliver` exitoso, el candidato queda **congelado**. No lo edites.

---

## 6. Verificar aislamiento (solo offline)

```bash
grep -oE 'https?://[a-zA-Z0-9./_?&=;+-]+' salida.html | grep -v 'w3.org' | sort -u
```

Salida vacía = cero peticiones externas. `w3.org` se excluye porque es el namespace XML de
SVG, no una descarga.

---

## 7. Evidencia de navegador (opcional)

```bash
node bin/archify.mjs visual-check salida.html --json
```

Necesita un Chrome/Chromium local. No necesita internet. Si no hay navegador disponible,
reportá esa limitación — no inventes evidencia.

---

## 8. Preview durante autoría (opcional, nunca por defecto)

```bash
node bin/archify.mjs preview architecture mi-spec.json salida.html --quality showcase
```

---

## Comparar dos versiones de una arquitectura

Para revisión de diseño o de PR — Before / Delta / After con recibo de máquina:

```bash
node bin/archify.mjs compare architecture \
  examples/checkout-platform.base.architecture.json \
  examples/checkout-platform.head.architecture.json \
  delta.html --json
```

Solo aplica a `architecture`. Opcional: `--receipt <ruta>` para el recibo de máquina.

Reporta agregados, eliminados, cambiados, movidos y re-ruteados exactos. **No** infiere
impacto, riesgo ni seguridad de merge.

---

## Marcas de producto

```bash
node bin/archify.mjs brands "postgresql" --json
```

Si hay preset, usá el ID canónico en el campo `brand` del nodo.
Si no hay preset: **omití `brand`**. Nunca infieras una marca de un rol vago.

`brands capture "<url>"` baja el logo desde internet — **prohibido en la variante offline**.

---

## Errores comunes

| Síntoma | Causa | Arreglo |
|---|---|---|
| `checksPassed: 4` | falta o está mal escrito `meta.quality_profile` | poner `"showcase"` exacto |
| Etiqueta tapada por una ruta | densidad | mové la etiqueta o la ruta; **no** borres la etiqueta |
| Arista cruzando un nodo no relacionado | demasiadas aristas | sacá aristas de bajo valor antes de rutear a mano |
| El HTML offline muestra otra fuente | esperado | usa el stack del sistema, no JetBrains Mono |
| `Cannot find module` | corriste desde otra carpeta | `cd archify-skill` primero |
| Se cuelga tras el primer candidato | chequeo de versión sin red | `export ARCHIFY_UPDATE_CHECK_DISABLED=1` |
