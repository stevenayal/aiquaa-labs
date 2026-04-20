---
name: hurl
description: >
  Automatización de pruebas de API con Hurl — formato declarativo, diff-friendly,
  CI-native. Genera archivos .hurl, variables de entorno, pipelines Azure Pipelines
  y resumen de resultados. Compatible con el stack aiquaa (caveman mode incluido).
  Usar cuando el usuario mencione "hurl", "pruebas declarativas", "archivo .hurl",
  "curl-like tests", o pida alternativa sin GUI a Postman/Newman.
  Auto-activa para cualquier flujo Hurl: autoría, ejecución, debug o CI.
---

Hurl run file. Claude write tests. Terse output. No fluff.

---

## ¿Qué es Hurl?

Hurl es un runner de HTTP en línea de comandos. Los tests se escriben en archivos `.hurl` —
texto plano legible por humanos y por LLMs. Sin GUI, sin JSON verboso, sin colecciones propietarias.
Cada archivo es una secuencia de requests HTTP con assertions integradas.

Diferencia clave frente a Postman/Newman:
- Postman → GUI-first, colección JSON, runner externo (Newman)
- Hurl → code-first, texto plano, runner nativo (`hurl` CLI o `hurlfmt`)
- Ambos son complementarios: Postman para exploración, Hurl para code review y CI declarativo

---

## Context Intake — SIEMPRE ejecutar primero

**Antes de generar cualquier archivo, recolectar contexto.** Sin excepciones.
El usuario puede dar nada, una URL, un curl, un contrato OpenAPI o código fuente.
Identificar qué falta y preguntar — una pregunta a la vez, en orden de prioridad.

---

### Paso 1 — Detectar qué ya dio el usuario

| Señal | Qué aporta |
|-------|-----------|
| URL completa (`https://api.ejemplo.com/v1/users`) | baseUrl + path del endpoint |
| Comando curl | método + url + headers + body (parcial o completo) |
| Archivo `.hurl` existente | requests existentes, pueden tener o no assertions |
| Archivo de variables (`vars.env`) | baseUrl, tokens, variables reutilizables |
| Spec OpenAPI / Swagger | contrato completo: endpoints, schemas, validaciones |
| DTO o validador del backend | reglas exactas de campos — clave para casos negativos |
| Resultados previos de `hurl --test` | fallos a corregir |
| "solo una URL" sin más contexto | casi nada — preguntar |

---

### Paso 2 — Preguntar lo que falta (una pregunta a la vez)

Trabajar en este orden de prioridad. Esperar respuesta antes de pasar a la siguiente.

#### Prioridad 1 — La URL (siempre obligatoria)

Si no hay URL base completa, preguntar:

> ¿Cuál es la URL base de la API? Ejemplo: `https://api.miempresa.com` o `http://localhost:8080`
>
> Si tenés un curl, pegalo directamente — lo proceso yo.

No continuar sin esto. Un path como `/users` sin host no es una URL.
Si el usuario da solo el path, pedir el host. Si da solo el host, pedir los paths.

#### Prioridad 2 — Los endpoints

Si hay URL base pero no endpoints:

> ¿Qué endpoints querés cubrir? Cualquiera de estos sirve:
>
> - Lista directa: `GET /users`, `POST /users`, `DELETE /users/{id}`
> - Un curl: `curl -X POST https://... -H "..." -d "..."`
> - Archivo OpenAPI/Swagger (JSON o YAML)
> - Código fuente de los endpoints (cualquier lenguaje)
>
> Si no sabés qué endpoints tiene la API, compartí la URL del Swagger si existe.

Si el usuario da un curl, extraer: método, URL completa, headers, body.
Confirmar lo extraído ("¿es correcto?") antes de continuar.

#### Prioridad 3 — El body (para POST / PUT / PATCH)

Si el método requiere body y no se tiene el schema:

> Para `<MÉTODO> <endpoint>` necesito la estructura del body. Podés dar:
>
> - JSON de ejemplo: `{ "name": "valor", "email": "valor" }`
> - Modelo o DTO del backend (C#, Java, TypeScript, Python, cualquier lenguaje)
> - Archivo de validaciones (FluentValidation, Zod, Joi, Pydantic, etc.)
>
> Sin esto no puedo saber qué campos son obligatorios ni qué validaciones cubrir.

Nunca inventar nombres de campos. Si el usuario dice "ya sabés el body" sin haberlo dado — pedir de nuevo.

#### Prioridad 4 — Autenticación

Si la API podría requerir auth y no se indicó que es pública:

> ¿La API requiere autenticación?
>
> - Sin auth (pública)
> - Bearer token → ¿tenés el token estático o hay un endpoint de login?
> - API Key → ¿en qué header va? ¿cómo se llama la key?
> - Basic Auth
> - Otro

Si Bearer con login: pedir URL del endpoint de login + campos (usuario/contraseña).
Se generará el request de login como primer entry en el archivo `.hurl` y se capturará el token con `[Captures]`.

Si Bearer estático: el token irá en el archivo de variables (`vars.env` / `vars-staging.env`).

#### Prioridad 5 — Archivo .hurl existente

Si el usuario pide agregar tests y podría haber un archivo previo:

> ¿Ya tenés un archivo `.hurl` para esta API? Compartilo si existe — lo expando sin pisar lo que ya tenés.
> Si no hay archivo, genero desde cero.

#### Prioridad 6 — Reglas de validación (para casos negativos)

Si el usuario pide casos negativos o validaciones de campos:

> Para casos negativos (campos vacíos, valores inválidos, límites de largo, enums fuera de rango)
> necesito las reglas de validación. Podés dar:
>
> - El archivo de validadores del backend
> - O manualmente: campos obligatorios, límites de largo, valores permitidos por campo
>
> Sin esto los casos negativos son aproximados — lo aviso si tengo que estimar.

#### Prioridad 7 — YML de Azure Pipelines existente

Solo cuando el usuario pide `/hurl:ci`:

> ¿Tenés un pipeline de Azure Pipelines existente que quieras usar como base?
> - Sí → compartilo — lo adapto para Hurl sin romper lo que ya tiene
> - No → genero desde cero con el template estándar

Si hay YML existente: leerlo, identificar jobs/steps actuales, inyectar el job de Hurl sin eliminar nada.
Confirmar qué se agrega y qué se preserva antes de escribir el archivo final.

#### Prioridad 8 — Metadata del informe (opcional)

Una vez confirmado el contexto base, preguntar opcionales para el reporte:

> Para el informe de resultados, ¿tenés esta info? (todo opcional)
>
> - **Versión de la API** — ejemplo: `v1.2.0` o link del release
> - **Link del repositorio** — ejemplo: `https://dev.azure.com/org/repo`
>
> Si los tenés, los incluyo en el encabezado del reporte. Si no, no pasa nada.

---

### Paso 3 — Confirmar antes de generar

Una vez con suficiente contexto, confirmar en este formato:

```
CONTEXTO DETECTADO:
  API:          <nombre o descripción>
  BASE URL:     <url completa>
  ENDPOINTS:    <lista de MÉTODO /path>
  AUTH:         <tipo o "ninguna">
  BODY:         <schema conocido o "no proporcionado">
  VALIDACIONES: <fuente o "no proporcionadas — casos negativos serán aproximados">
  ARCHIVO:      <nombre.hurl existente o "nuevo desde cero">
  VERSIÓN API:  <versión o "no proporcionada">
  REPO:         <url o "no proporcionado">
  SALIDA:       H_<NOMBRE>.hurl + V_<NOMBRE>.env [+ Y_<NOMBRE>_hurl.yml si aplica]

¿Confirmás o corregís algo antes de que genere?
```

Esperar confirmación. Luego generar.

---

### Escalation rules

- Usuario da "quiero testear mi API" → preguntar Prioridad 1
- Usuario da curl sin body para POST → preguntar Prioridad 3
- Usuario pega URL y dice "generá los tests" → preguntar Prioridades 2, 3, 4 en secuencia
- Usuario da código fuente en lenguaje desconocido → leer, extraer lo que se pueda, confirmar antes de generar
- Usuario da URL de Swagger → fetchear, extraer endpoints y schemas, confirmar antes de generar
- Usuario dice "arreglá el test roto" sin error → pedir output de `hurl --test` o el mensaje exacto de error
- Usuario dice "ya te dije todo" con contexto incompleto → listar exactamente qué falta, de a uno

---

## Convención de nombres de archivos

**Siempre respetar este patrón. Sin excepciones.**

| Tipo | Patrón | Ejemplo |
|------|--------|---------|
| Test file | `H_NOMBRE_DE_API.hurl` | `H_MYTHS_API.hurl` |
| Variables local | `V_NOMBRE_DE_API.env` | `V_MYTHS_API.env` |
| Variables staging | `V_NOMBRE_DE_API_STAGING.env` | `V_MYTHS_API_STAGING.env` |
| Pipeline Azure | `Y_NOMBRE_DE_API_hurl.yml` | `Y_MYTHS_API_hurl.yml` |
| Informe texto | `INFORME_HURL_NOMBRE_DE_API.txt` | `INFORME_HURL_MYTHS_API.txt` |

Reglas:
- `NOMBRE_DE_API` = UPPER_SNAKE_CASE
- Mismo nombre base en todos los archivos del mismo set — nunca divergir
- El sufijo `_hurl` en el YML distingue del pipeline de Newman si coexisten en el mismo repo

Estructura recomendada:
```
tests/
  hurl/
    H_MI_API.hurl
    V_MI_API.env
    V_MI_API_STAGING.env
azure-pipelines/
    Y_MI_API_hurl.yml
results/
    INFORME_HURL_MI_API.txt
```

---

## Stack

- Runner: `hurl` CLI (Rust, binario nativo — sin dependencias Node/Java)
- Formato de tests: Hurl DSL (`.hurl`)
- Variables: archivos `.env` clave=valor
- Reporters: `--test` (CLI), `--output` (response body), `--report-tap` (TAP), `--report-junit` (JUnit XML)
- CI target: Azure Pipelines (`Y_*_hurl.yml`)
- Instalación en CI: binario estático desde GitHub Releases o `apt` en Ubuntu runners

---

## Comandos

| Trigger | Acción |
|---------|--------|
| `/hurl:generate` | Generar archivo `.hurl` desde spec / source / curl / URL |
| `/hurl:add-test` | Agregar assertions a un entry existente en `.hurl` |
| `/hurl:fix` | Analizar y reparar un entry fallido |
| `/hurl:ci` | Generar `Y_NOMBRE_hurl.yml` para Azure Pipelines |
| `/hurl:env` | Crear o actualizar archivo de variables `.env` |
| `/hurl:run` | Mostrar el comando `hurl` correcto y reportar resultados dados |

---

## Formato de un archivo .hurl

Hurl es una secuencia de **entries**. Cada entry = 1 request HTTP + assertions opcionales.

### Estructura básica

```hurl
# Comentario — nombre del test o descripción
GET {{baseUrl}}/health
HTTP 200
```

### Entry completo con assertions

```hurl
# Health check
GET {{baseUrl}}/health
HTTP 200
[Asserts]
response_time < 500
header "Content-Type" contains "application/json"
jsonpath "$.status" == "ok"
```

### POST con body JSON

```hurl
# Crear recurso
POST {{baseUrl}}/resources
Content-Type: application/json
{
  "name": "Ejemplo",
  "description": "Recurso de prueba"
}
HTTP 201
[Captures]
resource_id: jsonpath "$.id"
[Asserts]
jsonpath "$.id" isString
jsonpath "$.name" == "Ejemplo"
```

### Reutilizar variable capturada

```hurl
# Obtener recurso creado
GET {{baseUrl}}/resources/{{resource_id}}
HTTP 200
[Asserts]
jsonpath "$.name" == "Ejemplo"

# Eliminar recurso
DELETE {{baseUrl}}/resources/{{resource_id}}
HTTP 204
```

### Bearer token desde login

```hurl
# Login — capturar token
POST {{baseUrl}}/auth/login
Content-Type: application/json
{
  "username": "{{username}}",
  "password": "{{password}}"
}
HTTP 200
[Captures]
token: jsonpath "$.access_token"

# Endpoint protegido
GET {{baseUrl}}/me
Authorization: Bearer {{token}}
HTTP 200
[Asserts]
jsonpath "$.email" isString
```

### Bearer token estático (desde variable)

```hurl
GET {{baseUrl}}/me
Authorization: Bearer {{token}}
HTTP 200
```

### Caso negativo — validación de campos

```hurl
# Body vacío → 400
POST {{baseUrl}}/resources
Content-Type: application/json
{}
HTTP 400
[Asserts]
jsonpath "$.errors" isCollection
```

### API Key en header

```hurl
GET {{baseUrl}}/data
X-Api-Key: {{api_key}}
HTTP 200
```

---

## Archivo de variables (.env)

Formato clave=valor, un par por línea. Sin comillas. Sin espacios alrededor del `=`.

```env
baseUrl=http://localhost:8080
token=
username=testuser
password=testpass
resource_id=
api_key=
```

Para staging:
```env
baseUrl=https://staging.miempresa.com
token=
username=testuser_stg
password=testpass_stg
resource_id=
api_key=
```

---

## Assertions de Hurl — referencia rápida

| Assertion | Ejemplo |
|-----------|---------|
| Status code | `HTTP 200` |
| Header presente | `header "Content-Type" exists` |
| Header valor | `header "Content-Type" == "application/json"` |
| Header contiene | `header "Content-Type" contains "json"` |
| JSONPath igualdad | `jsonpath "$.id" == "abc123"` |
| JSONPath tipo | `jsonpath "$.id" isString` |
| JSONPath colección | `jsonpath "$.items" isCollection` |
| JSONPath no nulo | `jsonpath "$.name" isString` |
| JSONPath entero | `jsonpath "$.count" isInteger` |
| JSONPath existe | `jsonpath "$.error" exists` |
| JSONPath no existe | `jsonpath "$.error" not exists` |
| Tiempo de respuesta | `response_time < 500` |
| Body contiene texto | `body contains "ok"` |
| Body regex | `body matches /^[0-9a-f-]{36}$/` |
| XPath (HTML/XML) | `xpath "//title" == "Mi API"` |

---

## Hurl CLI — referencia rápida

```bash
# Instalar (Ubuntu/Debian — para CI y local)
apt-get install -y hurl

# O desde binario estático (sin apt)
curl -LO https://github.com/Orange-OpenSource/hurl/releases/latest/download/hurl-x86_64-unknown-linux-gnu.tar.gz
tar xzf hurl-*.tar.gz
mv hurl /usr/local/bin/

# Run básico con variables
hurl --variables-file tests/hurl/V_MI_API.env tests/hurl/H_MI_API.hurl

# Modo test (exit code 1 si hay fallos — para CI)
hurl --test --variables-file tests/hurl/V_MI_API.env tests/hurl/H_MI_API.hurl

# Con reporte JUnit XML (para Azure Test Results)
hurl --test \
  --variables-file tests/hurl/V_MI_API.env \
  --report-junit results/hurl-results.xml \
  tests/hurl/H_MI_API.hurl

# Con reporte TAP
hurl --test \
  --variables-file tests/hurl/V_MI_API.env \
  --report-tap results/hurl-results.tap \
  tests/hurl/H_MI_API.hurl

# Continuar aunque haya fallos (no --fail-at-end en versiones antiguas)
hurl --test --variables-file V_MI_API.env H_MI_API.hurl || true

# Ver response body en stdout
hurl --variables-file V_MI_API.env H_MI_API.hurl --output -

# Verbose para debug
hurl --very-verbose --variables-file V_MI_API.env H_MI_API.hurl
```

---

## Pipeline Azure Pipelines — template estándar

### `Y_NOMBRE_DE_API_hurl.yml`

```yaml
# Y_MI_API_hurl.yml
# Hurl API tests — MI API
# Generado por skill hurl · aiquaa.com

trigger:
  branches:
    include:
      - main
      - develop

pool:
  vmImage: ubuntu-latest

variables:
  hurlVersion: 'latest'
  varFile: 'tests/hurl/V_MI_API.env'
  hurl File: 'tests/hurl/H_MI_API.hurl'
  resultsDir: '$(Build.ArtifactStagingDirectory)/hurl-results'

steps:

  - script: |
      echo "== Instalando Hurl =="
      curl -LO https://github.com/Orange-OpenSource/hurl/releases/latest/download/hurl-x86_64-unknown-linux-gnu.tar.gz
      tar xzf hurl-x86_64-unknown-linux-gnu.tar.gz
      sudo mv hurl /usr/local/bin/hurl
      hurl --version
    displayName: Instalar Hurl

  - script: mkdir -p $(resultsDir)
    displayName: Crear directorio de resultados

  - script: |
      hurl --test \
        --variables-file $(varFile) \
        --report-junit $(resultsDir)/hurl-junit.xml \
        $(hurlFile)
    displayName: Ejecutar tests Hurl
    continueOnError: true
    env:
      # Variables sensibles desde Azure Pipeline secrets
      # Agregar en Pipeline > Variables como secretos y mapear aquí:
      # HURL_token: $(token)
      # Hurl lee variables de entorno con prefijo HURL_<NOMBRE>
      HURL_token: $(token)

  - task: PublishTestResults@2
    condition: always()
    inputs:
      testResultsFormat: JUnit
      testResultsFiles: '$(resultsDir)/hurl-junit.xml'
      testRunTitle: 'Hurl — MI API'
      failTaskOnFailedTests: true
    displayName: Publicar resultados en Azure Test Plans

  - task: PublishBuildArtifacts@1
    condition: always()
    inputs:
      pathToPublish: $(resultsDir)
      artifactName: hurl-results
    displayName: Subir artefactos

```

### Notas del pipeline

**Variables sensibles:** Hurl lee variables de entorno con el prefijo `HURL_`. Si en el archivo `.env` local tenés `token=`, en el pipeline se mapea como `HURL_token: $(token)` donde `$(token)` es un secret en Azure Pipelines. No hardcodear credenciales en el YML.

**PublishTestResults:** Usa el reporte JUnit (`--report-junit`) para integrar con Azure Test Plans. Los resultados aparecen en la pestaña "Tests" del pipeline run y se puede hacer tracking histórico de pass/fail por test.

**continueOnError: true** en el step de ejecución + **failTaskOnFailedTests: true** en PublishTestResults garantiza que los resultados se publiquen aunque el step de Hurl falle, y el pipeline sigue marcando rojo correctamente.

**Coexistencia con pipeline de Newman:** Si el repo ya tiene `Y_MI_API.yml` (Newman), el archivo de Hurl va en `Y_MI_API_hurl.yml`. Son pipelines separados o se pueden unir como stages dentro de un mismo YML multi-stage.

---

## Formato de salida — run result (`/hurl:run`)

```
FILE: H_<NOMBRE>.hurl
VARS: V_<NOMBRE>.env
RESULT: ✅ PASS <n> | ❌ FAIL <n>
DURATION: <ms>ms

FAILURES (si hay):
  ❌ Entry <n> — <MÉTODO> <url>
     ASSERT: <tipo de assertion>
     GOT: <valor actual>
     EXPECTED: <valor esperado>
     FIX: <acción en una línea>
```

## Formato de salida — autoría (`/hurl:add-test`)

```
ENTRY: <MÉTODO> <url>
ADDED:
  ✅ HTTP <status>
  ✅ jsonpath "$.id" isString
  ✅ response_time < 500
HURL:
  <bloque entry — solo el nuevo código>
```

## Formato de salida — análisis de fallo (`/hurl:fix`)

```
ENTRY: <MÉTODO> <url>
STATUS: 🔴 ROTO | 🟡 FLAKY | 🔵 DESACTUALIZADO
ASSERT FALLIDA: <assertion exacta>
CAUSA: <una línea>
FIX: <parche o acción>
CONFIANZA: ALTA | MEDIA | BAJA
```

---

## Fallos comunes y fixes

| Síntoma | Causa | Fix |
|---------|-------|-----|
| `Assert failed: HTTP 200` con `HTTP 404` | URL incorrecta o variable vacía | Verificar `baseUrl` en vars file, probar con `--very-verbose` |
| `Variable not found: token` | Var no definida en `.env` ni en entorno | Agregar `token=` en `.env` o exportar `HURL_token=valor` |
| `jsonpath "$.id" failed` | Campo no existe en response body | Hacer `hurl --output - ...` para ver el body real |
| Fallo en CI, pasa local | Secret no mapeado en pipeline | Verificar `env: HURL_<VAR>: $(secret)` en el step |
| `SSL certificate verify failed` | HTTPS local sin cert válido | Agregar `--insecure` al comando (solo non-prod) |
| Todos los entries fallan en CI | Servicio no levantado antes del step | Agregar step de health check o `waitForService` antes |
| JUnit XML vacío | `--report-junit` path incorrecto | Verificar que el directorio de resultados exista antes de correr |
| `command not found: hurl` | Instalación fallida en CI | Verificar logs del step de instalación, revisar arquitectura del runner |

---

## Diferencias clave frente a Postman/Newman

| Aspecto | Postman / Newman | Hurl |
|---------|-----------------|------|
| Formato | JSON (colección propietaria) | Texto plano (`.hurl`) |
| GUI | Necesaria para crear | No existe — solo editor de texto |
| Diff en git | Difícil (JSON anidado) | Trivial (texto plano) |
| Variables | Environment JSON | Archivo `.env` clave=valor |
| Capturas de variables | `pm.environment.set()` en JS | `[Captures]` declarativo |
| Assertions | `pm.test()` en JS | `[Asserts]` declarativo |
| Scripting arbitrario | Sí (JavaScript completo) | No — solo lo que soporta Hurl DSL |
| Instalación en CI | `npm install -g newman` | Binario estático — sin runtime |
| Legibilidad por LLMs | Baja (JSON largo) | Alta (texto estructurado) |
| Reporte nativo CI | JSON + htmlextra (plugin) | JUnit XML nativo → Azure Test Plans |

**Cuándo usar Hurl sobre Postman/Newman:**
- El equipo prefiere code review sobre GUI
- Los tests viajan con el código fuente y se revisan en PRs
- Se quiere integración nativa con Azure Test Plans (JUnit XML)
- El runner de CI no tiene Node.js disponible o se prefiere binario sin dependencias

**Cuándo mantener Postman/Newman:**
- El equipo usa la GUI de Postman para exploración
- Hay colecciones existentes con scripts JavaScript complejos
- Se necesitan reporters htmlextra para stakeholders

---

## Auto-Clarity

Salir de caveman para: hallazgos de seguridad (auth bypass, token leak), cambios breaking en schema que afecten múltiples consumidores, confirmaciones de acciones irreversibles. Retomar caveman después.

## Boundaries

Escribe archivos `.hurl`, variables `.env`, comandos CLI, pipelines Azure Pipelines.
NO ejecuta Hurl — da los comandos listos para ejecutar.
NO inventa nombres de campos, reglas de validación ni valores de enum — pregunta si no los tiene.
"stop hurl" o "normal mode": volver a estilo verbose.
