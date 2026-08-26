# qa-productivity-skill — CLAUDE.md

## Project

QA productivity/quality scorecard skill for the aiquaa-labs stack. Owned by aiquaa-labs. Pulls
Azure DevOps state (Test Plans, Pipelines, Pull Requests) via the Azure CLI (`az boards`, `az
repos`, `az pipelines`, `az devops invoke`) and computes 5 metrics — real automation % (API/Web
only), pipeline execution evidence, validation depth, stability over time, and delivery
quantity — producing an auditable per-person/per-team Markdown report. Read-only: never writes
back to Azure DevOps, never generates or runs test automation itself. Also ships the two flow
diagrams (AI adoption in QA, SDD with QA integrated) used to explain why these metrics matter to
a leadership audience.

## Structure

```
skills/qa-productivity/    ← main skill (intake, extraction, depth heuristic, consolidation)
references/                 ← metrics-spec.md (full az command shapes per metric),
                               api-web-filter-convention.md, validation-depth-heuristics.md,
                               productivity-report-schema.md, and the two diagram source files
examples/                    ← mocked az/az-devops-invoke JSON + worked PR diffs + a fully
                               resolved example report — makes the skill testable without a
                               live Azure DevOps org or credentials ("modo ejemplo")
docs/                        ← usage guide in Spanish
.github/workflows/           ← CI for the skill package itself (validates key files exist)
```

## Key rules

- Never assumes the API/Web classification convention (Area Path vs. Tags) — always asks in
  intake and documents which one was active in the report header. Anything outside the active
  convention (DB objects, desktop) is excluded from the denominator, never guessed into a layer.
- "Real automation %" and "quality automation %" are always reported as two separate numbers,
  never averaged — a case only counts toward quality if it's Profunda (validation-depth
  heuristic) AND has execution evidence AND is stable. This is the mechanism that surfaces
  inflated automation numbers instead of hiding them behind a single score.
- Validation-depth classification (metric 3) reuses the sibling skills' own file-naming
  conventions (`H_*.hurl`, `T_*.spec.ts`, `F_*.feature`/`S_*.steps.ts`, `C_*.json`) to locate
  test files from a PR diff and grep for shallow-vs-deep assertion patterns — deterministic
  rules first, model judgment only for genuine ties, same spirit as
  `qa-orchestrator-skill/references/signal-mapping.md`.
- Connects via Azure CLI (`az` shelled out at runtime), not a custom Node.js REST client with a
  PAT — same pattern already used by `course-pr-skill` and `qa-orchestrator-skill`.
- Fully testable without a live Azure DevOps org via "modo ejemplo": every `az .../az devops
  invoke` call has an equivalent JSON/diff fixture under `examples/`, mapped 1:1 in
  `references/metrics-spec.md`.
- Never fills a data gap by inference — a missing PR link, missing pipeline evidence, or
  unlocatable test file is always reported explicitly under "Advertencias / datos incompletos",
  never silently estimated.
- Read-only, always — never opens a PR, comments on a work item, or modifies anything in Azure
  DevOps.
- The two business-context diagrams (`references/diagrama-adopcion-ia-qa.md`,
  `references/diagrama-sdd-qa-integrado.md`) deliberately exclude the team's own execution/
  orchestration architecture (portal, scheduled tasks, gateway) — that's out of scope for the
  leadership meeting these diagrams were built for.
