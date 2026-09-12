# archify-skill

> Diagramas técnicos interactivos como HTML autocontenido — powered by [aiquaa](https://aiquaa.com/)

Skill para Claude Code, Cursor, Windsurf y 40+ agentes de IA. Convierte una descripción o
la evidencia de un repositorio en un mapa técnico navegable: arquitectura, workflow,
secuencia, flujo de datos y ciclo de vida.

Motor [Archify](https://github.com/tt-a1i/archify) v2.16.0 (MIT) **vendorizado** — sin
instalación, sin `npm install`, sin dependencias de runtime. Requisito único: **Node ≥18**.

---

## Dos variantes

| | `archify` | `archify-offline` |
|---|---|---|
| Peticiones del HTML generado | 2 (Google Fonts) | **0** |
| Tipografía | JetBrains Mono | stack del sistema (Consolas / SF Mono / DejaVu) |
| `brands capture <url>` | permitido | prohibido |
| Chequeo de versión | apagable | apagado por contrato |
| Compilador, schemas, 9 checks | — idénticos — | — idénticos — |

Un solo runtime compartido. La variante se elige con `ARCHIFY_TEMPLATE`.

**Usá `archify-offline`** en redes corporativas restringidas, entornos air-gapped, banca,
auditoría, o cuando el requisito sea que el artefacto no emita ninguna petición externa.

---

## ¿Qué incluye?

| Componente | Qué hace |
|------------|----------|
| `skills/archify/SKILL.md` | Variante online — contrato de autoría completo |
| `skills/archify-offline/SKILL.md` | Variante offline — mismo contrato + aislamiento de red |
| `bin/archify.mjs` | CLI: `validate`, `deliver`, `preview`, `compare`, `doctor`, `guide`, `brands` |
| `renderers/` | Compiladores deterministas por tipo de diagrama |
| `schemas/` | JSON Schema por tipo — la especificación que escribe el agente |
| `examples/` | 14 specs JSON de referencia (forma de los campos, no hechos a copiar) |
| `references/` | Contratos de autoría, entrega y viewer runtime |
| `delta/` | Comparación Before / Delta / After entre dos snapshots validados |

---

## Los 5 tipos

| Tipo | Para | Qué incluir en el pedido |
|---|---|---|
| `architecture` | Componentes, servicios, storage, límites de confianza | Alcance, componentes core, camino principal |
| `workflow` | CI/CD, aprobaciones, tool calls, runbooks | Participantes, orden, ramas, excepciones |
| `sequence` | Llamadas API, fallback de caché, auth, trazas async | Quién llama, a quién, retornos, timing |
| `dataflow` | Pipelines, linaje, PII, consumidores | Fuentes, transformaciones, stores, límites |
| `lifecycle` | Estados, reintentos, esperas, terminales | Estados, eventos, reintento y cancelación |

---

## Uso rápido

```bash
cd archify-skill
export ARCHIFY_UPDATE_CHECK_DISABLED=1
node bin/archify.mjs doctor
```

**Online:**

```bash
node bin/archify.mjs deliver architecture mi-spec.json salida.html --quality showcase --json
```

**Offline:**

```bash
export ARCHIFY_TEMPLATE=offline
node bin/archify.mjs deliver architecture mi-spec.json salida.html --quality showcase --json
```

Un pase válido reporta `"checksPassed": 9`, `"errors": 0`, `"warnings": 0`.

Verificar aislamiento del artefacto offline:

```bash
grep -oE 'https?://[a-zA-Z0-9./_?&=;+-]+' salida.html | grep -v 'w3.org'
```

Salida vacía = cero peticiones externas.

---

## Cómo se pide desde el agente

Sin repositorio:

```text
Usá archify-offline para diagramar: Navegador -> API -> caché Redis -> fallback PostgreSQL.
```

Con evidencia de código:

```text
Analizá este repositorio y usá archify para un diagrama de arquitectura runtime de alto nivel.
Mostrá 8-12 componentes core, un camino principal, dependencias externas y límites de confianza.
El detalle de soporte va en tarjetas, no en más aristas.
```

Refinamiento: `agregá Redis`, `mové auth a la izquierda`, `resaltá el camino de rollback`.

---

## Encaje en el stack aiquaa

No reemplaza ninguna skill QA. Es soporte visual:

- Arquitectura de una suite de automatización (qué prueba qué, dónde corre)
- Pipeline CI de pruebas — etapas, gates, publicación de resultados
- Flujo de datos bajo prueba — origen, transformación, verificación en BD
- Ciclo de vida de un defecto o de un caso de prueba
- Secuencia de llamadas API que cubre un caso funcional

Combina con `qa-orchestrator-skill` (para diagramar lo que el orquestador decidió),
`postman-newman-skill` / `hurl-skill` (secuencias API reales) y
`database-object-testing-skill` (linaje e impacto de objetos de BD).

---

## Evidencia — tres afirmaciones distintas

1. **`deliver`** → checks deterministas sobre el artefacto (SHA-256 + bytes)
2. **`visual-check`** → comportamiento acotado en un navegador real (necesita Chrome local)
3. **Revisión perceptual** → requiere una persona o un revisor con visión

Nunca se mezclan. Un comando con exit ≠ 0 nunca es éxito.

---

## Licencia y atribución

MIT. Motor: [tt-a1i/archify](https://github.com/tt-a1i/archify) v2.16.0, basado en
Cocoon-AI/architecture-diagram-generator (MIT, v1.0). El archivo `LICENSE` original se
conserva en la raíz del paquete.

Detalles de mantenimiento y del parche local sobre el upstream: [CLAUDE.md](./CLAUDE.md).
Guía de uso paso a paso: [docs/uso.md](./docs/uso.md).
