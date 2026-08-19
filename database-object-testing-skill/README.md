# database-object-testing-skill

Skill y runner Node.js para probar objetos de bases de datos relacionales mediante una API REST. Compara comportamiento entre una versión base y una candidata, controla regresiones de costo y aplica buenas prácticas almacenadas como Markdown.

No requiere un driver Oracle ni acceso directo a la base de datos. El gateway REST corporativo es el único componente que se conecta al motor.

## Capacidades

- Vistas, SQL, funciones, procedimientos, paquetes y triggers.
- Assertions sobre cualquier ruta JSON.
- Comparación funcional base/candidato, con filas sin orden.
- Umbrales porcentuales para costo, lecturas y otras métricas normalizadas.
- Reglas humanas y ejecutables en `rules/*.md`.
- Informes PDF, JSON, Markdown y JUnit para CI.
- Token, URLs y datos sensibles desde variables de entorno.
- Respuestas y valores de evidencia omitidos de los informes por defecto.

## Inicio rápido

Requiere Node.js 20 o posterior. El runner no tiene dependencias npm. Para generar el PDF, instalar ReportLab:

```bash
npm run report:deps
```

En dos terminales:

```bash
npm run example:baseline
npm run example:candidate
```

En una tercera:

```powershell
$env:DBTEST_BASELINE_URL='http://127.0.0.1:4101'
$env:DBTEST_CANDIDATE_URL='http://127.0.0.1:4102'
$env:DBTEST_API_TOKEN='local-example-token'
npm run example:run
```

Los artefactos aparecen en `results/`, incluido `db-test-report.pdf`.

## Estructura

```text
database-object-testing-skill/
├── skills/test-database-objects/  skill instalable y referencias
├── src/                            runner Node.js
├── rules/                          reglas y buenas prácticas .md
├── reporter/                       generador del informe PDF
├── examples/                       suite y API simulada
└── test/                           pruebas del runner
```

## Integración real

Implementar en la API los endpoints normalizados documentados en `skills/test-database-objects/references/api-contract.md`. Si la API corporativa ya tiene otro formato, adaptar `src/api-client.mjs` o agregar un adaptador sin cambiar las suites.

Configurar siempre un usuario de solo los privilegios necesarios, listas permitidas de objetos, auditoría, límites de tiempo y rollback predeterminado. No apuntar suites de escritura a producción.

## Comandos

```bash
node src/cli.mjs validate-rules --rules rules
node src/cli.mjs run --suite examples/S_EXAMPLE.json --rules rules --output results
npm test
```

Si Python no está disponible en el `PATH`, usar `--python <ruta>` o definir `DBTEST_PYTHON`.

La ejecución termina con código `0` si todo pasa, `1` si hay fallos y `2` ante configuración inválida.
