# jmeter-skill — CLAUDE.md

## Project

Performance and stress testing skill for Apache JMeter. Owned by aiquaa-labs.
Lives at `Z:\Proyectos\aiquaa-labs\jmeter-skill`.
Complementary to postman-newman-skill (functional) and hurl-skill (declarative CI).
JMeter = performance / stress / load testing.

## Structure

```
skills/jmeter/   ← main skill (context intake + .jmx generation)
examples/        ← P_, D_, Y_ templates
reporter/        ← PDF report generator (Python + pandas + reportlab)
docs/            ← usage guide in Spanish
.github/workflows/ ← CI for the skill itself
```

## File naming convention

- Test plans: `P_NOMBRE_DE_API.jmx`
- Data CSV:   `D_NOMBRE_DE_API.csv`
- Results:    `R_NOMBRE_DE_API.jtl`
- Reports:    `INFORME_PERF_NOMBRE_DE_API.pdf`
- Pipelines:  `Y_NOMBRE_DE_API_jmeter.yml`

## Stress scenario standard

- Threads: 1000
- Loops:   30
- Total:   30.000 requests
- Ramp-up: 0 (instantaneous hit)
- No Think Time

## Reporter

- Entry: `reporter/jmeter_report.py`
- Deps:  `reporter/requirements.txt` (reportlab, pandas)
- Input: `.jtl` (CSV format from JMeter Simple Data Writer)
- Output: PDF with cover + sampler detail + top errors + verdict
- Verdict logic: error_rate > 10% = COLAPSO | > 2% or p95 > 3000ms = DEGRADACIÓN | else = AGUANTA

## Key rules

- Never hardcode URLs or tokens in .jmx — always User Defined Variables or CSV
- CSV: recycle=true, stopThread=false, shareMode=all
- Pipeline: always continueOnError on jmeter step, report generates condition=always
- Reporter lang: Spanish output, HTTP methods/codes stay in English
