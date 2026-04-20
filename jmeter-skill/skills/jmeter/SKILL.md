---
name: jmeter
description: >
  Pruebas de rendimiento y estrés de APIs con Apache JMeter. Genera planes de
  prueba .jmx, archivos CSV de datos, scripts de ejecución CLI y reportes PDF
  de resultados. Escenarios de estrés reales: 30.000 peticiones sin unidad de
  tiempo, configuración de hilos (1000 users × 30 loops), datos aleatorios vía
  CSV, auth por Bearer token o API Key. Compatible con el stack aiquaa
  (caveman mode incluido).
  Usar cuando el usuario mencione "jmeter", "prueba de carga", "prueba de estrés",
  "rendimiento", "threads", "usuarios concurrentes", "throughput", ".jmx",
  o pida simular tráfico masivo contra una API.
---

JMeter plan write. Claude generate config. Terse output. No fluff.

---

## ¿Qué es JMeter en este contexto?

Apache JMeter ejecuta pruebas de rendimiento y estrés contra APIs HTTP/HTTPS.
El escenario base de aiquaa es **estrés real sin unidad de tiempo**:

```
1000 threads (usuarios) × 30 loops = 30.000 peticiones totales
Ramp-up: configurable (default 0 — golpe instantáneo)
Sin Think Time — máxima presión sobre el servidor
```

Los planes de prueba se generan como archivos `.jmx` (XML).
Los datos de prueba van en archivos `.csv` que JMeter lee con CSV Data Set Config.
Los resultados se exportan como `.jtl` (CSV) y se convierten en PDF con el reporter Python.

---

## Context Intake — SIEMPRE ejecutar primero

**Antes de generar cualquier archivo, recolectar contexto.** Sin excepciones.
El usuario puede dar nada, una URL, un curl, un contrato OpenAPI o código fuente.
Identificar qué falta y preguntar — una pregunta a la vez, en orden de prioridad.
Nunca generar el .jmx sin tener al menos URL base + un endpoint.

---

### Paso 1 — Detectar qué ya dio el usuario

| Señal | Qué aporta |
|-------|-----------|
| URL completa (`https://api.ejemplo.com/v1/users`) | baseUrl + path del endpoint |
| Comando curl | método + url + headers + body |
| Archivo `.jmx` existente | plan de prueba previo — expandir sin pisar |
| Archivo `.csv` de datos | dataset de usuarios, tokens, IDs a usar |
| Spec OpenAPI / Swagger | contrato completo: endpoints, schemas |
| DTO o validador del backend | reglas de campos — para datos realistas en CSV |
| Resultados `.jtl` previos | fallos o métricas a analizar |
| "quiero probar mi API" sin más | casi nada — preguntar |

---

### Paso 2 — Preguntar lo que falta (una pregunta a la vez)

Trabajar en este orden. Esperar respuesta antes de pasar a la siguiente.

#### Prioridad 1 — La URL base (siempre obligatoria)

> ¿Cuál es la URL base de la API?
> Ejemplo: `https://api.miempresa.com` o `http://localhost:8080`
>
> Si tenés un curl, pegalo directamente — lo proceso yo.

No continuar sin esto. Un path `/users` sin host no es una URL.

#### Prioridad 2 — El endpoint a estresar

> ¿Qué endpoint querés estresar?
>
> - Método + path: `POST /api/v1/login`, `GET /api/v1/productos`
> - ¿Es un solo endpoint o una secuencia de requests? (login → consulta → logout)
>
> Si son varios endpoints en secuencia, los agrego como samplers en el mismo Thread Group.

#### Prioridad 3 — Configuración de carga

> ¿Usamos la configuración estándar de estrés o la personalizás?
>
> Configuración estándar aiquaa:
> - Threads (usuarios): **1000**
> - Loops por thread: **30**
> - Total requests: **30.000**
> - Ramp-up: **0 segundos** (golpe instantáneo)
>
> Si querés otro valor de threads, loops o ramp-up, decime cuál.

Si el usuario confirma la estándar, usar: threads=1000, loops=30, rampUp=0.
Si personaliza, usar los valores que indique.

#### Prioridad 4 — Autenticación

> ¿La API requiere autenticación?
>
> - Sin auth (pública)
> - Bearer token estático → te pido el token o lo leo de la variable `${token}`
> - Bearer token dinámico → hay un endpoint de login que devuelve el token
> - API Key en header → ¿cómo se llama el header? (ej: `X-Api-Key`)
> - Basic Auth → usuario y contraseña
> - Otro

Si Bearer dinámico: el primer sampler será el login. Se captura el token con **JSON Extractor** y se usa como `${token}` en los siguientes samplers.

Si Bearer estático o API Key: va en el CSV o como User Defined Variable en el .jmx.

#### Prioridad 5 — Body del request (para POST / PUT / PATCH)

> Para `<MÉTODO> <endpoint>` necesito la estructura del body. Podés dar:
>
> - JSON de ejemplo: `{ "user": "valor", "pass": "valor" }`
> - Modelo o DTO del backend (cualquier lenguaje)
> - Archivo de validaciones
>
> Si el body usa datos variables (distinto usuario por request), los pongo en el CSV.

Nunca inventar nombres de campos. Si el usuario dice "ya sabés el body" sin haberlo dado — pedir de nuevo.

#### Prioridad 6 — Datos variables (CSV)

> ¿Cada request necesita datos distintos (usuario, ID, token, etc.) o todos usan los mismos valores?
>
> - **Mismos valores** → User Defined Variables en el .jmx
> - **Datos distintos por request** → CSV Data Set Config
>   - ¿Cuántas filas de datos tenés? (mínimo recomendado: 1000 para 30.000 requests)
>   - ¿Qué campos necesitás? (username, password, id, token, etc.)
>   - ¿Generamos el CSV de ejemplo con datos ficticios o tenés uno real?

Si el usuario pide CSV con datos ficticios: generar `D_NOMBRE_DE_API.csv` con al menos 20 filas representativas y la estructura correcta para que JMeter lo consuma.

Configuración estándar del CSV Data Set Config:
```
Filename: ${__P(csvFile,data/D_NOMBRE_DE_API.csv)}
Variable Names: (columnas del CSV)
Delimiter: ,
Recycle on EOF: True   ← recicla cuando se acaban las filas
Stop thread on EOF: False
Sharing mode: All threads
```

#### Prioridad 7 — Assertions (validaciones de respuesta)

> ¿Qué validamos en cada response?
>
> Sugerencias estándar:
> - HTTP Status: 200 o 201
> - Response time < X ms (ej: < 2000ms)
> - Body contiene texto específico (ej: `"id"`)
>
> Si no especificás, agrego assertion de status code solamente.

#### Prioridad 8 — Listeners y métricas a capturar

> ¿Qué métricas necesitás en el reporte?
>
> El reporte PDF estándar incluye:
> - Throughput (req/seg)
> - Average response time (ms)
> - 90th / 95th / 99th percentile
> - Error rate (%)
> - Min / Max response time
>
> ¿Necesitás algo adicional? (latencia por endpoint, distribución de errores, etc.)

#### Prioridad 9 — Metadata del informe (opcional)

> Para el informe PDF, ¿tenés esta info? (todo opcional)
>
> - **Nombre de la API** — ej: `Myths API`
> - **Versión** — ej: `v1.2.0`
> - **Link del repositorio** — ej: `https://dev.azure.com/org/repo`
> - **Autor** — ej: `Juan Pérez — juan@empresa.com`
>
> Si los tenés, aparecen en la portada del PDF.

---

### Paso 3 — Confirmar antes de generar

```
CONTEXTO DETECTADO:
  API:          <nombre>
  BASE URL:     <url completa>
  ENDPOINT(S):  <lista de MÉTODO /path>
  CARGA:        <threads> users × <loops> loops = <total> requests | ramp-up: <s>s
  AUTH:         <tipo o "ninguna">
  BODY:         <schema o "no aplica">
  DATOS CSV:    <columnas del CSV o "User Defined Variables">
  ASSERTIONS:   <status + response time + body>
  VERSIÓN API:  <versión o "no proporcionada">
  REPO:         <url o "no proporcionado">
  AUTOR:        <nombre o "anónimo">
  SALIDA:       P_<NOMBRE>.jmx + D_<NOMBRE>.csv + INFORME_PERF_<NOMBRE>.pdf

¿Confirmás o corregís algo antes de que genere?
```

Esperar confirmación. Luego generar.

---

### Escalation rules

- Usuario dice "quiero probar mi API" → preguntar Prioridad 1
- Usuario da URL sin endpoint → preguntar Prioridad 2
- Usuario da endpoint sin auth info → preguntar Prioridad 4
- Usuario pide "1000 usuarios" sin más → confirmar Prioridad 3 completa
- Usuario pide CSV pero no da campos → preguntar Prioridad 6 (campos del CSV)
- Usuario pide "arreglá el plan" sin .jmx → pedir el archivo o el error
- Usuario dice "ya te dije todo" con contexto incompleto → listar exactamente qué falta, de a uno

---

## Convención de nombres de archivos

**Siempre respetar este patrón. Sin excepciones.**

| Tipo | Patrón | Ejemplo |
|------|--------|---------|
| Plan de prueba | `P_NOMBRE_DE_API.jmx` | `P_MYTHS_API.jmx` |
| Datos CSV | `D_NOMBRE_DE_API.csv` | `D_MYTHS_API.csv` |
| Resultados JTL | `R_NOMBRE_DE_API.jtl` | `R_MYTHS_API.jtl` |
| Informe PDF | `INFORME_PERF_NOMBRE_DE_API.pdf` | `INFORME_PERF_MYTHS_API.pdf` |
| Pipeline Azure | `Y_NOMBRE_DE_API_jmeter.yml` | `Y_MYTHS_API_jmeter.yml` |

Reglas:
- `NOMBRE_DE_API` = UPPER_SNAKE_CASE
- Mismo nombre base en todos los archivos del mismo set
- El sufijo `_jmeter` en el YML distingue del pipeline de Newman/Hurl

Estructura recomendada:
```
tests/
  jmeter/
    P_MI_API.jmx          ← plan de prueba
    data/
      D_MI_API.csv        ← datos de prueba
results/
  R_MI_API.jtl            ← resultados crudos
  INFORME_PERF_MI_API.pdf ← informe generado
azure-pipelines/
  Y_MI_API_jmeter.yml     ← pipeline Azure
```

---

## Stack

- Runner: Apache JMeter 5.6+ (Java 11+)
- Formato de plan: `.jmx` (XML — JMeter Test Plan)
- Datos: CSV Data Set Config (`.csv`)
- Resultados: Simple Data Writer → `.jtl` (CSV format)
- Reporters: JMeter Dashboard (HTML) + reporter Python → PDF
- CI target: Azure Pipelines (`Y_*_jmeter.yml`)
- Ejecución headless: `jmeter -n -t plan.jmx -l results.jtl`

---

## Comandos

| Trigger | Acción |
|---------|--------|
| `/jmeter:generate` | Generar `.jmx` desde spec / curl / URL |
| `/jmeter:csv` | Generar o actualizar archivo CSV de datos |
| `/jmeter:fix` | Analizar y reparar un plan fallido o resultado anómalo |
| `/jmeter:ci` | Generar pipeline Azure Pipelines |
| `/jmeter:run` | Mostrar comando de ejecución correcto |
| `/jmeter:report` | Analizar `.jtl` y describir qué incluirá el PDF |

---

## Estructura de un plan .jmx — escenario estándar aiquaa

El .jmx es XML. Se compone de estos elementos en orden:

```
TestPlan
└── ThreadGroup (1000 users, 30 loops, ramp-up 0)
    ├── CSV Data Set Config (si hay datos variables)
    ├── HTTP Request Defaults (baseUrl, puerto, protocolo)
    ├── HTTP Header Manager (Content-Type, Authorization)
    ├── [Sampler 0] HTTP Request — Login (si auth dinámica)
    │   └── JSON Extractor — capturar token
    ├── [Sampler 1] HTTP Request — endpoint principal
    │   ├── Response Assertion (status code)
    │   ├── Duration Assertion (response time < X ms)
    │   └── Response Assertion (body contains)
    └── Simple Data Writer → results/R_MI_API.jtl
```

### Configuración del Thread Group — estrés real

```xml
<ThreadGroup>
  <stringProp name="ThreadGroup.num_threads">1000</stringProp>
  <stringProp name="ThreadGroup.ramp_time">0</stringProp>
  <intProp name="ThreadGroup.loops">30</intProp>
  <!-- loops × threads = 30.000 requests totales -->
</ThreadGroup>
```

### HTTP Request Defaults

```xml
<ConfigTestElement testclass="ConfigTestElement" testname="HTTP Request Defaults">
  <stringProp name="HTTPSampler.domain">${baseUrl}</stringProp>
  <stringProp name="HTTPSampler.port">${port}</stringProp>
  <stringProp name="HTTPSampler.protocol">${protocol}</stringProp>
  <stringProp name="HTTPSampler.implementation">HttpClient4</stringProp>
</ConfigTestElement>
```

### CSV Data Set Config

```xml
<CSVDataSet testname="CSV Data Set Config">
  <stringProp name="filename">${__P(csvFile,data/D_MI_API.csv)}</stringProp>
  <stringProp name="variableNames">username,password,token</stringProp>
  <stringProp name="delimiter">,</stringProp>
  <boolProp name="recycle">true</boolProp>
  <boolProp name="stopThread">false</boolProp>
  <stringProp name="shareMode">shareMode.all</stringProp>
</CSVDataSet>
```

### HTTP Header Manager — Bearer token

```xml
<HeaderManager testname="HTTP Header Manager">
  <collectionProp name="HeaderManager.headers">
    <elementProp name="Authorization" elementType="Header">
      <stringProp name="Header.name">Authorization</stringProp>
      <stringProp name="Header.value">Bearer ${token}</stringProp>
    </elementProp>
    <elementProp name="Content-Type" elementType="Header">
      <stringProp name="Header.name">Content-Type</stringProp>
      <stringProp name="Header.value">application/json</stringProp>
    </elementProp>
  </collectionProp>
</HeaderManager>
```

### HTTP Header Manager — API Key

```xml
<elementProp name="X-Api-Key" elementType="Header">
  <stringProp name="Header.name">X-Api-Key</stringProp>
  <stringProp name="Header.value">${api_key}</stringProp>
</elementProp>
```

### Sampler — Login + JSON Extractor (Bearer dinámico)

```xml
<HTTPSamplerProxy testname="Login">
  <stringProp name="HTTPSampler.path">/api/auth/login</stringProp>
  <stringProp name="HTTPSampler.method">POST</stringProp>
  <boolProp name="HTTPSampler.postBodyRaw">true</boolProp>
  <elementProp name="HTTPsampler.Arguments" elementType="Arguments">
    <collectionProp name="Arguments.arguments">
      <elementProp name="" elementType="HTTPArgument">
        <stringProp name="Argument.value">{"username":"${username}","password":"${password}"}</stringProp>
      </elementProp>
    </collectionProp>
  </elementProp>
</HTTPSamplerProxy>

<JSONPathExtractor testname="Extraer token">
  <stringProp name="JSONPathExtractor.referenceNames">token</stringProp>
  <stringProp name="JSONPathExtractor.jsonPathExprs">$.access_token</stringProp>
  <stringProp name="JSONPathExtractor.defaultValues">TOKEN_NO_ENCONTRADO</stringProp>
</JSONPathExtractor>
```

### Response Assertion — status code

```xml
<ResponseAssertion testname="Assert Status 200">
  <collectionProp name="Asserion.test_strings">
    <stringProp>200</stringProp>
  </collectionProp>
  <stringProp name="Assertion.test_field">Assertion.response_code</stringProp>
  <intProp name="Assertion.test_type">8</intProp> <!-- Contains -->
</ResponseAssertion>
```

### Duration Assertion — response time

```xml
<DurationAssertion testname="Assert Tiempo &lt; 2000ms">
  <longProp name="DurationAssertion.duration">2000</longProp>
</DurationAssertion>
```

### Simple Data Writer — resultados .jtl

```xml
<ResultCollector testname="Simple Data Writer">
  <boolProp name="ResultCollector.error_logging">false</boolProp>
  <objProp>
    <name>saveConfig</name>
    <value class="SampleSaveConfiguration">
      <time>true</time>
      <latency>true</latency>
      <timestamp>true</timestamp>
      <success>true</success>
      <label>true</label>
      <code>true</code>
      <message>true</message>
      <threadName>true</threadName>
      <responseData>false</responseData>
      <encoding>false</encoding>
      <assertions>true</assertions>
      <subresults>false</subresults>
      <responseHeaders>false</responseHeaders>
      <requestHeaders>false</requestHeaders>
      <responseDataOnError>false</responseDataOnError>
      <bytes>true</bytes>
      <threadCounts>true</threadCounts>
      <idleTime>true</idleTime>
      <connectTime>true</connectTime>
    </value>
  </objProp>
  <stringProp name="filename">results/R_MI_API.jtl</stringProp>
</ResultCollector>
```

---

## Archivo CSV de datos — formato estándar

El CSV se llama `D_NOMBRE_DE_API.csv`. Primera fila = headers (nombres de variables).
Sin espacios en los headers — JMeter los usa como `${variable}`.

### Ejemplo con username + password

```csv
username,password
user001,pass001
user002,pass002
user003,pass003
```

### Ejemplo con token estático por usuario

```csv
username,token
user001,eyJhbGc...abc001
user002,eyJhbGc...abc002
user003,eyJhbGc...abc003
```

### Ejemplo con ID de recurso

```csv
resource_id,api_key
550e8400-e29b-41d4-a716-446655440001,key-abc-001
550e8400-e29b-41d4-a716-446655440002,key-abc-002
```

Reglas del CSV:
- Mínimo 1000 filas para pruebas de 30.000 requests (JMeter recicla con `recycle=true`)
- Sin comillas a menos que el valor contenga comas
- Encoding: UTF-8 sin BOM
- El archivo va en `tests/jmeter/data/D_MI_API.csv`

---

## Ejecución CLI — referencia rápida

```bash
# Instalación (Ubuntu/Debian)
apt-get install -y default-jdk
wget https://downloads.apache.org/jmeter/binaries/apache-jmeter-5.6.3.tgz
tar xzf apache-jmeter-5.6.3.tgz
export JMETER_HOME=$PWD/apache-jmeter-5.6.3
export PATH=$JMETER_HOME/bin:$PATH

# Ejecución headless básica
jmeter -n \
  -t tests/jmeter/P_MI_API.jmx \
  -l results/R_MI_API.jtl \
  -e -o results/dashboard/

# Con parámetros en línea de comandos (override de variables)
jmeter -n \
  -t tests/jmeter/P_MI_API.jmx \
  -l results/R_MI_API.jtl \
  -Jthreads=1000 \
  -Jloops=30 \
  -JbaseUrl=https://api.miempresa.com \
  -JcsvFile=tests/jmeter/data/D_MI_API.csv

# Generar dashboard HTML (requiere -e -o en el run o post-run)
jmeter -g results/R_MI_API.jtl -o results/dashboard/

# Verificar sintaxis del .jmx sin correrlo
jmeter -n -t tests/jmeter/P_MI_API.jmx --loglevel INFO 2>&1 | head -30
```

---

## Pipeline Azure Pipelines — template estándar

```yaml
# Y_MI_API_jmeter.yml
# JMeter stress tests — MI API
# Generado por skill jmeter · aiquaa.com

trigger:
  branches:
    include:
      - main
      - develop

pool:
  vmImage: ubuntu-latest

variables:
  jmeterVersion: '5.6.3'
  planFile: 'tests/jmeter/P_MI_API.jmx'
  csvFile: 'tests/jmeter/data/D_MI_API.csv'
  resultsDir: '$(Build.ArtifactStagingDirectory)/jmeter-results'
  dashboardDir: '$(Build.ArtifactStagingDirectory)/jmeter-dashboard'

steps:

  - script: |
      echo "== Instalando Java =="
      sudo apt-get install -y default-jdk
      java -version

      echo "== Descargando JMeter $(jmeterVersion) =="
      wget -q https://downloads.apache.org/jmeter/binaries/apache-jmeter-$(jmeterVersion).tgz
      tar xzf apache-jmeter-$(jmeterVersion).tgz
      echo "##vso[task.prependpath]$(pwd)/apache-jmeter-$(jmeterVersion)/bin"
    displayName: Instalar JMeter

  - script: mkdir -p $(resultsDir) $(dashboardDir)
    displayName: Crear directorios de resultados

  - script: |
      jmeter -n \
        -t $(planFile) \
        -l $(resultsDir)/R_MI_API.jtl \
        -e -o $(dashboardDir) \
        -JcsvFile=$(csvFile) \
        -JbaseUrl=$(baseUrl)
    displayName: Ejecutar prueba de estrés JMeter
    continueOnError: true
    env:
      JMETER_token: $(token)

  - script: |
      pip install reportlab pandas --quiet
      python reporter/jmeter_report.py \
        --results $(resultsDir)/R_MI_API.jtl \
        --output $(resultsDir)/INFORME_PERF_MI_API.pdf \
        --api-name "MI API" \
        --threads 1000 \
        --loops 30
    displayName: Generar informe PDF
    condition: always()

  - task: PublishBuildArtifacts@1
    condition: always()
    inputs:
      pathToPublish: $(Build.ArtifactStagingDirectory)
      artifactName: jmeter-results
    displayName: Subir artefactos
```

---

## Formato de salida — análisis de resultados (`/jmeter:report`)

```
FILE: R_<NOMBRE>.jtl
PLAN: P_<NOMBRE>.jmx
CARGA: <threads> users × <loops> loops = <total> requests

MÉTRICAS:
  Throughput:        <n> req/seg
  Avg response time: <n> ms
  90th percentile:   <n> ms
  95th percentile:   <n> ms
  99th percentile:   <n> ms
  Min:               <n> ms
  Max:               <n> ms
  Error rate:        <n>%

ERRORES (si hay):
  ❌ <sampler> → HTTP <code> — <n> ocurrencias
     CAUSA: <una línea>
     FIX:   <acción>

VEREDICTO: ✅ API aguanta la carga | ⚠️ degradación | ❌ colapso bajo estrés
```

---

## Fallos comunes y fixes

| Síntoma | Causa | Fix |
|---------|-------|-----|
| `Connection refused` en todos los samplers | Servicio no levantado | Verificar que la API esté corriendo antes de JMeter |
| Error rate > 5% con status 503 | Servidor saturado — esperado en estrés | Documentar el límite encontrado en el informe |
| `${token}` sin resolver — literal en request | CSV no cargado o columna mal nombrada | Verificar `variableNames` en CSV Data Set Config |
| JMeter termina en segundos con 0 requests | `.jmx` mal formado | Correr con `--loglevel DEBUG` para ver el error |
| Todos los threads fallan en loop 1 | Login falla — token no capturado | Verificar JSON Extractor: path y default value |
| `OutOfMemoryError` en JMeter | Heap insuficiente para 1000 threads | Agregar `-Xms2g -Xmx4g` al comando de ejecución |
| Dashboard HTML vacío | `-e -o` path incorrecto o .jtl vacío | Verificar que el .jtl tenga datos antes de generar dashboard |
| Percentiles 99 altísimos, avg normal | Algunos threads colapsan — comportamiento esperado | Documentar en informe como límite de la API |

---

## Auto-Clarity

Salir de caveman para: error rate > 20% (documentar límite con precisión), hallazgos de seguridad encontrados durante estrés, recomendaciones de arquitectura para escalar. Retomar caveman después.

## Boundaries

Escribe archivos `.jmx`, `.csv`, comandos CLI, pipelines Azure Pipelines.
NO ejecuta JMeter — da los comandos listos para ejecutar.
NO inventa campos de body, reglas de validación ni valores de CSV — pregunta si no los tiene.
NO recomienda umbrales de performance sin datos reales — los describe como configurables.
"stop jmeter" o "normal mode": volver a estilo verbose.
