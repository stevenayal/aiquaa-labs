# Guía de uso — hurl-skill

## Instalación

```bash
npx skills add aiquaa-labs/hurl-skill
```

Para agentes específicos:

```bash
npx skills add aiquaa-labs/hurl-skill -a cursor
npx skills add aiquaa-labs/hurl-skill -a windsurf
npx skills add aiquaa-labs/hurl-skill -a cline
```

---

## Instalar Hurl localmente

```bash
# Windows (winget)
winget install Hurl.Hurl

# macOS (brew)
brew install hurl

# Ubuntu/Debian
apt-get install -y hurl

# Binario estático (cualquier plataforma)
curl -LO https://github.com/Orange-OpenSource/hurl/releases/latest/download/hurl-x86_64-unknown-linux-gnu.tar.gz
tar xzf hurl-*.tar.gz
sudo mv hurl /usr/local/bin/
hurl --version
```

---

## Comandos disponibles

| Comando | Qué hace |
|---------|----------|
| `/hurl:generate` | Genera `.hurl` desde spec, curl, código fuente o URL |
| `/hurl:add-test` | Agrega assertions a un entry existente |
| `/hurl:fix` | Analiza y repara un entry fallido |
| `/hurl:ci` | Genera pipeline Azure Pipelines |
| `/hurl:env` | Crea o actualiza archivo de variables `.env` |
| `/hurl:run` | Muestra el comando `hurl` correcto y reporta resultados |

La skill siempre pregunta antes de generar. En orden de prioridad:
1. URL base de la API
2. Endpoints y métodos
3. Body (para POST/PUT/PATCH)
4. Autenticación
5. Archivo `.hurl` existente
6. Reglas de validación (para casos negativos)
7. YML existente a modificar (solo para `/hurl:ci`)
8. Versión y repo (para el informe — opcionales)

---

## Uso rápido

### Generar desde cero

```
/hurl:generate
```

La skill te va a preguntar la URL base, los endpoints y el tipo de auth.

### Generar desde un curl

```
/hurl:generate
curl -X POST https://api.miempresa.com/users \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Juan", "email": "juan@ejemplo.com"}'
```

### Agregar tests a un entry existente

```
/hurl:add-test
[pegá el entry .hurl acá]
```

### Correr la colección localmente

```bash
hurl --test \
  --variables-file tests/hurl/V_MI_API.env \
  tests/hurl/H_MI_API.hurl
```

### Correr con reporte JUnit (para Azure)

```bash
hurl --test \
  --variables-file tests/hurl/V_MI_API.env \
  --report-junit results/hurl-junit.xml \
  tests/hurl/H_MI_API.hurl
```

---

## Estructura recomendada de archivos

```
tests/
  hurl/
    H_MI_API.hurl              ← tests
    V_MI_API.env               ← variables local
    V_MI_API_STAGING.env       ← variables staging
azure-pipelines/
    Y_MI_API_hurl.yml          ← pipeline Azure
results/
    hurl-junit.xml             ← generado por hurl --report-junit
```

---

## Por qué JUnit XML para Azure Pipelines

Azure DevOps solo publica resultados en la pestaña **Tests** si el reporte está en formato JUnit XML.
Los reportes `json` y `htmlextra` de Newman **no** activan esa pestaña — son formatos propietarios.

Hurl genera JUnit XML nativo con `--report-junit`. Sin plugins, sin configuración extra.

El pipeline mínimo que hace aparecer los resultados:

```yaml
- script: |
    hurl --test \
      --variables-file tests/hurl/V_MI_API.env \
      --report-junit $(Build.ArtifactStagingDirectory)/hurl-junit.xml \
      tests/hurl/H_MI_API.hurl
  displayName: Ejecutar tests Hurl
  continueOnError: true

- task: PublishTestResults@2
  condition: always()
  inputs:
    testResultsFormat: JUnit
    testResultsFiles: '$(Build.ArtifactStagingDirectory)/hurl-junit.xml'
    testRunTitle: 'Hurl — MI API'
    failTaskOnFailedTests: true
  displayName: Publicar en Azure Test Plans
```

Dos claves:
- `continueOnError: true` en el step de ejecución → publica resultados aunque haya fallos
- `failTaskOnFailedTests: true` en PublishTestResults → el pipeline sigue marcando rojo si hay tests fallidos

---

## Variables sensibles en Azure Pipelines

Hurl lee variables de entorno con el prefijo `HURL_`. Si en el archivo `.env` local tenés `token=`,
en el pipeline se mapea así:

```yaml
- script: |
    hurl --test \
      --variables-file $(varFile) \
      --report-junit $(resultsDir)/hurl-junit.xml \
      $(hurlFile)
  displayName: Ejecutar tests Hurl
  continueOnError: true
  env:
    HURL_token: $(token)        # $(token) es un secret en Pipeline > Variables
    HURL_api_key: $(apiKey)     # agregar tantos como necesites
```

Los secrets de Azure nunca van en el YML — solo la referencia `$(nombre_secret)`.

---

## Convención de archivos

```
H_MI_API.hurl              ← colección de tests
V_MI_API.env               ← variables local
V_MI_API_STAGING.env       ← variables staging
Y_MI_API_hurl.yml          ← Azure Pipelines
```

Mismo `MI_API` en todos — nunca divergir.

---

## Créditos

Creado por [aiquaa](https://aiquaa.com/) — *Saber es calidad*

Compatible con [postman-newman-skill](https://github.com/aiquaa-labs/postman-newman-skill).
