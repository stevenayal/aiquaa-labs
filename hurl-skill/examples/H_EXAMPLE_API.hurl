# Health check
GET {{baseUrl}}/health
HTTP 200
[Asserts]
response_time < 500
header "Content-Type" contains "application/json"
jsonpath "$.status" == "ok"


# GET /resources — listar recursos
GET {{baseUrl}}/resources
HTTP 200
[Asserts]
jsonpath "$" isCollection
response_time < 500


# POST /resources — crear recurso
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
response_time < 500


# GET /resources/:id — obtener recurso creado
GET {{baseUrl}}/resources/{{resource_id}}
HTTP 200
[Asserts]
jsonpath "$.id" == {{resource_id}}
jsonpath "$.name" == "Ejemplo"


# DELETE /resources/:id — eliminar recurso
DELETE {{baseUrl}}/resources/{{resource_id}}
HTTP 204


# POST /resources — body vacío → 400
POST {{baseUrl}}/resources
Content-Type: application/json
{}
HTTP 400
[Asserts]
jsonpath "$.errors" isCollection
