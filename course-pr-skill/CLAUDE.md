# course-pr-skill — CLAUDE.md

## Project

PR-based delivery skill for the aiquaa automation course. Owned by aiquaa-labs.
Platform-agnostic: detects GitHub (gh) vs Azure DevOps (az repos) from `git remote get-url origin`.

## Structure

```
skills/course-pr/  ← main skill (pre-flight + branch + commit + PR flow)
references/         ← checklist-entrega.md (expected artifacts per course week)
examples/           ← PULL_REQUEST_TEMPLATE.md
docs/                ← usage guide in Spanish
```

## Key rules

- Pre-flight (secret scan, tests, expected artifacts) always runs before any git mutation.
- Secret scan patterns: sbx_[a-z0-9_]+ (sandbox API keys), postgres(ql)://user:pass@,
  Bearer tokens ≥20 chars. A match aborts the flow — never auto-strip and continue silently.
- Never commit to main/master — always branch grupo-<n>/semana-<n>-<tema> first.
- Never push --force, never auto-merge, never open a PR without explicit user confirmation
  (opening a PR is an outward-facing action per the safety rules this session follows).
- Does not request or handle gh/az credentials — assumes the student already authenticated.
