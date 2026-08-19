# Checklist de entrega — por semana

Referencia para `/curso:entregar` (paso 1.3, artefactos esperados) y `/curso:revisar`
(revisión entre pares). Ajustar según el avance real de la clase — esta tabla asume la
progresión estándar del curso a partir de la semana 3 (ver README raíz del monorepo).

| Semana | Tema | Artefactos esperados |
|--------|------|------------------------|
| 3 | BDD — features y steps | `F_GRUPO_NN_MODULO.feature`, `S_*.steps.ts`, `world.ts`/`hooks.ts` si es la primera entrega |
| 4 | BDD + verificación en BD | lo de semana 3 + steps `@db` usando `sql/select`, evidencia de corrida (`cucumber-report.json`) |
| 5 | API funcional — Postman/Hurl | `C_*.json`+`E_*.json` o `H_*.hurl`+`V_*.env`, con `pm.test()`/asserts agregados |
| 6 | E2E web — Playwright | `T_*.spec.ts`, `pages/*Page.ts`, uso de `data-testid` (ver skill sandbox) |
| 7 | Rendimiento — JMeter | `P_*.jmx` property-driven, al menos una corrida `baseline` y una de otro perfil, `INFORME_PERF_*.pdf` |
| 8 | Integración final | pipeline CI (`Y_*.yml`) corriendo en el repo del alumno, informe consolidado |

## Checklist genérico (toda semana)

- [ ] No hay secretos en el diff (API keys, `.env`, connection strings) — ver escaneo del paso 1.1
- [ ] Los tests/escenarios corren localmente sin error de sintaxis (`--dry-run` cuando aplica)
- [ ] Nombres de archivo siguen la convención de prefijos del stack (`F_`, `S_`, `P_`, `T_`, etc.)
- [ ] El PR describe qué se automatizó y cómo correrlo — no solo "semana N"
- [ ] Si hay `TODO` de `ocr-bdd-skill` sin resolver, están listados explícitamente en el PR
