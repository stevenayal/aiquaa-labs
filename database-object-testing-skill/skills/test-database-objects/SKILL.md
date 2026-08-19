---
name: test-database-objects
description: Diseñar, generar, ejecutar y diagnosticar pruebas automatizadas de objetos de bases de datos relacionales a través de una API REST, sin conexión directa ni drivers del motor. Usar cuando Codex deba probar SQL, vistas, funciones, procedimientos, paquetes o triggers; comparar ambientes base y candidato; evaluar planes o costos; aplicar reglas y buenas prácticas almacenadas en Markdown; generar suites JSON; o analizar los reportes del runner db-object-test.
---

# Probar objetos de base de datos

Usar el runner Node.js `database-object-testing-skill/src/cli.mjs`. No conectarse directamente a la base de datos. No solicitar ni guardar credenciales: usar variables de entorno para URL y token.

## Flujo

1. Identificar el objeto, su tipo, comportamiento esperado, datos controlados y efectos laterales.
2. Confirmar el contrato de la API. Leer [api-contract.md](references/api-contract.md) al integrar o adaptar endpoints.
3. Cargar todos los `.md` del directorio de reglas indicado por el usuario. Si no indica uno, usar `database-object-testing-skill/rules/`. Leer [rule-authoring.md](references/rule-authoring.md) al crear o cambiar reglas.
4. Crear o actualizar una suite JSON. Leer [suite-format.md](references/suite-format.md) para campos y operadores.
5. Diseñar como mínimo:
   - camino feliz;
   - entradas nulas, límites y datos inexistentes;
   - errores de negocio y de permisos cuando sean comprobables;
   - efectos de escritura y atomicidad usando `transactionMode: "rollback"`;
   - comparación funcional base/candidato;
   - comparación de costo cuando la API implemente `explain`.
6. Ejecutar desde `database-object-testing-skill/`:

```bash
node src/cli.mjs validate-rules --rules rules
node src/cli.mjs run --suite examples/S_EXAMPLE.json --rules rules --output results
```

7. Informar el veredicto, diferencias funcionales, regresiones de costo, reglas incumplidas y evidencia. No presentar una estimación de costo como medición real si la API no devolvió métricas.

## Criterios de diseño

- Preferir binds y datos deterministas.
- Comparar únicamente rutas estables; excluir timestamps, IDs generados y métricas volátiles.
- Tratar cambios de filas o parámetros de salida como regresión salvo que la suite los declare intencionales.
- Definir umbrales de costo explícitos por métrica. No inventar un umbral corporativo.
- Marcar `severity: "error"` para reglas que bloquean; las advertencias no hacen fallar la suite.
- Ejecutar escrituras en un ambiente de prueba y con rollback. Requerir autorización explícita antes de usar producción o `transactionMode: "commit"`.
- Ocultar tokens, credenciales, binds sensibles y respuestas con datos personales en informes compartidos.

## Adaptación a Oracle vía API

Mantener el runner agnóstico. Traducir en el gateway REST las operaciones hacia Oracle y normalizar la respuesta al contrato de la skill. Para procedimientos o paquetes, retornar parámetros OUT en `data.out`; para cursores, usar `data.rows`; para costos, mapear el plan a `cost`, `cardinality`, `bytes`, `logicalReads` o métricas equivalentes.

Si la API corporativa no coincide con el contrato, modificar solo el cliente/adaptador del runner y conservar las suites.

## Límites

- No ejecutar DDL o DML destructivo fuera de un ambiente aislado.
- No afirmar equivalencia si falta el ambiente base.
- No evaluar costos mediante tiempo de red únicamente.
- No exponer SQL o código fuente sensible fuera del reporte local.
