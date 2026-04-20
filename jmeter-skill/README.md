# jmeter-skill

> Pruebas de rendimiento y estrés de APIs con Apache JMeter — powered by [aiquaa](https://aiquaa.com/)

Skill para Claude Code, Cursor, Windsurf y más de 40 agentes de IA. A partir de una URL o especificación, genera todo lo necesario para correr una prueba de estrés real: plan `.jmx`, datos CSV, pipeline CI e informe PDF con veredicto automático.

---

## ¿Qué problema resuelve?

Configurar JMeter manualmente para un escenario de estrés real toma horas: definir thread groups, CSV data sets, extractores de token, assertions, listeners y pipelines CI. Esta skill lo genera en segundos a partir de una conversación — con los patrones correctos desde el inicio.

---

## ¿Qué incluye?

| Componente | Descripción |
|------------|-------------|
| `skills/jmeter/SKILL.md` | Instrucciones del agente — genera `.jmx`, CSV, pipelines y reportes |
| `examples/P_EXAMPLE_API.jmx` | Plan de prueba completo: login, extracción de token, endpoint bajo estrés |
| `examples/D_EXAMPLE_API.csv` | Archivo de datos de ejemplo (20 usuarios) |
| `examples/Y_EXAMPLE_API_jmeter.yml` | Pipeline Azure Pipelines listo para usar |
| `reporter/jmeter_report.py` | Generador de informe PDF con métricas, percentiles y veredicto |

---

## Instalación

```bash
# Claude Code
npx skills add aiquaa-labs/jmeter-skill

# Cursor
npx skills add aiquaa-labs/jmeter-skill -a cursor

# Windsurf
npx skills add aiquaa-labs/jmeter-skill -a windsurf

# Cualquier otro agente
npx skills add aiquaa-labs/jmeter-skill
```

---

## Uso rápido

Activá la skill con cualquiera de estos triggers:

```
/jmeter:generate   → generar plan .jmx desde spec / curl / URL
/jmeter:csv        → generar o actualizar archivo de datos CSV
/jmeter:fix        → analizar y reparar plan fallido o resultado anómalo
/jmeter:ci         → generar pipeline Azure Pipelines
/jmeter:run        → mostrar el comando de ejecución correcto
/jmeter:report     → analizar .jtl y generar descripción del PDF
```

La skill siempre recolecta contexto antes de generar — URL, endpoints, carga, auth, datos CSV.

---

## Escenario de estrés por defecto

```
Threads (usuarios): 1000
Loops por thread:   30
Total requests:     30.000
Ramp-up:            0 s  (golpe instantáneo)
Think Time:         ninguno
```

Todos los parámetros son configurables en la conversación o como flags en el comando de ejecución:

```bash
jmeter -n -t P_MI_API.jmx -l R_MI_API.jtl \
  -Jthreads=500 -Jloops=60 -JrampUp=30
```

---

## Datos variables con CSV

JMeter puede usar un dato diferente por cada request. La skill genera el archivo `D_*.csv` con la estructura correcta:

```csv
username,password,resource_id
user001,pass001,uuid-001
user002,pass002,uuid-002
```

El CSV se recicla automáticamente — con 20 filas cubre 30.000 requests sin cortes.

---

## Informe PDF

```bash
pip install reportlab pandas

python reporter/jmeter_report.py \
  --results  results/R_MI_API.jtl \
  --api-name "Mi API" \
  --threads  1000 \
  --loops    30 \
  --author   "Nombre — email@empresa.com" \
  --repo-url "https://github.com/org/repo" \
  --api-version "v1.0.0"
```

El informe incluye portada con estadísticas, tabla de percentiles (P90/P95/P99), detalle por sampler, top errores y veredicto automático:

| Veredicto | Condición |
|-----------|-----------|
| ✅ Aguanta la carga | Error rate ≤ 2% y P95 ≤ 3000 ms |
| ⚠️ Degradación detectada | Error rate > 2% o P95 > 3000 ms |
| ❌ Colapso bajo estrés | Error rate > 10% |

Salida: `INFORME_PERF_MI_API.pdf`

---

## Convención de nombres

| Tipo | Patrón | Ejemplo |
|------|--------|---------|
| Plan de prueba | `P_NOMBRE_DE_API.jmx` | `P_PAYMENTS_API.jmx` |
| Datos CSV | `D_NOMBRE_DE_API.csv` | `D_PAYMENTS_API.csv` |
| Resultados | `R_NOMBRE_DE_API.jtl` | `R_PAYMENTS_API.jtl` |
| Informe PDF | `INFORME_PERF_NOMBRE_DE_API.pdf` | `INFORME_PERF_PAYMENTS_API.pdf` |
| Pipeline CI | `Y_NOMBRE_DE_API_jmeter.yml` | `Y_PAYMENTS_API_jmeter.yml` |

---

## Estructura del repositorio

```
jmeter-skill/
├── skills/jmeter/
│   └── SKILL.md                      ← instrucciones del agente
├── examples/
│   ├── P_EXAMPLE_API.jmx             ← plan de prueba de ejemplo
│   ├── D_EXAMPLE_API.csv             ← datos de ejemplo
│   └── Y_EXAMPLE_API_jmeter.yml      ← pipeline Azure de ejemplo
├── reporter/
│   ├── jmeter_report.py              ← generador de PDF
│   └── requirements.txt
├── docs/
│   └── uso.md
└── .github/workflows/
    └── Y_JMETER_SKILL_CI.yml
```

---

## Stack de skills aiquaa

| Skill | Tipo de prueba |
|-------|----------------|
| [`postman-newman-skill`](../postman-newman-skill) | Funcional — colecciones Postman, GUI-first |
| [`hurl-skill`](../hurl-skill) | Funcional — declarativo, diff-friendly, CI-native |
| [`jmeter-skill`](.) | Rendimiento — estrés, carga, percentiles, PDF |

---

## Créditos

Creado por [aiquaa](https://aiquaa.com/) — *Saber es calidad*

## Licencia

MIT
