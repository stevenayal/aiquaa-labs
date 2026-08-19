# qa-orchestrator-skill — CLAUDE.md

## Project

QA routing/orchestration skill for the aiquaa-labs stack. Owned by aiquaa-labs. Decides which
of the 10 existing skills (bdd, postman-newman, hurl, playwright, jmeter, flaui,
database-object-testing, ocr-bdd, sandbox, course-pr) apply to a given PR and/or user story,
can select multiple at once, invokes them in sequence, and produces an auditable decision log
plus a consolidated result report. Does not generate test artifacts itself — always defers to
the target skill's own `SKILL.md`.

## Structure

```
skills/qa-orchestrator/   ← main skill (intake, secret scan, classification, invocation, gates)
references/                ← signal-mapping.md (full scoring table), decision-log-schema.md,
                              consolidated-report-schema.md, prerequisites-check.md
examples/                   ← synthetic PR diffs + historia + worked bitácora/informe
docs/                       ← usage guide in Spanish
.github/workflows/          ← CI for the skill package itself (validates key files exist)
```

## Key rules

- Rule-based classification always runs first (path/extension grep on the diff, keyword grep
  on the story). The LLM only re-reads for genuine ties/ambiguity — never as the primary
  classifier. This keeps routing decisions reproducible and auditable.
- Secret scan (same regex as `course-pr-skill`: `sbx_[a-z0-9_]+`,
  `postgres(ql)?://user:pass@`, `Bearer [A-Za-z0-9._-]{20,}`) runs at the **start** of
  `/qa:analizar`, not only before delivery — a match halts the whole pipeline.
- Multi-skill selection is the default — a PR/story spanning multiple layers (API + UI, for
  example) selects and runs all matching skills, not just the top score.
- Confidence thresholds: ≥15 (path/extension match) = auto-select; 8–14 (keyword only) =
  listed but requires one grouped confirmation before generating; tie within 3 points on the
  same layer = ambiguous, ask the user, never guess; all-zero = stop, ask what to test.
- Never invokes another skill's generation logic directly — always reads that skill's own
  `SKILL.md` at `../<name>-skill/skills/<name>/SKILL.md` (or `../hurl-skill/SKILL.md` for the
  root-level exception) and follows its documented flow and commands.
- Every `/qa:analizar` run writes/updates `BITACORA_<...>.md` — the audit trail of what was
  detected, scored, decided, and (later) generated/run. Content hash enables idempotent
  re-runs: unchanged input reuses the prior decision instead of re-asking or re-generating.
- Prerequisite checks (`references/prerequisites-check.md`) run before generating/running each
  selected skill — a failed prerequisite skips that skill and reports why, never fails
  silently and never falls back to an unsafe alternative (e.g. never falls back to a direct DB
  driver when the REST gateway isn't configured).
- Never opens a PR, pushes, or merges itself — `/qa:entregar` always defers to
  `course-pr-skill` (`/curso:entregar`), which requires its own explicit confirmation before
  opening the PR. This is an intentional double gate, not redundant duplication.
- Consolidated report (`INFORME_CONSOLIDADO_<...>.md`) uses a gate pattern for the global
  verdict — the worst individual skill verdict wins, never an average.
