# Ejemplo — diff de PR con validación superficial

Simula la salida combinada de `az devops invoke --area git --resource
pullrequestiterationchanges` + `az devops invoke --area git --resource items` para el PR #8802
("Automatiza TC-4103 actualizar limite tarjeta"), aplicando la heurística de
`validation-depth-heuristics.md`.

## Archivos cambiados (PR #8802)

```
H_ActualizarLimite.hurl   (nuevo)
```

## Contenido de `H_ActualizarLimite.hurl`

```hurl
PUT {{base_url}}/api/v1/tarjetas/{{tarjeta_id}}/limite
x-api-key: {{api_key}}
Content-Type: application/json
{
  "nuevoLimite": 5000
}

HTTP 200
```

## Clasificación aplicada

- **Paso 1 (ubicar archivo):** matchea prefijo `H_*.hurl` → skill de origen `hurl-skill`.
- **Paso 2 (grep de señal):** hay una línea `HTTP 200` esperada y **no hay bloque `[Asserts]`**
  en el entry — no se verifica ningún campo del body ni se encadena una verificación en base de
  datos (`POST /api/v1/sql/select`) para confirmar que el límite realmente cambió.
- **Paso 3 (clasificación final):** **Superficial** — cuenta como "automatizado" en la métrica 1
  (Azure DevOps lo marca `Automated`), pero **no** cuenta como automatización de calidad. Se
  reporta en el informe bajo "Casos superficiales" de Carlos Ruiz.

## Qué haría que este mismo caso clasificara como Profunda

```hurl
PUT {{base_url}}/api/v1/tarjetas/{{tarjeta_id}}/limite
x-api-key: {{api_key}}
Content-Type: application/json
{
  "nuevoLimite": 5000
}

HTTP 200
[Asserts]
jsonpath "$.limite" == 5000

POST {{base_url}}/api/v1/sql/select
x-api-key: {{api_key}}
Content-Type: application/json
{
  "query": "SELECT limite FROM tarjetas WHERE id = {{tarjeta_id}}"
}

HTTP 200
[Asserts]
jsonpath "$.rows[0].limite" == 5000
```
