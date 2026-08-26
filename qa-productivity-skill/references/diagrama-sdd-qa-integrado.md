# Diagrama 2 — Flujo SDD con QA integrado

> **Nota:** este diagrama NO incluye la arquitectura de ejecución/orquestación propia del
> equipo (portal, tareas programadas, gateway) — esa queda deliberadamente fuera de la reunión
> con líderes para no dar excusa de "esperemos a que esté listo el portal". Si se edita este
> archivo, mantener esa exclusión.

> Versión interactiva (Artifact): https://claude.ai/code/artifact/787993ed-b273-46b5-8f72-5a3c39df8365

## Diagrama

```mermaid
flowchart LR
    E1["1. Negocio / Product Owner<br/>Define requerimientos vía chatbot;<br/>la IA pregunta y genera la historia de usuario"]
    E2["2. Líder técnico + IA<br/>Define el reglamento técnico<br/>(reglas de negocio + spec técnica)"]
    E3["3. IA (desarrollo)<br/>Desarrolla la funcionalidad,<br/>genera pruebas unitarias,<br/>entrega Pull Request"]
    E4["4. Analista de QA<br/>Revisa el resultado,<br/>releva necesidades funcionales<br/>y de rendimiento no cubiertas"]
    E5["5. QA + IA<br/>(Claude Code + skills)<br/>Ejecuta pruebas funcionales manuales,<br/>confirma el desarrollo,<br/>dispara la automatización"]
    E6["6. QA<br/>Entrega el Pull Request<br/>de automatización"]

    G{"Gate de calidad<br/>(qa-productivity-skill)<br/>% real · evidencia · profundidad<br/>· estabilidad · cantidad"}

    E1 --> E2 --> E3 --> E4 --> E5 --> E6 --> G
    G -->|"cumple"| P["Pipeline / CD"]
    G -->|"no cumple"| E5

    style G fill:#f7d774,stroke:#a67c00,color:#1a1a1a
```

## Por qué importa para el objetivo de negocio

- **QA es una etapa formal del ciclo, no un paso posterior y desconectado.** El flujo integra a
  QA desde la etapa 4 — revisando el resultado de la IA de desarrollo y relevando lo que aún no
  está cubierto, con un rol equivalente al del líder técnico pero del lado de calidad — hasta la
  etapa 6, entregando la automatización. Esto es lo que mantiene a QA dentro del mismo ritmo de
  entrega que Desarrollo, en vez de heredar trabajo acumulado al final del ciclo.
- **El gate de calidad es lo que cierra el círculo con la medición real.** El trabajo no termina
  cuando se entrega el Pull Request de automatización — termina cuando esa automatización tiene
  calidad suficiente para sostenerse en el tiempo dentro del pipeline y reducir de verdad el
  esfuerzo manual. Ese gate es exactamente lo que mide `qa-productivity-skill` sobre Azure
  DevOps: % real, evidencia de ejecución, profundidad de validación, estabilidad y cantidad —
  nunca solo cantidad.
- **Es la condición para sostener el volumen de las 200+ APIs.** Un flujo donde QA participa
  desde la definición de la historia hasta el gate de calidad es lo que hace posible absorber el
  volumen que viene sin que QA se convierta en cuello de botella — y es la referencia que todo
  el equipo puede consultar para entender su rol dentro del ciclo SDD/CD, no una decisión
  aislada de una sola persona o proyecto.
