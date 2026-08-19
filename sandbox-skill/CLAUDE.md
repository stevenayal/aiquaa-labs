# sandbox-skill — CLAUDE.md

## Project

Contract skill for the aiquaa Sandbox practice environment. Owned by aiquaa-labs.
No test-file generation here — this is the shared fact source other skills query.

## Structure

```
skills/sandbox/   ← main skill (contract summary + context intake)
references/       ← detailed lookup tables (endpoints, SQL, testids, grupos)
docs/             ← usage guide in Spanish
```

## Source of truth

Facts here were verified against:
- `Z:\Proyectos\aiquaa-sandbox-api` (lib/openapi.ts, lib/handle-sql-request.ts, lib/sql-validator.ts,
  lib/rate-limit.ts, lib/errors.ts, lib/api-route.ts, scripts/setup-db.sql, scripts/seed-data.sql)
- `Z:\Proyectos\aiquaa-sandbox-web` (lib/testids.ts, app/api/proxy/[...path]/route.ts)

If the sandbox API changes, re-verify against those files before editing this skill —
do not guess or extrapolate.

## Key facts other skills depend on

- Auth: `x-api-key` header only. No JWT.
- Rate limit: 30 req / 60s sliding window, per API key, on every authenticated route.
- Envelope: `{ data }` success, `{ error: { code, message, details? } }` failure.
- SQL sandbox: `qa_training` schema, 15-table whitelist, single statement, param count must match.
- Seed is deterministic and destructive (`TRUNCATE ... RESTART IDENTITY`) — ids are not stable
  across reseeds.
