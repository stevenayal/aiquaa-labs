# hurl-skill — CLAUDE.md

## Project

QA automation skill for Hurl. Owned by aiquaa-labs. Lives at `Z:\Proyectos\aiquaa-labs\hurl-skill`.
Complementary to postman-newman-skill — Hurl for declarative CI, Postman/Newman for GUI exploration.

## Structure

```
skills/hurl/     ← main skill (context intake + generation)
examples/        ← H_, V_, Y_ templates
docs/            ← usage guide in Spanish
.github/workflows/ ← CI for the skill itself
```

## File naming convention

- Test files: `H_NOMBRE_DE_API.hurl`
- Variables local: `V_NOMBRE_DE_API.env`
- Variables staging: `V_NOMBRE_DE_API_STAGING.env`
- Pipelines Azure: `Y_NOMBRE_DE_API_hurl.yml`

## Key rules

- Never hardcode URLs in .hurl files — always `{{baseUrl}}`
- Never hardcode tokens — always `{{token}}` from vars file or HURL_ env var
- Azure CI: always use `--report-junit` + `PublishTestResults@2` — this is what makes results appear in the Tests tab
- `continueOnError: true` on hurl step + `failTaskOnFailedTests: true` on PublishTestResults — both required
- Reporter format for Azure: JUnit XML only — json and htmlextra do NOT publish to Azure Test Plans
- Skills: edit SKILL.md only
