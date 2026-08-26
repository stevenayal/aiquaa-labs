# Guía de uso — qa-productivity-skill

## Instalación

```bash
npx skills add aiquaa-labs/qa-productivity-skill
```

Para agentes específicos:

```bash
npx skills add aiquaa-labs/qa-productivity-skill -a cursor
npx skills add aiquaa-labs/qa-productivity-skill -a windsurf
```

## Requisitos

- **Modo real:** `az` CLI + extensión `azure-devops` (`az extension add --name azure-devops`),
  sesión autenticada (`az login`) con permisos de lectura sobre Test Plans, Pipelines y
  Repos/Pull Requests del proyecto objetivo.
- **Modo ejemplo:** ninguno — corre contra los fixtures de `examples/`, sin `az login` ni org
  real. Útil para validar la skill, o para explicarle el flujo a alguien sin exponer datos
  reales del banco.

## Flujo típico

1. `/productividad:configurar` — org, proyecto, y la pregunta que nunca se salta: ¿el proyecto
   clasifica API/Web por Area Path o por Tags? Sin esa respuesta no se calculan las métricas 1 y
   5 correctamente. También define el período del informe.
2. `/productividad:extraer` — corre los comandos `az`/`az devops invoke` documentados en
   `references/metrics-spec.md` (o lee los fixtures equivalentes en modo ejemplo).
3. `/productividad:auditar-profundidad` — para cada caso automatizado con PR válido, ubica el
   archivo de test por prefijo (`H_`, `T_`, `F_`/`S_`, `C_`) y aplica la heurística de
   `references/validation-depth-heuristics.md`.
4. `/productividad:consolidar` — agrega todo en `INFORME_PRODUCTIVIDAD_<...>.md`, con % real y %
   de calidad siempre como columnas separadas.
5. `/productividad:completo` corre los cuatro pasos de punta a punta, respetando los gates
   intermedios (filtro no confirmado, `az login` no verificado).

## Cuándo usar esto en vez de mirar Azure DevOps directamente

Azure DevOps ya muestra "% de casos automatizados" de forma nativa — pero ese número no
distingue automatización real de una que solo valida `HTTP 200`, ni excluye lo que hoy no es
automatizable (BD, escritorio), ni cruza contra evidencia de ejecución o estabilidad. Esta skill
suma valor cuando:

- Necesitás saber si el % de automatización que reporta el equipo es real o está inflado.
- Vas a presentar productividad de QA en una reunión de liderazgo y necesitás datos objetivos,
  no una estimación a ojo.
- Querés dar acompañamiento específico a alguien — el informe señala exactamente qué casos son
  superficiales, sin evidencia o inestables, no solo un score global.

## Diagramas de contexto de negocio

`references/diagrama-adopcion-ia-qa.md` y `references/diagrama-sdd-qa-integrado.md` no son
salidas que la skill regenere — son contexto versionado para explicar, en una reunión, por qué
estas métricas existen y cómo se conecta QA al ciclo SDD/CD de Desarrollo. Ambos excluyen a
propósito la arquitectura de ejecución/orquestación propia del equipo.

## Salidas

`INFORME_PRODUCTIVIDAD_<EQUIPO-o-PERSONA>_<PERIODO>.md` — informe consolidado por persona y
equipo. No modifica nada en Azure DevOps: es de solo lectura.
