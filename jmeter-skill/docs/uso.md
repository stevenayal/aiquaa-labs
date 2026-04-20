# Guía de uso — jmeter-skill

## Instalación

```bash
npx skills add aiquaa-labs/jmeter-skill
```

Para agentes específicos:

```bash
npx skills add aiquaa-labs/jmeter-skill -a cursor
npx skills add aiquaa-labs/jmeter-skill -a windsurf
npx skills add aiquaa-labs/jmeter-skill -a cline
```

---

## Instalar JMeter localmente

```bash
# Windows — descargar binario desde:
# https://jmeter.apache.org/download_jmeter.cgi
# Extraer y agregar /bin al PATH

# Ubuntu / Debian
sudo apt-get install -y default-jdk
wget https://downloads.apache.org/jmeter/binaries/apache-jmeter-5.6.3.tgz
tar xzf apache-jmeter-5.6.3.tgz
export JMETER_HOME=$PWD/apache-jmeter-5.6.3
export PATH=$JMETER_HOME/bin:$PATH
jmeter --version
```

---

## Comandos disponibles

| Comando | Qué hace |
|---------|----------|
| `/jmeter:generate` | Genera `.jmx` desde spec, curl, código fuente o URL |
| `/jmeter:csv` | Genera o actualiza archivo CSV de datos de prueba |
| `/jmeter:fix` | Analiza y repara plan fallido o resultado anómalo |
| `/jmeter:ci` | Genera pipeline Azure Pipelines |
| `/jmeter:run` | Muestra el comando de ejecución correcto |
| `/jmeter:report` | Analiza `.jtl` y describe qué incluirá el PDF |

La skill siempre pregunta antes de generar. En orden de prioridad:
1. URL base de la API
2. Endpoint(s) a estresar
3. Configuración de carga (threads, loops, ramp-up)
4. Autenticación (Bearer, API Key, Basic, ninguna)
5. Body del request (para POST/PUT/PATCH)
6. Datos variables — CSV o User Defined Variables
7. Assertions (status code, response time, body)
8. Listeners y métricas adicionales
9. Metadata del informe (nombre, versión, repo, autor — opcionales)

---

## Escenario estándar aiquaa

```
Threads (usuarios):  1000
Loops por thread:    30
Total requests:      30.000
Ramp-up:             0 segundos (golpe instantáneo)
Think Time:          ninguno
```

Para modificar cualquier parámetro en tiempo de ejecución sin tocar el .jmx:

```bash
jmeter -n -t P_MI_API.jmx -l R_MI_API.jtl \
  -Jthreads=500 \
  -Jloops=60 \
  -JrampUp=30
```

---

## Uso rápido — ejecución local

### Correr el plan de ejemplo

```bash
jmeter -n \
  -t examples/P_EXAMPLE_API.jmx \
  -l results/R_EXAMPLE_API.jtl \
  -e -o results/dashboard/ \
  -JbaseUrl=localhost \
  -Jport=3000 \
  -Jprotocol=http \
  -JcsvFile=examples/D_EXAMPLE_API.csv
```

### Con más heap para 1000 threads

```bash
JVM_ARGS="-Xms2g -Xmx4g" jmeter -n \
  -t tests/jmeter/P_MI_API.jmx \
  -l results/R_MI_API.jtl \
  -e -o results/dashboard/
```

### Generar solo el dashboard HTML desde un .jtl existente

```bash
jmeter -g results/R_MI_API.jtl -o results/dashboard/
```

---

## CSV de datos — convención

El archivo de datos se llama `D_NOMBRE_DE_API.csv`.
Primera fila = headers. Los headers son los nombres de las variables en JMeter (`${variable}`).

```csv
username,password,resource_id
user001,pass001,uuid-001
user002,pass002,uuid-002
```

Reglas:
- Mínimo 1000 filas para 30.000 requests (JMeter recicla con `recycle=true`)
- Sin comillas salvo que el valor contenga comas
- Encoding UTF-8 sin BOM
- Va en `tests/jmeter/data/D_MI_API.csv`

---

## Generar el informe PDF

### Instalación de dependencias

```bash
pip install reportlab pandas
```

### Uso básico

```bash
python reporter/jmeter_report.py \
  --results results/R_MI_API.jtl \
  --api-name "Mi API" \
  --threads 1000 \
  --loops 30
```

### Uso completo

```bash
python reporter/jmeter_report.py \
  --results  results/R_MI_API.jtl \
  --output   results/INFORME_PERF_MI_API.pdf \
  --api-name "Mi API" \
  --threads  1000 \
  --loops    30 \
  --api-version "v1.2.0" \
  --repo-url "https://dev.azure.com/org/repo" \
  --author   "Juan Pérez — juan@empresa.com"
```

### Qué contiene el informe

- Portada con estadísticas principales: total requests, throughput, avg response time, error rate
- Tabla de percentiles: mínimo, mediana, P90, P95, P99
- Veredicto automático:
  - `AGUANTA LA CARGA` → error rate ≤ 2% y P95 ≤ 3000ms
  - `DEGRADACIÓN DETECTADA` → error rate > 2% o P95 > 3000ms
  - `COLAPSO BAJO ESTRÉS` → error rate > 10%
- Detalle por sampler: total, errores, error %, avg, P90, P95, max
- Top 10 errores por sampler y código HTTP
- Footer con autor y `Powered by skill jmeter · aiquaa.com`

---

## Azure Pipelines — puntos clave

El pipeline estándar (`Y_*_jmeter.yml`) incluye:

1. Instalación de Java + JMeter desde binario
2. Ejecución headless con `jmeter -n`
3. Generación de dashboard HTML (`-e -o`)
4. Generación de informe PDF (`jmeter_report.py`) con `condition: always()`
5. Upload de artefactos (JTL + PDF + dashboard)

Variables sensibles se pasan como secrets de Azure:
```yaml
env:
  JMETER_token: $(token)      # secret en Pipeline > Variables
  JMETER_api_key: $(apiKey)
```

En el .jmx se leen como:
```xml
<stringProp name="Argument.value">${__P(token,)}</stringProp>
```

---

## Convención de archivos

```
tests/jmeter/
  P_MI_API.jmx              ← plan de prueba
  data/
    D_MI_API.csv            ← datos de prueba
results/
  R_MI_API.jtl              ← resultados crudos (generado por JMeter)
  dashboard/                ← dashboard HTML (generado por -e -o)
  INFORME_PERF_MI_API.pdf   ← informe PDF (generado por reporter)
azure-pipelines/
  Y_MI_API_jmeter.yml       ← pipeline Azure
```

---

## Stack aiquaa — cuándo usar cada skill

| Necesidad | Skill |
|-----------|-------|
| Pruebas funcionales con GUI Postman | `postman-newman-skill` |
| Pruebas funcionales declarativas, CI-native | `hurl-skill` |
| Pruebas de rendimiento y estrés | `jmeter-skill` |

---

## Créditos

Creado por [aiquaa](https://aiquaa.com/) — *Saber es calidad*
