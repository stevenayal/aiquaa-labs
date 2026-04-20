# jmeter-skill

> Pruebas de rendimiento y estrés de APIs con Apache JMeter — powered by [aiquaa](https://aiquaa.com/)

Skill para Claude Code, Cursor, Windsurf y 40+ agentes de IA. Genera planes de prueba `.jmx`, archivos CSV de datos, pipelines Azure Pipelines e informes PDF de rendimiento — con salidas ultra-compactas estilo caveman.

---

## Escenario estándar aiquaa

```
1000 threads (usuarios) × 30 loops = 30.000 peticiones totales
Ramp-up: 0 segundos — golpe instantáneo
Sin Think Time — máxima presión sobre el servidor
```

---

## ¿Qué incluye?

| Componente | Qué hace |
|------------|----------|
| `skills/jmeter/SKILL.md` | Skill principal — genera `.jmx`, CSV, CI pipelines |
| `examples/P_EXAMPLE_API.jmx` | Plan de prueba de ejemplo con login + endpoint |
| `examples/D_EXAMPLE_API.csv` | Datos de prueba de ejemplo (20 usuarios) |
| `examples/Y_EXAMPLE_API_jmeter.yml` | Pipeline Azure Pipelines de ejemplo |
| `reporter/jmeter_report.py` | Generador de informe PDF con métricas y veredicto |

---

## Instalación

```bash
npx skills add aiquaa-labs/jmeter-skill
```

---

## Uso rápido

```
/jmeter:generate   → generar .jmx desde spec / curl / URL
/jmeter:csv        → generar o actualizar archivo CSV de datos
/jmeter:fix        → analizar y reparar plan fallido o resultado anómalo
/jmeter:ci         → generar pipeline Azure Pipelines
/jmeter:run        → mostrar comando de ejecución correcto
/jmeter:report     → analizar .jtl y describir qué incluirá el PDF
```

---

## Instalar JMeter localmente

```bash
# Windows — descargar desde:
# https://jmeter.apache.org/download_jmeter.cgi

# Ubuntu/Debian
sudo apt-get install -y default-jdk
wget https://downloads.apache.org/jmeter/binaries/apache-jmeter-5.6.3.tgz
tar xzf apache-jmeter-5.6.3.tgz
export PATH=$PWD/apache-jmeter-5.6.3/bin:$PATH
jmeter --version
```

---

## Generar informe PDF

```bash
pip install reportlab pandas

python reporter/jmeter_report.py \
  --results results/R_MI_API.jtl \
  --api-name "Mi API" \
  --threads 1000 \
  --loops 30 \
  --author "Juan Pérez — juan@empresa.com" \
  --repo-url "https://dev.azure.com/org/repo" \
  --api-version "v1.2.0"
```

Salida: `INFORME_PERF_MI_API.pdf`

---

## Convención de nombres

| Tipo | Patrón | Ejemplo |
|------|--------|---------|
| Plan de prueba | `P_NOMBRE_DE_API.jmx` | `P_MYTHS_API.jmx` |
| Datos CSV | `D_NOMBRE_DE_API.csv` | `D_MYTHS_API.csv` |
| Resultados | `R_NOMBRE_DE_API.jtl` | `R_MYTHS_API.jtl` |
| Informe PDF | `INFORME_PERF_NOMBRE_DE_API.pdf` | `INFORME_PERF_MYTHS_API.pdf` |
| Pipeline Azure | `Y_NOMBRE_DE_API_jmeter.yml` | `Y_MYTHS_API_jmeter.yml` |

---

## Estructura del repositorio

```
jmeter-skill/
├── skills/
│   └── jmeter/
│       └── SKILL.md
├── examples/
│   ├── P_EXAMPLE_API.jmx
│   ├── D_EXAMPLE_API.csv
│   └── Y_EXAMPLE_API_jmeter.yml
├── reporter/
│   ├── jmeter_report.py
│   └── requirements.txt
├── docs/
│   └── uso.md
└── .github/
    └── workflows/
        └── Y_JMETER_SKILL_CI.yml
```

---

## Stack de skills aiquaa

| Skill | Para qué |
|-------|----------|
| `postman-newman-skill` | Pruebas funcionales — colecciones GUI |
| `hurl-skill` | Pruebas funcionales — declarativo, CI-native |
| `jmeter-skill` | Pruebas de rendimiento y estrés |

---

## Créditos

Creado por [aiquaa](https://aiquaa.com/) — *Saber es calidad*

## Licencia

MIT
